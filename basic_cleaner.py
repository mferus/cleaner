import getpass
import os

from chosen_folder import ChosenFolderHandler
from config_handler import ConfigHandler


class Cleaner:
    @staticmethod
    def run_cleaning(dry_run=False, underscore_flag=False):
        """method designed for running program"""

        is_config_exists = os.path.exists(ConfigHandler.config_file)
        if is_config_exists:
            default_directory = ConfigHandler.get("default_directory")
        else:
            default_directory = "/home/" + getpass.getuser() + "/Downloads"

        while True:
            directory = input(
                f"Default directory for cleaner is {default_directory}. \n"
                f"If it's not, please input correct directory: "
            )
            if directory != "" and os.path.isdir(directory):
                break
            elif directory == "" and os.path.isdir(default_directory):
                directory = default_directory
                break
            else:
                print("Provided path is not a directory.")
        if directory != default_directory:
            ConfigHandler.add(default_directory=directory)

        cleaner = ChosenFolderHandler(
            directory, dry_run=dry_run, underscore_flag=underscore_flag
        )
        cleaner.organize()
        cleaner.clean()


if __name__ == "__main__":
    Cleaner.run_cleaning()
