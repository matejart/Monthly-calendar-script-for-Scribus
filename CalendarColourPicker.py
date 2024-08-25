import sys
import re

try:
    from scribus import (
        changeColorCMYK,
        defineColorCMYK,
        defineColorRGB,
        getColor,
        getColorAsRGB,
        haveDoc,
        ICON_CRITICAL,
        messageBox,
        NotFoundError,
        redrawAll,
    )
except ImportError:
    print("This Python script is written for the Scribus \
      scripting interface.")
    print("It can only be run from within Scribus.")
    sys.exit(1)

try:
    import tkinter as tk
    from tkinter import colorchooser, Frame, messagebox
except ImportError:
    print("This script requires Python Tkinter properly installed.")
    messageBox('Script failed',
               'This script requires Python Tkinter properly installed.',
               ICON_CRITICAL)
    sys.exit(1)


class ColorCategory:
    """ Structure to represent a colour category (a row in the GUI picker) """
    name: str
    cmyk: tuple = (0, 0, 0, 0)
    color_names: list

    def __init__(self, name: str, cmyk: tuple, color_names: list):
        self.name = name
        self.cmyk = cmyk
        self.color_names = color_names

    @classmethod
    def CreateSimpleColorCategories(cls) -> list:
        return [
            ColorCategory(
                name="Main colour",
                cmyk=(0, 0, 0, 0),
                color_names=[
                    "txtWeekend-m{}", "txtDayNamesWeekend-m{}", "txtHoliday-m{}",
                    "fillMonthHeading-m{}"
                ]
            ),
            ColorCategory(
                name="Light colour",
                cmyk=(0, 0, 0, 0),
                color_names=[ "txtWeekend2-m{}", ]
            ),
            ColorCategory(
                name="Date text",
                cmyk=(0, 0, 0, 0),
                color_names=[ "txtDate2-m{}", ]
            ),
            ColorCategory(
                name="Special date text",
                cmyk=(0, 0, 0, 0),
                color_names=[ "txtSpecialDate-m{}", ]
            ),
        ]

class TkColorSchemeEditor(Frame):
    """ Implementation of the dialog for editing the months' colour scheme """
    TEMPORARY_COLOR = "calColorSchemeTemporary"

    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.color_categories = ColorCategory.CreateSimpleColorCategories()
        self.months = ["January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November",
                       "December"]
        self.current_month = 1
        self._init_gui()

        self._load_colors(1)

    def _init_gui(self):
        self.master.title("Calendar colour picker")

        self.message = tk.Label(self.master, text="Message ...")

        # Month picker area
        month_frame = tk.Frame(self.master)
        month_frame.grid(row=0, column=0, columnspan=9)

        month_label = tk.Label(month_frame, text="Month:")
        month_label.grid(row=0, column=0)
        month_dropdown = tk.StringVar()
        month_dropdown.set("January")  # Set an initial value
        month_menu = tk.OptionMenu(
            month_frame,
            month_dropdown,
            *self.months,
            command=self._on_select_month)
        month_menu.grid(row=0, column=1)

        self.vars: list = []
        self.rects: list = []
        # Colour grid
        for i, color_category in enumerate(self.color_categories):
            row_label = tk.Label(self.master, text=color_category.name)
            row_label.grid(row=i+1, column=0)

            # Colored rectangle
            color_rect = tk.Label(self.master, bg="black", width=10, height=2)
            color_rect.grid(row=i+1, column=1)
            self.rects.append(color_rect)

            color_rect.bind("<Button-1>",
                            lambda event, category_i=i: self.pick_color(event, category_i))

            # Input boxes for CMYK values
            cyan_var = tk.StringVar(value="0", name=f"cyan_{i + 1}")
            magenta_var = tk.StringVar(value="0", name=f"magenta_{i + 1}")
            yellow_var = tk.StringVar(value="0", name=f"yellow_{i + 1}")
            black_var = tk.StringVar(value="0", name=f"black_{i + 1}")
            self.vars.append([cyan_var, magenta_var, yellow_var, black_var])

            cyan_label = tk.Label(self.master, text="C:")
            magenta_label = tk.Label(self.master, text="M:")
            yellow_label = tk.Label(self.master, text="Y:")
            black_label = tk.Label(self.master, text="K:")
            cyan_label.grid(row=i+1, column=2)
            magenta_label.grid(row=i+1, column=4)
            yellow_label.grid(row=i+1, column=6)
            black_label.grid(row=i+1, column=8)

            check_percent = (self.master.register(self._validate_percent), "%W", "%P", "%V")
            cyan_entry = tk.Entry(
                self.master, textvariable=cyan_var, validate="all", validatecommand=check_percent, name=f"c_{i}")
            magenta_entry = tk.Entry(
                self.master, textvariable=magenta_var, validate="all", validatecommand=check_percent, name=f"m_{i}")
            yellow_entry = tk.Entry(
                self.master, textvariable=yellow_var, validate="all", validatecommand=check_percent, name=f"y_{i}")
            black_entry = tk.Entry(
                self.master, textvariable=black_var, validate="all", validatecommand=check_percent, name=f"k_{i}")
            cyan_entry.grid(row=i+1, column=3)
            magenta_entry.grid(row=i+1, column=5)
            yellow_entry.grid(row=i+1, column=7)
            black_entry.grid(row=i+1, column=9)

        # Buttons
        button_row = len(self.color_categories) + 1
        apply_button = tk.Button(self.master, text="Apply", command=self.apply_color)
        reset_button = tk.Button(self.master, text="Reset", command=self.reset_color)
        close_button = tk.Button(self.master, text="Close", command=self.close_dialog)
        apply_button.grid(row=button_row, column=0, columnspan=2)
        reset_button.grid(row=button_row, column=2, columnspan=2)
        close_button.grid(row=button_row, column=4, columnspan=2)

        self.message.grid(row=button_row, column=6, columnspan=4)

    def _validate_percent(self, widget: str, newval: str, op: str):
        valid = re.match("^[0-9]$|^[1-9][0-9]$|^(100)$", newval) is not None
        msg = f"Validating {widget} on {op} at {newval}: {valid}"
        if valid:
            namesplit = widget.split("_")
            row_n = int(namesplit[1])
            color_name = namesplit[0][1:]
            try:
                row = self.vars[row_n]
                cmyk = {
                    "c": row[0].get(),
                    "m": row[1].get(),
                    "y": row[2].get(),
                    "k": row[3].get()
                }
                cmyk[color_name] = newval

                msg = f"{msg}: {cmyk}"

                defineColorCMYK(TkColorSchemeEditor.TEMPORARY_COLOR,
                                int(round(int(cmyk["c"])/100*255)),
                                int(round(int(cmyk["m"])/100*255)),
                                int(round(int(cmyk["y"])/100*255)),
                                int(round(int(cmyk["k"])/100*255)))
                (r, g, b) = getColorAsRGB(TkColorSchemeEditor.TEMPORARY_COLOR)

                self.rects[row_n].config(background=f"#{r:02x}{g:02x}{b:02x}")
            except Exception as e:
                msg = f"{type(e)}: {e}"

        #self.message.config(text=msg)
        if op == "key":
            return True
        return valid

    def _load_colors(self, month):
        for i, color_category in enumerate(self.color_categories):
            cmyk = color_category.cmyk
            color_name = str.format(color_category.color_names[0], month)
            try:
                cmyk = getColor(color_name)
            except NotFoundError:
                messagebox.showerror(
                    message=f"Colour {color_name} not found in the document.")
                self.master.destroy()
            color_category.cmyk = cmyk

            self._set_row_entries(i, cmyk)

    def _set_row_entries(self, row_i: int, cmyk: tuple):
        for ci in range(4):
            self.vars[row_i][ci].set(int(100*int(cmyk[ci])/255))

    def _get_row_entries(self, row_i: int) -> tuple:
        return tuple(
            [
                int(round(int(self.vars[row_i][ci].get())*2.55))
                for ci in range(4)
            ]
        )

    def _on_select_month(self, *args):
        try:
            month = self.months.index(args[0]) + 1
        except ValueError:
            messagebox.showerror(message=f"Unknown month {args[0]}.")
            return
        self.current_month = month
        self._load_colors(month)

    def pick_color(self, event, category_i: int):
        try:
            source = event.widget
            rgb = colorchooser.askcolor(source.cget("background"))
            if rgb[0] is not None:
                self.message.config(text=f"{rgb[0]}")
                defineColorRGB(TkColorSchemeEditor.TEMPORARY_COLOR, *rgb[0])
                cmyk = getColor(TkColorSchemeEditor.TEMPORARY_COLOR)

                self.color_categories[category_i].cmyk = cmyk
                self._set_row_entries(category_i, cmyk)
        except Exception as e:
            self.message.config(text=f"{e}")

    def apply_color(self):
        color_category = self.color_categories[self.current_month - 1]
        for color_name_pattern in color_category.color_names:
            color_name = str.format(color_name_pattern, self.current_month)
            try:
                changeColorCMYK(color_name, )

    def reset_color(self):
        for i, color_category in enumerate(self.color_categories):
            self._set_row_entries(i, color_category.cmyk)

    def close_dialog(self):
        self.master.destroy()


def main():
    """ Application/Dialog for editing colour schemes for each month """
    if haveDoc() <= 0:
        messageBox("Document required",
            "A file containing a monthly calendar needs to be open.",
            ICON_CRITICAL)
        sys.exit(1)

    try:
        root = tk.Tk()
        app = TkColorSchemeEditor(root)
        root.mainloop()
    finally:
        redrawAll()

if __name__ == '__main__':
    main()