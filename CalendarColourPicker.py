import sys
import re

try:
    from scribus import (
        defineColorCMYK,
        getColorAsRGB,
        haveDoc,
        ICON_CRITICAL,
        messageBox,
        redrawAll,
    )
except ImportError:
    print("This Python script is written for the Scribus \
      scripting interface.")
    print("It can only be run from within Scribus.")
    sys.exit(1)

try:
    import tkinter as tk
    from tkinter import Frame, messagebox
except ImportError:
    print("This script requires Python Tkinter properly installed.")
    messageBox('Script failed',
               'This script requires Python Tkinter properly installed.',
               ICON_CRITICAL)
    sys.exit(1)


class TkColorSchemeEditor(Frame):
    """ Implementation of the dialog for editing the months' colour scheme """
    TEMPORARY_COLOR = "calColorSchemeTemporary"

    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.master.title("Calendar colour picker")

        self.message = tk.Label(self.master, text="Message ...")

        # Month picker area
        month_frame = tk.Frame(self.master)
        month_frame.grid(row=0, column=0, columnspan=9)

        month_label = tk.Label(month_frame, text="Month:")
        month_label.grid(row=0, column=0)
        month_dropdown = tk.StringVar()
        month_dropdown.set("January")  # Set an initial value
        month_menu = tk.OptionMenu(month_frame, month_dropdown, "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
        month_menu.grid(row=0, column=1)

        self.vars: list[tk.StringVar] = []
        self.rects: list[tk.Label] = []
        # Colour grid
        labels = ["Main colour", "Light colour", "Date text", "Special date text"]
        for i, label_text in enumerate(labels):
            row_label = tk.Label(self.master, text=label_text)
            row_label.grid(row=i+1, column=0)

            # Colored rectangle
            color_rect = tk.Label(self.master, bg="black", width=10, height=2)
            color_rect.grid(row=i+1, column=1)
            self.rects.append(color_rect)

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
        apply_button = tk.Button(self.master, text="Apply", command=self.apply_color)
        reset_button = tk.Button(self.master, text="Reset", command=self.reset_color)
        close_button = tk.Button(self.master, text="Close", command=self.close_dialog)
        apply_button.grid(row=len(labels)+1, column=0, columnspan=2)
        reset_button.grid(row=len(labels)+1, column=2, columnspan=2)
        close_button.grid(row=len(labels)+1, column=4, columnspan=2)

        self.message.grid(row=len(labels)+1, column=6, columnspan=4)

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
                                int(int(cmyk["c"])/100*255),
                                int(int(cmyk["m"])/100*255),
                                int(int(cmyk["y"])/100*255),
                                int(int(cmyk["k"])/100*255))
                (r, g, b) = getColorAsRGB(TkColorSchemeEditor.TEMPORARY_COLOR)

                self.rects[row_n].config(background=f"#{r:02x}{g:02x}{b:02x}")
            except Exception as e:
                msg = f"{type(e)}: {e}"

        self.message.config(text=msg)
        if op == "key":
            return True
        return valid

    def apply_color(self):
        # Get the selected color from the color chooser
        # Update the colored rectangles or perform any other actions
        messagebox.showinfo(
            message=f"Main colour c {self.vars[0][0].get()}, m {self.vars[0][1].get()}, y {self.vars[0][2].get()}, k {self.vars[0][3].get()}"
        )

    def reset_color(self):
        # Reset the color values to default or initial values
        # You can implement this based on your needs
        pass

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