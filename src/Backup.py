from FileItter import FileItter
from collections import defaultdict
import os.path as op
import pathlib
from crypto import Crypto
import json
import zipfile
import os
import tempfile
import datetime
import shutil


class Backup:
    """
    main backup class runs and controls backup procedure
    backups reduced in file count by 84% and size by 64%

    Usage: Backup(target path, backup path, password to encrypt with)
    """

    def __init__(self, target_path: str, backup_path: str, password: str):
        if not op.isdir(target_path):
            raise Exception()

        self.crypto = Crypto(password)

        self.file_iterator = FileItter(target_path)
        self.files = self.file_iterator.itter_files(target_path)
        self.directories = self.file_iterator.itter_directories()

        self.temp_folder = tempfile.TemporaryDirectory()

        self.backup_path = backup_path
        self.target_path = target_path
        self.temp_path = self.temp_folder.name

        pathlib.Path(backup_path).mkdir(parents=True, exist_ok=True)  # creates backup folder

        self.backup_zip = zipfile.ZipFile(self.temp_path + "\\backup.zip",
                                          mode='w', compression=zipfile.ZIP_STORED, allowZip64=True)

        self.backup_zip_path = self.backup_zip.filename

        self.main_config_dict = dict()

    def backup(self, ui_caller=print):
        """
        main backup function
        """

        ui_caller("Starting:")
        ui_caller("Step 1 of 6: Building directory tree")
        self.backup_directory_tree()

        ui_caller("Step 2 of 6: Building file tree")
        self.backup_file_tree(ui_caller)

        ui_caller("Step 3 of 6: Packing Data")
        self.store_target_files(self.main_config_dict, ui_caller)

        ui_caller("Step 4 of 6: Storing file trees")
        self.store_config_files()

        self.backup_zip.close()  # closing backup zip

        ui_caller("Step 5 of 6: Encrypting files")
        self.backup_zip_path = self.crypto.encrypt_file(self.backup_zip.filename)

        dest = self.backup_path + "/" + datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") \
               + " " + pathlib.Path(self.backup_zip_path).name  # potential path merging issue on Linux

        if op.exists(dest):  # checks if file already exists
            os.remove(dest)

        ui_caller(f"Step 6 of 6: Copying backup to target location: {dest}")
        shutil.copy(self.backup_zip_path, dest)
        self.temp_folder.cleanup()  # cleanup temp folder

        ui_caller("Done!")

        self.generate_stats(self.main_config_dict["file_tree"], ui_caller)

        return dest

    def backup_file_tree(self, ui_caller):
        """
        builds a dict with hash of file as a key and a list of files with that has as the value
        {"hash":["list", "of", "files", "with", "the", "has"]}
        """
        paths_dict = defaultdict(list)
        files = list(self.files)

        if not files:  # checks if folder has files
            raise OSError("Specified folder is Empty")

        ui_caller(func="start_progress_bar")
        ui_caller(func="set_progress_config", maximum=len(files))

        for index, file_path in enumerate(files):
            paths_dict[self.file_iterator.hash_file(file_path)].append(file_path.replace(self.target_path, ""))

            ui_caller(func="set_progress_config", value=index)

        ui_caller(func="stop_progress_bar")

        self.main_config_dict["file_tree"] = dict(paths_dict)

    def backup_directory_tree(self):
        """
        builds directory tree in the backup path using path lib
        parents=True -> will make all parents as necessary
        exists=True -> if the folder exists it will ignore
        """
        self.main_config_dict["directory_tree"] = [i.replace(self.target_path, "") for i in self.directories]

    def store_target_files(self, config_dict: dict, ui_caller):
        """
        creates zip file in backup location
        adds a single entry of each duplicate file to the zip
        renames the file to its hash
        if the file has only one copy it is copied straight to the backup folder
        """
        zip_file = zipfile.ZipFile(self.temp_path + "\\duplicates.zip",
                                   mode='w', compression=zipfile.ZIP_STORED, allowZip64=True)
        files = config_dict['file_tree'].items()

        ui_caller(func="start_progress_bar")
        ui_caller(func="set_progress_config", maximum=len(files))

        for index, kv in enumerate(files):
            #  kv -> (key, value) -> (str, list) -> (hash, list of paths with same hash)
            ui_caller(func="set_progress_config", value=index)

            path = kv[-1][0]  # choose first path
            zip_file.write(self.target_path + path, arcname=kv[0] + ".duplicate")

        ui_caller(func="stop_progress_bar")

        zip_file.close()

        self.backup_zip.write(zip_file.filename, arcname="duplicates.zip")

        os.remove(zip_file.filename)

    def store_config_files(self):
        """
        writes files dictionary and stats to config file
        """
        path = self.temp_path + "\\config"
        with open(path, "w") as f:
            f.write(json.dumps(self.main_config_dict))
        self.backup_zip.write(path, arcname="config")
        os.remove(path)

    @staticmethod
    def generate_stats(config_dict: dict, ui_caller) -> dict:
        """
        mainly for the user generates a set of stats about a particular backup
        """
        individual_files_count = len(config_dict)
        file_count = sum([len(v) for k, v in config_dict.items()])
        reduction_percent = int(100 - ((individual_files_count / file_count) * 100))
        ui_caller("--- Stats ---")
        ui_caller(f"Number of unique files: {individual_files_count}")
        ui_caller(f"Total number of files: {file_count}")
        ui_caller(f"Compression Ratio: {reduction_percent}%")

        return {"individual_files_count": individual_files_count,
                "file_count": file_count,
                "reduction_percent": reduction_percent}
