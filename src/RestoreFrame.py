from tkinter import *
from tkinter.ttk import *
from Restore import Restore, BadBackupFile, InvalidPassword
from tkinter import messagebox
from tkinter.filedialog import askdirectory, askopenfilename
import os.path as op
import time


class RestoreFrame(Frame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        """
        ui setup
        """

        # create frames
        self.top_frame = Frame(self)
        self.bottom_frame = Frame(self)

        # create labels
        Label(self.top_frame, text="Password: ").grid(row=0, sticky=W)
        Label(self.top_frame, text="File To Restore: ").grid(row=1, sticky=W)
        Label(self.top_frame, text="Output Folder:  ").grid(row=2, sticky=W)

        # create text box and progress bar
        self.text = Text(self.bottom_frame, font=("Calibri", 12, ""), state=DISABLED)
        self.progress_bar = Progressbar(self.bottom_frame, orient=HORIZONTAL, length=100, mode='determinate')

        # create entry boxes
        self.pass_box = Entry(self.top_frame, show="*", width=100)
        self.restore_file = Entry(self.top_frame, width=100)
        self.output_path = Entry(self.top_frame, width=100)

        # create buttons
        self.browse_b = Button(self.top_frame, text="Browse", command=self.browse_restore_file, width=10)
        self.browse_dir_b = Button(self.top_frame, text="Browse", command=self.browse_output_path, width=10)
        # self.exit_b = Button(self, text="Exit", command=exit, width=10)
        self.backup_b = Button(self, text="Restore", command=self.restore, width=10)
        self.show_pass_b = Button(self.top_frame, text="Show Pass", width=10)

        # position widgets
        self.pass_box.grid(row=0, column=1, columnspan=30)
        self.restore_file.grid(row=1, column=1, columnspan=30)
        self.output_path.grid(row=2, column=1, columnspan=30)
        self.show_pass_b.grid(row=0, column=31, sticky=W)
        self.browse_b.grid(row=1, column=31, sticky=W)
        self.browse_dir_b.grid(row=2, column=31, sticky=W)

        self.top_frame.pack(fill=X)
        self.bottom_frame.pack(fill=BOTH, expand=True)

        self.progress_bar.pack(fill=X, expand=True, side=TOP)
        self.text.pack(fill=BOTH, expand=True)

        # self.exit_b.pack(side=RIGHT)
        self.backup_b.pack(side=LEFT)

        # bind buttons
        self.show_pass_b.bind('<ButtonPress-1>', lambda _: self.pass_box.config(show=""))
        self.show_pass_b.bind('<ButtonRelease-1>', lambda _: self.pass_box.config(show="*"))

    def __call__(self, *args, func="ui_print", **kwargs):
        """
        couldn't think of a better way for the class to access the ui without a callback
        proves a number of call backs main to manipulate the progress bar or print to the text box
        """
        funcs = {"ui_print": self.ui_print,
                 "start_progress_bar": self.progress_bar.start,
                 "stop_progress_bar": self.progress_bar.stop,
                 "set_progress_config": self.progress_bar.config,
                 "update": self.update}

        try:
            funcs[func](*args, **kwargs)
        except KeyError:
            return
        finally:
            self.update()

    def restore(self):
        """
        main restore function sets up inputs for restore class
        """
        restore_file = self.restore_file.get()
        out_path = self.output_path.get()
        password = self.pass_box.get()

        if not self.check_inputs(restore_file, out_path, password):
            return

        self.disable_buttons()  # disables all buttons

        restore_obj = Restore(restore_file, out_path, password)  # get restore class object

        start = time.time()

        try:
            restore_obj.restore(ui_caller=self)
        except BadBackupFile:
            messagebox.showerror("Bad Backup File",
                                 f"File to restore is not a valid backup file:\n{restore_file}")
            self("Error Occurred Restore Aborted")
            self.enable_buttons()
            return

        except InvalidPassword:
            messagebox.showerror("Incorrect Password",
                                 f"Password Incorrect: {'*'*len(password)}")
            self("Error Occurred Restore Aborted")
            self.enable_buttons()
            return
        except OSError as e:
            messagebox.showerror("OS Error",
                                 f"Following Error Occurred During Restore: {e}")
            self("Error Occurred, Restore Aborted")
            self.enable_buttons()
            return

        end = time.time()

        self("Time Taken: " + str((end - start) / 60) + " mins")

        self.enable_buttons()  # re-enable all buttons

        messagebox.showinfo("Restore Complete",
                            f"Restore Successfully completed\n Output File: {out_path}")

    def browse_restore_file(self):
        """
        opens interactive browse window which user can use to locate file
        """
        file = askopenfilename(initialdir="/",
                               title="Select Locked",
                               filetypes=(("locked files", "*.locked"),))
        self.restore_file.delete(0, 'end')
        self.restore_file.insert(0, file)

    def browse_output_path(self):
        """
        opens interactive browse window which user can use to locate folder
        """
        dir_ = askdirectory()
        self.output_path.delete(0, 'end')
        self.output_path.insert(0, dir_)

    def disable_buttons(self):
        """
        changes all buttons states to disabled
        """
        self.browse_b.configure(state=DISABLED)
        self.browse_dir_b.configure(state=DISABLED)
        self.backup_b.configure(state=DISABLED)

    def enable_buttons(self):
        """
        changes all buttons states to normal
        """
        self.browse_b.configure(state="normal")
        self.browse_dir_b.configure(state="normal")
        self.backup_b.configure(state="normal")

    def ui_print(self, data):
        self.text.config(state="normal")
        self.text.insert(END, data + "\n\n")
        self.text.see(END)
        self.text.config(state=DISABLED)
        self.update()

    @staticmethod
    def check_inputs(restore_file, output_path, password):
        """
        validates user inputs
        """
        if not password:
            messagebox.showerror("Error", "Password Required")
            return False
        elif not op.exists(restore_file) or not op.exists(output_path):
            messagebox.showerror("Error", "Selected paths where not found")
            return False
        elif not op.isfile(restore_file) or not op.isdir(output_path):
            messagebox.showerror("Error", "Restore file must be a FILE\nOutput folder must be a FOLDER")
            return False
        elif op.samefile(restore_file, output_path):
            messagebox.showerror("Error", "Selected paths are the same")
            return False
        else:
            return True
