#!/usr/bin/python
# -*- coding: utf-8 -*-

import calendar
import locale
import logging
from typing import List
from MonthlyCalendar import CalendarStyle, ColorScheme, DateStyle, HolidayStyle, MoonStyle, calcHolidays, calcMoons, ScMonthCalendar

logging.basicConfig(filename="U:\\tmp\\scribus-calendar.log", level=logging.DEBUG)

try:
    from scribus import messageBox, ALIGN_CENTERED, ALIGN_LEFT, ALIGNV_BOTTOM, ALIGNV_TOP, ICON_CRITICAL
except ImportError as e:
    logging.error(e)
    print("This Python script is written for the Scribus \
      scripting interface.")
    print("It can only be run from within Scribus.")
    sys.exit(1)


# dzzzMonthColors = {}
# for m, data in dzzzMonthColors100.items():
#   dzzzMonthColors[m] = {}
#   for name, cmyk100 in data.items():
#     dzzzMonthColors[m][name] = (cmyk100[0]*2.55, cmyk100[1]*2.55, cmyk100[2]*2.55, cmyk100[3]*2.55)


dzzzMonthColors = {
    1: {'mainColor': (0, 28, 45, 45), 'lightColor': (0, 28, 45, 45)},
    2: {'mainColor': (0, 56, 10, 28), 'lightColor': (0, 22, 43, 12)},
    3: {'mainColor': (10, 0, 119, 109), 'lightColor': (22, 0, 38, 56)},
    4: {'mainColor': (45, 0, 145, 63), 'lightColor': (15, 0, 5, 30)},
    5: {'mainColor': (0, 7, 20, 56), 'lightColor': (0, 28, 5, 28)},
    6: {'mainColor': (114, 10, 0, 112), 'lightColor': (30, 5, 0, 56)},
    7: {'mainColor': (0, 73, 140, 20), 'lightColor': (0, 73, 140, 20)},
    8: {'mainColor': (109, 2, 0, 20), 'lightColor': (5, 12, 0, 10)},
    9: {'mainColor': (0, 79, 142, 89), 'lightColor': (0, 30, 58, 43)},
    10: {'mainColor': (0, 10, 48, 2), 'lightColor': (0, 10, 48, 2)},
    11: {'mainColor': (0, 0, 28, 84), 'lightColor': (0, 2, 0, 5)},
    12: {'mainColor': (0, 193, 188, 33), 'lightColor': (0, 71, 89, 15)}
}


def createCaledar(year: int, months: List[int]) -> None:
    firstDay = calendar.MONDAY
    weekNr = False
    weekNrHd="T"
    offsetX=123.59
    marginX=0.0
    offsetY=0.0
    marginY=90.71
    drawImg=False
    miniCals=False
    cFont="Futura PT Light"
    lang="Slovenian"

    locale.setlocale(locale.LC_CTYPE, lang)
    locale.setlocale(locale.LC_TIME, lang)

    holidaysFile = "U:\\home\\matej\\Projekti\\Scribus\\Monthly-calendar-script-for-Scribus\\holidays\\SI_holidays_DZZZKranj.txt"
    moonsFile = "U:\\home\\matej\\Projekti\\Scribus\\Monthly-calendar-script-for-Scribus\\moonphases.txt"
    utcdiff = 1

    hol = calcHolidays(year)
    holidaysList = hol.importHolidays(holidaysFile)

    moon = calcMoons(year, utcdiff)
    moonsList = moon.importMoons(moonsFile)

    dzzzDateStyle = DateStyle(
        textAlignment=ALIGN_LEFT,
        textVerticalAlignment=ALIGNV_BOTTOM,
        fontscale=0.30,
        marginScale=0.06
    )

    dzzzHolidayStyle = HolidayStyle(
        textAlignment=ALIGN_LEFT,
        textVerticalAlignment=ALIGNV_TOP,
        fontscale=0.15,
        enableFirstLineOffset=False
    )

    dzzzMoonStyle = MoonStyle(
        cFont="Cambria Math Regular",
        textAlignment=ALIGN_CENTERED,
        textVerticalAlignmentSmallCell=ALIGNV_BOTTOM,
        textVerticalAlignment=ALIGNV_BOTTOM
    )

    calendarStyle = CalendarStyle(
        fullRowCount=False,
        fillAllDays=True,
        headerDisplayYear=False,
        headerMonthUpperCase=False
    )

    colorScheme = ColorScheme.coloredWeekendsHolidaysHeader(dzzzMonthColors)
    colorScheme.colors["fillDayNames"] = ColorScheme.WHITE_CMYK
    colorScheme.colors["txtDayNames"] = colorScheme.colors["txtDate"]
    
    cal = ScMonthCalendar(
        year=year,
        months=months,
        firstDay=firstDay,
        weekNr=weekNr,
        weekNrHd=weekNrHd,
        offsetX=offsetX, marginX=marginX,
        offsetY=offsetY, marginY=marginY,
        drawImg=drawImg,
        miniCals=miniCals,
        cFont=cFont,
        lang=lang,
        holidaysList=holidaysList,
        moonsList=moonsList,
        promptNewDoc=False
    )
    cal.showProgress = False
    cal.dateStyle = dzzzDateStyle
    cal.holidayStyle = dzzzHolidayStyle
    cal.moonStyle = dzzzMoonStyle
    cal.calendarStyle = calendarStyle
    cal.colorScheme = colorScheme
    err = cal.createCalendar()
    if err != None:
        messageBox("Napaka", err, icon=ICON_CRITICAL)


def main():
    createCaledar(2023, [4, 6, 7])

if __name__ == '__main__':
    main()
