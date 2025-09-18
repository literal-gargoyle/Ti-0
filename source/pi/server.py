#!/usr/bin/env python3
"""
Minimal Pi-side phone controller skeleton:
- Uses pyserial to talk to an AT-capable modem
- Provides send_at() and a read loop that parses basic responses
- Handles incoming SMS and simple call status events (expand as needed)
"""

#!! THIS IS A MINIMAL EXAMPLE, NOT PRODUCTION-READY CODE !!

import os
import sys
import time
import threading
import logging
import argparse
import queue
import signal
import json
import subprocess

# third-party
import serial  # pyserial
from dotenv import load_dotenv  # optional

# Optional imports you may enable if you use them:
# import requests      # for external APIs (email, webhooks)
# import RPi.GPIO as GPIO  # for power management or button input

# --- Configuration & logging -------------------------------------------------
load_dotenv(".env")  # optional .env support

DEFAULT_DEVICE = os.getenv("MODEM_DEVICE", "/dev/ttyUSB0")
DEFAULT_BAUD = int(os.getenv("MODEM_BAUD", "115200"))
READ_TIMEOUT = 0.5

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"),
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("ti0.pi")

# --- Low-level modem wrapper ------------------------------------------------
class Modem:
    def __init__(self, device=DEFAULT_DEVICE, baud=DEFAULT_BAUD, timeout=READ_TIMEOUT):
        self.device = device
        self.baud = baud
        self.timeout = timeout
        self.ser = None
        self._lock = threading.Lock()

    def open(self):
        logger.info("Opening serial device %s @ %d", self.device, self.baud)
        try:
            self.ser = serial.Serial(self.device, self.baud, timeout=self.timeout)
            # ensure CRLF behavior for many modems
            self.ser.write_timeout = 2
        except Exception as e:
            logger.exception("Failed to open serial device: %s", e)
            raise

    def close(self):
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except Exception:
                pass
        logger.info("Serial closed")

    def send_at(self, cmd, wait_for="OK", timeout=5.0):
        """Send an AT command and return list of reply lines (non-blocking read loop should also capture)."""
        raw = (cmd.strip() + "\r\n").encode("utf-8")
        with self._lock:
            logger.debug(">>> %s", cmd)
            self.ser.write(raw)
            self.ser.flush()

            # simple synchronous waiter for common replies
            deadline = time.time() + timeout
            lines = []
            while time.time() < deadline:
                line = self.ser.readline().decode(errors="ignore").strip()
                if not line:
                    continue
                logger.debug("<<< %s", line)
                lines.append(line)
                if wait_for and line.upper().startswith(wait_for):
                    break
            return lines

    def readline(self):
        """Non-blocking single-line read (for background reader)."""
        try:
            raw = self.ser.readline()
            if not raw:
                return ""
            return raw.decode(errors="ignore").strip()
        except Exception as e:
            logger.exception("Serial read error: %s", e)
            return ""

# --- High-level server ------------------------------------------------------
class PhoneServer:
    def __init__(self, modem: Modem):
        self.modem = modem
        self.running = False
        self.reader_thread = None
        self.msg_queue = queue.Queue()

    def start(self):
        self.modem.open()
        # basic modem init
        self.modem.send_at("AT")
        self.modem.send_at("ATE0")  # echo off
        self.modem.send_at("AT+CMGF=1")  # SMS text mode
        # configure for new SMS indications to be sent unsolicited (module-specific)
        # example: AT+CNMI=2,1,0,0,0
        try:
            self.modem.send_at("AT+CNMI=2,1,0,0,0")
        except Exception:
            logger.debug("CNMI not supported or error; continue")

        self.running = True
        self.reader_thread = threading.Thread(target=self._reader_loop, name="modem-reader", daemon=True)
        self.reader_thread.start()
        logger.info("PhoneServer started")

    def stop(self):
        logger.info("Stopping PhoneServer")
        self.running = False
        if self.reader_thread:
            self.reader_thread.join(timeout=2.0)
        self.modem.close()

    def _reader_loop(self):
        """Continuously read lines from the modem and dispatch events."""
        while self.running:
            try:
                line = self.modem.readline()
                if not line:
                    continue
                logger.debug("MODEM LINE: %s", line)
                self._handle_line(line)
            except Exception as e:
                logger.exception("Error in reader loop: %s", e)
                time.sleep(1)

    def _handle_line(self, line):
        """Parse unsolicited modem responses (very small example)."""
        # incoming SMS indication (module-dependent syntax)
        if line.startswith("+CMTI:"):
            # New SMS received — parse index then fetch it
            logger.info("New SMS indication: %s", line)
            # crude parsing
            parts = line.split(",")
            if len(parts) >= 2:
                index = parts[1]
                threading.Thread(target=self._fetch_sms, args=(index,), daemon=True).start()
            return

        # incoming call indicator example (module-specific; many modules emit RING)
        if "RING" in line or "+CLIP:" in line:
            logger.info("Incoming call / CLIP: %s", line)
            # forward to calculator or take action
            self.msg_queue.put({"type": "call", "raw": line})
            return

        # catch plain OK/ERROR etc
        if line in ("OK", "ERROR"):
            logger.debug("Modem status: %s", line)
            return

        # otherwise send to queue for higher-level handling
        self.msg_queue.put({"type": "raw", "raw": line})

    def _fetch_sms(self, index):
        """Read SMS message by index and delete it (example)."""
        try:
            lines = self.modem.send_at(f'AT+CMGR={index}', wait_for="OK", timeout=3.0)
            # lines now contain header + body — do more robust parsing here
            logger.info("Fetched SMS index %s -> %s", index, lines)
            # optionally forward to calculator
            self.msg_queue.put({"type": "sms", "index": index, "lines": lines})
            # remove SMS to avoid reprocessing (optional)
            self.modem.send_at(f'AT+CMGD={index}', wait_for="OK", timeout=3.0)
        except Exception as e:
            logger.exception("Failed to fetch SMS %s: %s", index, e)

    def send_sms(self, number: str, text: str):
        """Send SMS (text mode example)."""
        logger.info("Sending SMS to %s", number)
        with self.modem._lock:
            # start send
            self.modem.ser.write(f'AT+CMGS="{number}"\r\n'.encode())
            time.sleep(0.5)
            # modem expects message text then Ctrl+Z
            self.modem.ser.write(text.encode() + b"\x1A")
            # read until OK or ERROR
            return self.modem.send_at("", wait_for="OK", timeout=10.0)

# --- CLI / entrypoint -------------------------------------------------------
def main(argv=None):
    p = argparse.ArgumentParser(description="ti-0 Pi phone controller")
    p.add_argument("--device", "-d", default=DEFAULT_DEVICE, help="Serial device for the modem")
    p.add_argument("--baud", "-b", type=int, default=DEFAULT_BAUD, help="Serial baud rate")
    args = p.parse_args(argv)

    modem = Modem(device=args.device, baud=args.baud)
    server = PhoneServer(modem)

    def handle_sig(sig, frame):
        logger.info("Signal received, shutting down")
        server.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_sig)
    signal.signal(signal.SIGTERM, handle_sig)

    try:
        server.start()
        # main loop: process messages from server.msg_queue and forward to calculator or UI
        while True:
            try:
                msg = server.msg_queue.get(timeout=1.0)
            except queue.Empty:
                continue
            logger.info("Application message: %s", msg)
            # TODO: implement forwarding to calculator or other IPC
    except Exception:
        logger.exception("Fatal error")
    finally:
        server.stop()

if __name__ == "__main__":
    main()