from RestoreFrame import RestoreFrame
from BackupFrame import BackupFrame
from tkinter import Tk, mainloop, TclError, Frame, Label, messagebox
from tkinter.ttk import Notebook


class About(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        text = "Author: Asad\n" \
               "Version: 1.0 Beta\n" \
               "Date: 13\\01\\2019\n" \
               "Licence: MIT\n" \

        self.text_label = Label(self, text=text).pack(expand=True)


def main():
    """
    todo tests

    Structuring it like this seems bad?
    should use multi threading for ui but maybe later down the line
    loc: 1,012
    """
    root = Tk()
    note = Notebook(root)

    back_f = BackupFrame(note)
    restore_f = RestoreFrame(note)
    about_f = About(note)

    root.title("Backup Utility")

    try:
        root.iconbitmap("icon.ico")  # doesnt break if icon not found
    except TclError:
        pass

    note.add(back_f, text='Backup')
    note.add(restore_f, text='Restore')
    note.add(about_f, text="About")
    note.pack(expand=True, fill="both")
    mainloop()


if __name__ == "__main__":
    try:
        main()  # entry gets the ball rolling
    except BaseException as e:  # fail gracefully
        messagebox.showerror("Fatal Error", f"Fatal Unhandled Exception Occurred: {e}")
