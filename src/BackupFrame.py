from tkinter import *
from tkinter.ttk import *
from Backup import Backup
from tkinter import messagebox
from ConfigMGR import ConfigMGR
from tkinter.filedialog import askdirectory
from datetime import datetime, timedelta
import os.path as op
import time


class BackupFrame(Frame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        """
        ui setup
        """

        self.config = ConfigMGR()

        # create frames
        self.top_frame = Frame(self)
        self.bottom_frame = Frame(self)

        # create labels
        Label(self.top_frame, text="Password: ").grid(row=0, sticky=W)
        Label(self.top_frame, text="Folder To Backup: ").grid(row=1, sticky=W)
        Label(self.top_frame, text="Output Folder:  ").grid(row=2, sticky=W)

        # create text box and progress bar
        self.text = Text(self.bottom_frame, font=("Calibri", 12, ""), state=DISABLED)
        self.progress_bar = Progressbar(self.bottom_frame, orient=HORIZONTAL, length=100, mode='determinate')

        # create entry boxes
        self.pass_box = Entry(self.top_frame, show="*", width=100)
        self.target_folder = Entry(self.top_frame, width=100)
        self.backup_path = Entry(self.top_frame, width=100)

        # create buttons
        self.show_pass_b = Button(self.top_frame, text="Show Pass", width=10)
        self.browse_b = Button(self.top_frame, text="Browse", command=self.browse_dir_target, width=10)
        self.browse_dir_b = Button(self.top_frame, text="Browse", command=self.browse_dir_backup, width=10)
        # self.exit_b = Button(self, text="Exit", command=exit, width=10)
        self.backup_b = Button(self, text="Backup", command=self.backup, width=10)
        self.set_default_b = Button(self, text="Set Default Paths", command=self.set_default_inputs)

        # position widgets
        self.pass_box.grid(row=0, column=1, columnspan=30)
        self.target_folder.grid(row=1, column=1, columnspan=30)
        self.backup_path.grid(row=2, column=1, columnspan=30)
        self.show_pass_b.grid(row=0, column=31, sticky=W)
        self.browse_b.grid(row=1, column=31, sticky=W)
        self.browse_dir_b.grid(row=2, column=31, sticky=W)

        self.top_frame.pack(fill=X)
        self.bottom_frame.pack(fill=BOTH, expand=True)

        self.progress_bar.pack(fill=X, expand=True, side=TOP)
        self.text.pack(fill=BOTH, expand=True)

        # self.exit_b.pack(side=RIGHT)
        self.set_default_b.pack(side=LEFT)
        self.backup_b.pack(side=LEFT)

        # bind buttons
        self.show_pass_b.bind('<ButtonPress-1>', lambda _: self.pass_box.config(show=""))
        self.show_pass_b.bind('<ButtonRelease-1>', lambda _: self.pass_box.config(show="*"))

        self.load_defaults()  # load default values into entry widgets

    def __call__(self, *args, func="ui_print", **kwargs):
        """
        couldn't think of a better way for the class to access the ui without a callback
        proves a number of call backs main to manipulate the progress bar or print to the text box
        """
        funcs = {"ui_print": self.ui_print,
                 "start_progress_bar": self.progress_bar.start,
                 "stop_progress_bar": self.progress_bar.stop,
                 "set_progress_config": self.progress_bar.config}

        try:
            funcs[func](*args, **kwargs)
        except KeyError:
            return
        finally:
            self.update()

    def backup(self):
        """
        function takes gui inputs, plugs into backup class
        runs backup
        displays relevant outputs

        flow:
         - get inputs from input boxes
         - check inputs
         - disable buttons
         - create backup object
         -  start timer
         - run back function
         - end timer
         - display time taken

        """
        target_folder = self.target_folder.get()
        backup_folder = self.backup_path.get()
        password = self.pass_box.get()

        if not self.check_inputs(target_folder, backup_folder, password):
            return

        self.disable_buttons()

        backup_obj = Backup(target_folder, backup_folder, password)

        start = time.time()
        try:
            dest = backup_obj.backup(ui_caller=self)
        except OSError as e:
            messagebox.showerror("OS Error",
                                 f"Following Error Occurred During Backup: {e}")
            self("Error Occurred, Backup Aborted")
            self.enable_buttons()
            return

        end = time.time()

        t = datetime(1, 1, 1) + timedelta(seconds=(end - start))
        self(f"Time Taken: {t.hour} Hours: {t.minute} Minutes: {t.second} Seconds")
        self.enable_buttons()

        messagebox.showinfo("Backup Complete", f"Backup Successfully completed\n Output File: {dest}")

    def browse_dir_target(self):
        """
        opens interactive browse window which user can use to locate folder
        """
        dir_ = askdirectory()
        self.target_folder.delete(0, 'end')
        self.target_folder.insert(0, dir_)

    def browse_dir_backup(self):
        """
        opens interactive browse window which user can use to locate folder
        """
        dir_ = askdirectory()
        self.backup_path.delete(0, 'end')
        self.backup_path.insert(0, dir_)

    def disable_buttons(self):
        """
        changes all buttons states to disabled
        """
        self.browse_b.configure(state=DISABLED)
        self.browse_dir_b.configure(state=DISABLED)
        self.backup_b.configure(state=DISABLED)
        self.set_default_b.configure(state=DISABLED)

    def enable_buttons(self):
        """
        changes all buttons states to normal
        """
        self.browse_b.configure(state="normal")
        self.browse_dir_b.configure(state="normal")
        self.backup_b.configure(state="normal")
        self.set_default_b.configure(state="normal")

    def ui_print(self, data):
        self.text.config(state="normal")
        self.text.insert(END, data + "\n\n")
        self.text.see(END)
        self.text.config(state=DISABLED)
        self.update()

    @staticmethod
    def check_inputs(target_folder, backup_folder, password):
        """
         validates user inputs
         """
        if not password:
            messagebox.showerror("Error", "Password Required")
            return False
        elif len(password) > 16:
            messagebox.showerror("Error Password Too Long", "Password Greater Then 16 Characters")
            return False
        elif not op.exists(target_folder) or not op.exists(backup_folder):
            messagebox.showerror("Error", "Selected paths where not found")
            return False
        elif not op.isdir(target_folder) or not op.isdir(backup_folder):
            messagebox.showerror("Error", "Selected paths are not folders")
            return False
        elif op.samefile(target_folder, backup_folder):
            messagebox.showerror("Error", "Selected paths are the same")
            return False
        else:
            return True

    def load_defaults(self):
        """
        retrieves default inputs from config manager and inserts into text box
        """
        defaults = self.config.load_default_inputs()

        self.pass_box.delete(0, END)
        self.pass_box.insert(0, defaults["pass"])

        self.backup_path.delete(0, END)
        self.backup_path.insert(0, defaults["backup_path"])

        self.target_folder.delete(0, END)
        self.target_folder.insert(0, defaults["target_path"])

    def set_default_inputs(self):
        """
        retrieves inputs from text boxes validates and sends to config manager
        """
        target_folder = self.target_folder.get()
        backup_folder = self.backup_path.get()
        password = self.pass_box.get()
        if not target_folder and not backup_folder and not password:
            self.config.set_default_inputs("", "", "")
            messagebox.showinfo("Set Default Paths", f"Defaults Cleared!\n")
            return
        else:
            if not self.check_inputs(target_folder, backup_folder, password):
                return

        self.config.set_default_inputs(password, backup_folder, target_folder)

        messagebox.showinfo("Set Default Paths", f"Paths Successfully set as default:\n"
                                                 f"Target Folder: {target_folder}\n"
                                                 f"Backup Folder: {backup_folder}")
