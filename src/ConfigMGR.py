import random
import json
import os.path as op
import os
import functools


def save(func):
    """
    decorator saves data to file after use
    """

    @functools.wraps(func)
    def stub(self, *args, **kwargs):
        ret = func(self, *args, *kwargs)
        with open(self.config_file_path, "w") as f:
            json.dump(self.data, f)
        return ret

    return stub


class ConfigMGR:
    """
    class manages config data
    main config data dict structure {"defaults": ("password", "backup_path", "target_path"), "backups": [backup_dict...]}'
    backup_dict = {"size": int, "pass": password, "original_path": path, "backup_path", path}

    !!! backup_dict and associated function not yet implemented !!!
    """

    # todo class unfinished
    def __init__(self):
        self.config_file_path = op.abspath("config.json")  # retrieve full path fo json file

        try:  # config file validation
            self.data = json.load(open(self.config_file_path, "r"))
            keys = ["pass", "backup_path", "target_path"]

            # checks if default keys are valid
            for key in self.data["defaults"].keys():
                if key not in keys:  # removes keys that should not be in dict
                    raise KeyError()
                else:
                    keys.remove(key)  # if found remove key from list

            if keys:  # checks if any key is missing
                raise KeyError()

        except (FileNotFoundError, KeyError, json.decoder.JSONDecodeError):
            json.dump({"defaults": {"pass": "", "backup_path": "", "target_path": ""}},
                      open(self.config_file_path, "w"))
            self.data = json.load(open(self.config_file_path, "r"))

    @save
    def set_default_inputs(self, password, backup_path, target_path):
        """
        stores inputs in json to be written to text file
        """
        self.data["defaults"] = {"pass": password, "backup_path": backup_path, "target_path": target_path}

    def load_default_inputs(self):
        """
        returns default values from config
        """
        return self.data["defaults"]

    def get_backups(self):
        """
        Testing unused
        """
        final = []
        for i in range(278):
            final.append({"date": "2018-12-28 22-24-55",
                          "values": ("path_to_backup", "original_path", "358MB", "True", "True"),
                          "tags": random.choice(["NotFound", "Found"])})
        return final

    def get_file_size(self, path):
        """
        Testing unused
        return file size as nicely formatted string e.g 500MB
        """
        return op.getsize(path)

    @save
    def store_backup_data(self, path_to_backup, original_path):
        """
        Testing unused
        """
        self.data["backups"].append({"size": self.get_file_size(path_to_backup),
                                     "original_path": original_path,
                                     "backup_path": path_to_backup})

    @save
    def remove_backup(self, path_to_backup, delete_file=True):
        """
        Testing unused
        """
        if op.exists(path_to_backup) and delete_file:
            os.remove(path_to_backup)
        for entry in list(self.data["backups"]):
            if op.samefile(entry["backup_path"], path_to_backup):
                self.data["backups"].remove(entry)
                break
