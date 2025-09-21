# ti-0
![License](https://img.shields.io/github/license/literal-gargoyle/ti-0?style=for-the-badge)
![CI](https://img.shields.io/github/actions/workflow/status/literal-gargoyle/ti-0/WORKFLOW.yml?branch=main&style=for-the-badge)
![Last Commit](https://img.shields.io/github/last-commit/literal-gargoyle/ti-0?style=for-the-badge)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-Zero%202W-brightgreen?style=for-the-badge&logo=raspberry-pi)
![TI](https://img.shields.io/badge/TI-84%20CE-ff6f00?style=for-the-badge&logo=texas-instruments)
![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue?style=for-the-badge&logo=python)

## Overview

ti-0 is a hybrid physical and digital phone module project that turns a TI-84 CE calculator into a simple phone interface by pairing it with a Raspberry Pi Zero and a cellular (SIM) module. The Raspberry Pi handles cellular connectivity, call/SMS routing, and power management; the TI-84 CE provides a minimal user interface on the calculator's screen and keypad.

This repository contains the code, documentation, and assembly notes for both sides of the project (calculator-side code and Pi-side controller scripts).

## Features

- Make and receive calls using a SIM-equipped cellular modem attached to a Raspberry Pi Zero.
- Seperate battery, so the module can be a standalone phone through SSH
- Send and receive SMS messages.
- Minimal, calculator-native UI on a TI-84 CE for dialing, call status, and SMS viewing.
- Email client on the TI-84, sends through the pi zero.

## Hardware (recommended)

- TI-84 Plus CE (or compatible CE model)
- Raspberry Pi Zero 2w (Raspberry Pi Zero 2wh recommended, as it has presoldered headers)
- Waveshare GSM/GPRS HAT, or applicable sim800c module
- microSD card for the Pi OS (32-64gb)
- Pi zero UPS(A) HAT. (Make sure it connects underneath through pogo pins)
- Ti-Link cable (Mini USB -> Micro USB)
- Antenna for the cellular module (Most hats come with one)
- Throwaway (PrePaid) Sim card. I recommend one with about 5gb of data.

Note: Make sure you do not plug in **power** for the raspberry pi, while the battery is on, this will fry the Raspberry Pi Zero.

## Software stack

- Pi-side: Python 3 scripts (controller, serial handling, AT command interface to modem)
- Pi OS: Debian-based Raspberry Pi OS recommended
- Calculator-side: compact app/program that runs on the TI-84 CE, There is also 2 ASM scripts you need to install on the calulator.

## Quick start (Pi)

1. Flash Raspberry Pi OS (Lite is fine) to your microSD card.
2. Boot the Pi and enable SSH/serial as needed.
3. Install system dependencies and Python packages:

```bash
sudo apt update && sudo apt install -y python3 python3-pip git
git clone https://github.com/literal-gargoyle/ti-0/
cd ti-0
pip3 install -r requirements.txt
```

4. Wire the cellular modem and TI-84 CE as described in the hardware notes (calculator/ and docs/ subfolders). Ensure the SIM card is active and the modem has an antenna.

5. Start the Pi controller

```bash
python3 source/pi/server.py --device /dev/ttyS0
```

Modify the device path to match your serial device (for example /dev/ttyUSB0, /dev/ttyAMA0, or a USB-serial adapter path). This can change between calculators.

## Quick start (Calculator)

- !!**Make sure that your calculator is running OS version 5.4 or earlier. If you have a calculator with the latest, or a version newer than specified, you need to install [arTIFICE](https://yvantt.github.io/arTIfiCE/) on your calculator.**!!
- Build or copy the calculator-side program to your TI-84 CE using your preferred TI transfer tools (TI-Connect CE, Cervantes, or community toolchains). Typical file formats are `.8xp` or calculator-archive packages.
- !!**Make sure your calulator is fully charged during this process.**!!
- Start the program on the calculator and follow on-screen instructions to pair with the Pi (USB or serial). See `source/ti-84/README.md` for build and install specifics.

## Usage examples

- Dial from the TI: enter number, press Dial — the Pi will send AT commands to the modem and forward call status to the calculator.
- Send SMS from the calculator: compose a message and send — Pi relays it via the modem.
- Logs and debugging are available on the Pi (check `logs/` or stdout from `phone_server.py`).

Pi debug run:

```bash
python3 source/pi/server.py --device /dev/ttyUSB0 --log-level debug
```
*Adjust --device as necessary*

## Development

- Keep Pi code modular: separate serial/modem logic from high-level routing.
- Add tests for parsing AT responses and for message/call state machines where possible (unit-testable Python modules).
- If you add native TI code, document the toolchain and provide a small build script in `source/ti-84/scripts/`.

## Troubleshooting

- Serial permissions: add your user to the `dialout` group or run with sudo for testing.
- SIM module startup: some modules require a stable 4V supply or a capacitor to handle transmit current spikes — consult the module datasheet.
- Check antenna and carrier signal (AT+CSQ to get signal quality).

## Security & Legal

- This project directly interacts with cellular networks and user communications. Be mindful of local laws and carrier terms of service when making calls or sending messages.
- Do not expose the Pi controller to the public internet without proper authentication and TLS.

## Roadmap / Status

- Status: experimental / proof-of-concept, I'm currently working on making the hardware for this project, I will try to update as frewuently as possible.
- Planned: better UI on the calculator, auto-reconnect on signal loss, battery/power-management improvements, richer SMS threading. Encyption.

## Contributing

Contributions welcome. Please open issues for bugs or feature requests and send pull requests for changes.

## License

[CC BY-NA-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

## Authors / Contact

- Primary: @literal-gargoyle
- Contact: waltuhwhiteyo1234@gmail.com

