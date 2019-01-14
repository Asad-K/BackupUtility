import zipfile
import tempfile
from crypto import Crypto
import pathlib
import json
import shutil


class InvalidPassword(Exception):
    pass


class BadBackupFile(Exception):
    pass


class Restore:
    """
    Restore class restores file from a correctly formatted .zip.locked file
    files names and data are preserved, file system specific meta data lost such as original data created etc.
    Usage: Restore(date backups.zip.locked path, destination directory, password to decrypt backup)
    """

    def __init__(self, backup_path: str, restore_path: str, password: str):
        self.backup_path = backup_path
        self.restore_path = restore_path

        pathlib.Path(restore_path).mkdir(parents=True, exist_ok=True)  # create restore directory

        self.tempfile = tempfile.TemporaryDirectory()

        self.crypto = Crypto(password)

    def restore(self, ui_caller=print):

        """
        groups restore functions and runs in correct order
        """
        ui_caller("Step 1 of 4: unzipping files")
        try:
            self.unzip_to_temp()
        except zipfile.BadZipFile:  # incorrect password
            self.tempfile.cleanup()
            raise InvalidPassword()

        ui_caller("Step 2 of 4: parsing config")
        dir_tree, file_tree = self.parse_config()

        ui_caller("Step 3 of 3: building directory tree")
        self.build_directory_tree(dir_tree)

        ui_caller("Step 4 of 4: restoring files")
        self.restore_files(file_tree, ui_caller)

        self.tempfile.cleanup()
        ui_caller("done!")
        return True

    def unzip_to_temp(self):
        """
        decrypts and unzips backup file to temp folder and relevant internal zips
        order: date backup.zip.locked -> backup.zip -> config, duplicates.zip -> config, duplicates.zip, *.duplicate
        """
        temp_zip = self.tempfile.name + "\\backup.zip"

        try:
            self.crypto.decrypt_file(self.backup_path, temp_zip)
        except BaseException:  # struct.error: unpack requires a buffer of 8 bytes raised if file invalid
            self.tempfile.cleanup()
            raise BadBackupFile(self.backup_path)

        with zipfile.ZipFile(temp_zip, mode="r", allowZip64=True) as zipf:
            zipf.extractall(path=self.tempfile.name)

        with zipfile.ZipFile(self.tempfile.name + "\\duplicates.zip", mode="r", allowZip64=True) as zipf:
            zipf.extractall(path=self.tempfile.name)

    def parse_config(self):
        """
        parses json from config file in temp folder
        """
        with open(self.tempfile.name + "\\config", "r") as f:
            _json = json.loads(f.read().strip())
        return _json["directory_tree"], _json["file_tree"]

    def build_directory_tree(self, dir_tree: list):
        """
        iterates through dir tree parsed from config
        builds directory tree in destination folder
        uses Path.mkdir()
        """
        for dir_ in dir_tree:
            pathlib.Path(self.restore_path + dir_).mkdir(parents=True, exist_ok=True)

    def restore_files(self, file_tree: dict, ui_caller):
        """
        only to be used after build_directory_tree
        iterates through keys (md5 hashes) and accesses values (list of paths)
        copies files with hash.duplicate to its location in the destination directory with name corrected amended
        """
        ui_caller(func="start_progress_bar")
        ui_caller(func="set_progress_config", maximum=len(file_tree.keys()))

        for index, hash_ in enumerate(file_tree):

            ui_caller(func="set_progress_config", value=index)

            for path in file_tree[hash_]:
                shutil.copy(self.tempfile.name + "\\" + hash_ + ".duplicate", self.restore_path + path)

        ui_caller(func="stop_progress_bar")
