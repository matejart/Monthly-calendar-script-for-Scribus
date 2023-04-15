#!/usr/bin/python
# -*- coding: utf-8 -*-

import calendar
import locale
import logging
from typing import List
from MonthlyCalendar import CalendarStyle, DateStyle, HolidayStyle, MoonStyle, calcHolidays, calcMoons, ScMonthCalendar

logging.basicConfig(filename="U:\\tmp\\scribus-calendar.log", level=logging.DEBUG)

try:
    from scribus import messageBox, ALIGN_CENTERED, ALIGN_LEFT, ALIGNV_BOTTOM, ALIGNV_TOP, ICON_CRITICAL
except ImportError as e:
    logging.error(e)
    print("This Python script is written for the Scribus \
      scripting interface.")
    print("It can only be run from within Scribus.")
    sys.exit(1)


def createCaledar(year: int, months: List[int]) -> None:
    firstDay = calendar.MONDAY
    weekNr = False
    weekNrHd="T"
    offsetX=0.0
    marginX=0.0
    offsetY=0.0
    marginY=0.0
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
        fontscale=0.2
    )

    dzzzMoonStyle = MoonStyle(
        cFont="Cambria Math Regular",
        textAlignment=ALIGN_CENTERED,
        textVerticalAlignmentSmallCell=ALIGNV_BOTTOM,
        textVerticalAlignment=ALIGNV_BOTTOM
    )

    calendarStyle = CalendarStyle(
        fullRowHeight=False
    )
    
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
        moonsList=moonsList
    )
    cal.showProgress = False
    cal.dateStyle = dzzzDateStyle
    cal.holidayStyle = dzzzHolidayStyle
    cal.moonStyle = dzzzMoonStyle
    err = cal.createCalendar()
    if err != None:
        messageBox("Napaka", err, icon=ICON_CRITICAL)


def main():
    createCaledar(2023, [4, 6, 7])

if __name__ == '__main__':
    main()
