import os
import re
from subprocess import call


class Folder:
    """
    Class to represent a folder with assigned extensions

    Attributes:
        folder (str): folder name
        files (list): file that exists in folder
    """
    def __init__(self, folder):
        """
        Folder init method

        Args:

        :param folder: folder name
        """
        self.folder = folder
        self.files = []

    def __str__(self):
        return self.folder

    def __repr__(self):
        return self.__str__()

    def add_file(self, item):
        self.files.append(item)

    def get_name(self):
        """
        :return: end path of the folder
        """
        return self.folder

    def get_extensions(self):
        """
        :return: list of all extensions written as .val
        """
        return list(set([file.get_extension() for file in self.files]))

    def get_file(self):
        return self.files

    def get_files(self):
        return [file for file in self.files]


class File:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def create_extension(self, extension):
        if not self.get_extension():
            self.name += '.' + extension

    def get_extension(self):
        if '.' in self.name:
            return self.name.split(".")[-1]
        else:
            return False

    def get_name(self):
        return self.__str__()

    def get_just_name(self):
        if '.' in self.name:
            return ''.join(self.name.split(".")[:-1])
        else:
            return self.__str__()

    def get_name_with_escape_signs(self):
        return ''.join(["\\" + character for character in self.name])

    def get_next_number(self):
        if re.findall(r".+ \([1-9]+\)$", self.name):
            result = ""
            iterator = len(self.name) - 1
            not_found = True
            while iterator != 0 and not_found:
                if self.name[iterator] == "(":
                    result = self.name[iterator:]
                    not_found = False
                iterator -= 1
            return int(''.join([char for char in result if char.isdigit()]))


class Cleaner:
    """
    Object to represent path for cleaning

    Attributes:
        directory (str): path to directory to make
        folders (list): list containing all folders in directory
    """
    def __init__(self, directory):
        self.directory = directory
        self.folders = []
        self.possibilities = {}

    def _add_folder(self, item):
        """ Adds folder obj to folder list

        Args:
            item (Folder): Folder object to add
        """
        self.folders.append(item)

    def get_folders(self):
        """
        return list containing all folders objects in directory
        """
        return self.folders

    def _search_for_extension(self, searched_extension):
        for folder in self.folders:
            for extension in folder.get_extensions():
                if searched_extension == extension:
                    return True, folder
        return False, None

    def organize(self):
        """
        search for all folders and file with specific extensions stored within them
        """
        downloads_list = [pos for pos in (os.popen(f'ls {self.directory}').read()).split("\n")[:-1]
                          if os.path.isdir(f"{self.directory}/{pos}")]
        for folder in downloads_list:
            temp_folder = Folder(folder)
            self._add_folder(temp_folder)
            self._add_all_files(temp_folder)

    def clean(self, underscore_flag=False):
        """
        Using stored data (found by organize method) to move files in main directory to specific folders
        """

        # file list in main directory
        clean_list = [pos for pos in (os.popen(f'ls {self.directory}').read()).split("\n")[:-1]
                      if os.path.isfile(f"{self.directory}/{pos}")]

        for file in clean_list:
            temp_file = File(file)

            # get extension from file: if file has no extension checking for extension in folders is disabled
            temp_extension = temp_file.get_extension()
            directory_name = ""
            extension_flag = False
            if not temp_extension:
                temp_extension, directory_name = self._file_with_no_extension(temp_file)
                extension_flag = True

            # check if extension is supported: if it's not supported, it's not searching for match in folder's files
            matching_flag = False
            if not extension_flag:
                checker = self._search_for_extension(temp_extension)
                if checker[0] is True:
                    directory_name = checker[1]
                else:
                    directory_name = self._create_or_define(file, temp_extension)
                    matching_flag = True

            # taking out name out of object
            temp_position = temp_file.get_name()

            # checking if same object doesn't exist
            iterator = 0
            ordinal_number = ""
            duplicate = False
            while iterator < len(self.folders) and not matching_flag and not duplicate:
                if self.folders[iterator].get_name() == directory_name:
                    files = self.folders[iterator].get_files()
                    for folder_file in files:
                        if folder_file .get_name() == temp_file.get_name():
                            duplicate = True
                            number = folder_file .get_next_number()
                            if number:
                                ordinal_number = f" ({number+1})"
                            else:
                                ordinal_number = " (1)"
                iterator += 1

            # create model for new file name
            if extension_flag:
                temp_extension = ""
            else:
                temp_extension = '.' + temp_extension

            target_name = (temp_file.get_just_name() + ordinal_number + temp_extension)

            # create file path with escape signs
            target_name = ''.join(["\\" + character for character in target_name])

            # change spaces to underscore
            if underscore_flag:
                target_name = target_name.replace(" ", "_")

            # calling bash command for move file
            call(f'mv /{self.directory}/{temp_position} /{self.directory}/{directory_name}/{target_name}', shell=True)

        # log to console
        if not clean_list:
            print("No actions were taken")
        elif len(clean_list) == 1:
            print("1 file were moved")
            print(f"{clean_list[0]}")
        else:
            print(f"{len(clean_list)} files were moved")
            print(f"{', '.join(clean_list)}")

    def _add_all_files(self, folder):
        """add all extensions found in folder
        Args:
            folder (Folder): folder as holder of possible extensions
        """
        file_list = [pos for pos in os.popen(f'ls {self.directory}/{folder.get_name()}').read().split("\n")[:-1]
                     if os.path.isfile(f"{self.directory}/{folder.get_name()}/{pos}")]
        for position in file_list:
            temp_file = File(position)
            folder.add_file(temp_file)

    def _create_or_define(self, file, extension):
        """method to define solution for unsupported extensions: create new folder or add to existing one?

        :param file: file with unsupported extension
        :param extension: unsupported extension
        :return folder ready where program should move file
        """
        if not self.possibilities:
            self.possibilities = {str(folder): folder for folder in self.folders}

        while True:
            create_folder = input(f"File {file} has unsupported extension: '{extension}'.\n "
                                  f"Do you want to create new folder? [y/N]:\n"
                                  f"(Folders: {', '.join(self.possibilities.keys())}) ")
            if create_folder.lower() == "y":
                return self._create_folder(extension)

            elif create_folder.lower() == "n" or create_folder == "":
                return self._define_extension_folder(extension)
            else:
                print("Invalid input")

    def _create_folder(self, extension):
        """create folder for unsupported extension

        :param extension: unsupported extension
        :return folder (str) created for purpose specific extension
        """
        if not self.possibilities:
            self.possibilities = {str(folder): folder for folder in self.folders}

        while True:
            folder_name = input("Please enter directory name: ")
            checker = [True if char.isalnum() else False for char in folder_name]
            if False not in checker and folder_name not in self.possibilities.keys():
                call(f"mkdir {self.directory}/{folder_name}", shell=True)
                temp_folder = Folder(folder_name)
                self._add_folder(temp_folder)
                temp_file = File(extension)
                temp_folder.add_file(temp_file)
                return folder_name
            else:
                print("Invalid input")

    def _define_extension_folder(self, extension):
        """ Define folder for unsupported extension

        :param extension: unsupported extension
        :return: directory (str) where file should be moved
        """
        if not self.possibilities:
            self.possibilities = {str(folder): folder for folder in self.folders}
        while True:
            directory = input(f"Pick folder where files with {extension} extension should be moved: ")
            if directory in self.possibilities:
                temp_file = File(extension)
                self.possibilities[directory].add_file(temp_file)
                return directory
            else:
                print("Invalid input")

    def _file_with_no_extension(self, file):
        """method for situation when file has no extension

        :param file: file with no extension
        :return: extension for file to work with chosen folder
        """
        if not self.possibilities:
            self.possibilities = {str(folder): folder for folder in self.folders}

        while True:
            directory = input(f"File called '{file}' has no extension.\n"
                              f"From list below pick folder where this file should be moved\n"
                              f"{', '.join(self.possibilities.keys())}\n")
            if directory in self.possibilities:
                if self.possibilities[directory].get_extensions():
                    return self.possibilities[directory].get_extensions()[0], directory
                else:
                    temp_file = File(f".Valid-{file}")
                    self.possibilities[directory].add_file(temp_file)
                    return temp_file, directory
            else:
                print("Invalid input")


def get_name_with_escape_signs(item):
    return ''.join(["\\" + character for character in item])


if __name__ == '__main__':
    populate = Cleaner('/data/Pobrane')
    populate.organize()
    populate.clean(underscore_flag=True)
