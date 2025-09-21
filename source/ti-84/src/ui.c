//
// Created by literal-gargoyle on 9/20/2025.
//
// UI for the TI-84 CE (CEDEV / CE TOOLCHAIN)
// - main menu

#include <tice.h>
#include <graphx.h>
#include <keypadc.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdint.h>

int initSMSMenu(void);
int initEMAILMenu(void);

static void waitKeyRelease(void) {
    do { kb_Scan(); } while (kb_Data[1] | kb_Data[2] | kb_Data[3] | kb_Data[4] | kb_Data[5] | kb_Data[6] | kb_Data[7]);
}

void main(void)
{
    int menuSelection = 0;
    gfx_Begin();
    gfx_SetDrawScreen();
    gfx_FillScreen(255);

    while (true)
    {
        gfx_FillScreen(255);
        gfx_SetTextFGColor(0);
        gfx_SetTextXY(10, 10);
        gfx_PrintString("TI-0 - FRONTUSERINT - main.c");

        if (menuSelection == 0) gfx_SetTextBGColor(224); else gfx_SetTextBGColor(255);
        gfx_SetTextXY(10, 30);
        gfx_PrintString("> SMS");

        if (menuSelection == 1) gfx_SetTextBGColor(224); else gfx_SetTextBGColor(255);
        gfx_SetTextXY(10, 50);
        gfx_PrintString("> EMAIL");

        gfx_SetTextBGColor(255);
        gfx_SwapDraw();
        kb_Scan();

        if (kb_Data[7] & kb_Down) { if (menuSelection < 1) menuSelection++; waitKeyRelease(); }
        if (kb_Data[7] & kb_Up) { if (menuSelection > 0) menuSelection--; waitKeyRelease(); }

        if (kb_Data[6] & kb_Enter)
        {
            if (menuSelection == 0) initSMSMenu();
            if (menuSelection == 1) initEMAILMenu();
            waitKeyRelease();
        }

        if (kb_Data[1] & kb_Clear) break;
    }
    gfx_End();
}

int initSMSMenu(void)
{
    int selection = 0;
    while (true)
    {
        gfx_FillScreen(255);
        gfx_SetTextFGColor(0);
        gfx_SetTextXY(10, 10);
        gfx_PrintString("SMS MENU");

        if (selection == 0) gfx_SetTextBGColor(224); else gfx_SetTextBGColor(255);
        gfx_SetTextXY(10, 30);
        gfx_PrintString("> View Messages");

        if (selection == 1) gfx_SetTextBGColor(224); else gfx_SetTextBGColor(255);
        gfx_SetTextXY(10, 50);
        gfx_PrintString("> Back");

        gfx_SetTextBGColor(255);
        gfx_SwapDraw();
        kb_Scan();

        if (kb_Data[7] & kb_Down) { if (selection < 1) selection++; waitKeyRelease(); }
        if (kb_Data[7] & kb_Up) { if (selection > 0) selection--; waitKeyRelease(); }

        if (kb_Data[6] & kb_Enter)
        {
            if (selection == 0)
            {
                gfx_FillScreen(255);
                gfx_SetTextXY(10, 10);
                gfx_PrintString("No messages.");
                gfx_SwapDraw();
                waitKeyRelease();
                while (!(kb_Data[6] & kb_Enter)) { kb_Scan(); }
                waitKeyRelease();
            }
            if (selection == 1) { waitKeyRelease(); return 0; }
        }

        if (kb_Data[1] & kb_Clear) return 0;
    }
}

int initEMAILMenu(void)
{
    int selection = 0;
    while (true)
    {
        gfx_FillScreen(255);
        gfx_SetTextFGColor(0);
        gfx_SetTextXY(10, 10);
        gfx_PrintString("EMAIL MENU");

        if (selection == 0) gfx_SetTextBGColor(224); else gfx_SetTextBGColor(255);
        gfx_SetTextXY(10, 30);
        gfx_PrintString("> Inbox");

        if (selection == 1) gfx_SetTextBGColor(224); else gfx_SetTextBGColor(255);
        gfx_SetTextXY(10, 50);
        gfx_PrintString("> Back");

        gfx_SetTextBGColor(255);
        gfx_SwapDraw();
        kb_Scan();

        if (kb_Data[7] & kb_Down) { if (selection < 1) selection++; waitKeyRelease(); }
        if (kb_Data[7] & kb_Up) { if (selection > 0) selection--; waitKeyRelease(); }

        if (kb_Data[6] & kb_Enter)
        {
            if (selection == 0)
            {
                gfx_FillScreen(255);
                gfx_SetTextXY(10, 10);
                gfx_PrintString("No emails.");
                gfx_SwapDraw();
                waitKeyRelease();
                while (!(kb_Data[6] & kb_Enter)) { kb_Scan(); }
                waitKeyRelease();
            }
            if (selection == 1) { waitKeyRelease(); return 0; }
        }

        if (kb_Data[1] & kb_Clear) return 0;
    }
}
