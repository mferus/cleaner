import os
import getpass

from chosen_folder import ChosenFolderHandler
from config_handler import ConfigHandler


class Cleaner:
    @staticmethod
    def run_cleaning():
        """ method designed for running program"""

        is_config_exists = os.path.exists(ConfigHandler.config_file)
        if is_config_exists:
            default_directory = ConfigHandler.get("default_directory")
        else:
            default_directory = "/home/" + getpass.getuser() + "/Downloads"

        while True:
            directory = input(f"Default directory for cleaner is {default_directory}. \n"
                              f"If it's not, please input correct directory: ")
            if directory != "" and os.path.isdir(directory):
                break
            elif directory == "":
                directory = default_directory
                break
            else:
                print("Provided path is not a directory.")
                continue
        if directory != default_directory:
            ConfigHandler.add(default_directory=directory)

        cleaner = ChosenFolderHandler(directory)
        cleaner.organize()
        cleaner.clean()


if __name__ == '__main__':
    Cleaner.run_cleaning()
