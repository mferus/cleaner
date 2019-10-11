import os
import getpass

from chosen_folder import ChosenFolderHandler


class Cleaner:
    @staticmethod
    def run_cleaning():
        """ method designed for running program, like basic interface
        """
        default_directory = "/home/" + getpass.getuser() + "/Downloads"

        while True:
            directory = input(f"Default directory for cleaner is {default_directory}. \n"
                              f"If it's not, please input correct directory: ")
            if directory != "":
                default_directory = directory
            if os.path.isdir(directory):
                break
            else:
                print("Provided path is not a directory.")

        cleaner = ChosenFolderHandler(default_directory)
        cleaner.organize()
        cleaner.clean()


if __name__ == '__main__':
    Cleaner.run_cleaning()
