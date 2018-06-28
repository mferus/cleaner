import os
import re
from subprocess import call
import getpass


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
        :return: list of all extensions found in folder
        """
        return set([file.get_extension() for file in self.files])

    def get_file(self):
        return self.files

    def get_files(self):
        return [file for file in self.files]


class File:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def create_extension(self, extension):
        if not self.get_extension():
            self.name += '.' + extension

    def get_extension(self):
        if '.' in self.name:
            return self.name.split(".")[-1]
        else:
            return ""

    def get_name(self):
        return self.__str__()

    def get_just_name(self):
        if '.' in self.name:
            return ''.join(self.name.split(".")[:-1])
        else:
            return self.__str__()

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
        else:
            return 1


class DownloadsFolder:
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
                    return folder.get_name()
        return ""

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
        self._validate_extensions()

    def clean(self, underscore_flag=False):
        """
        Using stored data (found by organize method) to move files in main directory to specific folders
        """

        # file list in main directory
        clean_list = [pos for pos in (os.popen(f'ls {self.directory}').read()).split("\n")[:-1]
                      if os.path.isfile(f"{self.directory}/{pos}")]

        for file in clean_list:
            temp_file = File(file)
            new_directory = self._create_or_define(temp_file)

            # same name case
            ordinal_number = self.check_same_objects(new_directory, temp_file)

            # extension case
            temp_extension = ""
            if temp_file.get_extension():
                temp_extension = '.' + temp_file.get_extension()

            target_name = temp_file.get_just_name() + ordinal_number + temp_extension

            if underscore_flag:
                target_name = target_name.replace(" ", "_")

            file_position = get_name_with_escape_signs(f"/{self.directory}/{temp_file.get_name()}")
            new_position = get_name_with_escape_signs(f"/{self.directory}/{new_directory}/{target_name}")

            call(f'mv {file_position} {new_position}', shell=True)

        # log to console
        if not clean_list:
            print("No cleaning were required")
        elif len(clean_list) == 1:
            print("1 file were moved")
            print(f"{clean_list[0]}")
        else:
            print(f"{len(clean_list)} files were moved")
            print(f"{', '.join(clean_list)}")

    def check_same_objects(self, directory_name, temp_file):
        ordinal_number = ""
        files = self.possibilities[directory_name].get_files()

        for file in files:
            if file.get_name() == temp_file.get_name():
                number = file.get_next_number()
                if number:
                    ordinal_number = f" ({number+1})"
                elif not number:
                    ordinal_number = ""
                else:
                    ordinal_number = " (2)"
        return ordinal_number

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

    def _create_or_define(self, file):
        """method to define solution for unsupported extensions: create new folder or add to existing one?

        :param file: file with unsupported extension
        :return folder ready where program should move file
        """
        if not self.possibilities:
            self.possibilities = {str(folder): folder for folder in self.folders}

        if file.get_extension():
            search = self._search_for_extension(file.get_extension())
            if search:
                return search
            print(f"File {file} has unsupported extension: '{file.get_extension()}'.")
        else:
            print(f"File '{file}' has no extension.")
        while True:
            create_folder = input(f"Do you want to create new folder for this file? [y/N]:\n"
                                  f"(Folders: {', '.join(self.possibilities.keys())}) ")
            if create_folder.lower() == "y":
                return self._create_folder(file)

            elif create_folder.lower() == "n" or create_folder == "":
                return self._define_extension_folder(file)
            else:
                print("Invalid input")

    def _create_folder(self, file):
        """create folder for unsupported extension

        :param file: file object
        :return folder (str) created for purpose specific extension
        """

        while True:
            folder_name = input("Please enter directory name: ")
            checker = [True if char.isalnum() else False for char in folder_name]
            if False not in checker and folder_name not in self.possibilities.keys():
                call(f"mkdir {self.directory}/{folder_name}", shell=True)
                temp_folder = Folder(folder_name)
                self._add_folder(temp_folder)
                if file.get_extension():
                    temp_folder.add_file(file)
                return folder_name
            else:
                print("Invalid input")

    def _define_extension_folder(self, file):
        """ Define folder for unsupported extension

        :param file: unsupported file
        :return: directory (str) where file should be moved
        """
        if not self.possibilities:
            self.possibilities = {str(folder): folder for folder in self.folders}
        while True:
            directory = input(f"Pick folder where file {file.get_name()} extension should be moved: ")
            if directory in self.possibilities:
                if file.get_extension():
                    self.possibilities[directory].add_file(file)
                return directory
            else:
                print("Invalid input")

    def _validate_extensions(self):
        """
        Interface for checking duplicates
        """
        valid_set = self._check_duplicate_extensions()

        if valid_set:
            decision = input("Extensions are scattered in your folders.\n"
                             "Do you want to move them all to specific folder\n"
                             "or just run basic cleaning? [move/basic]: ")
            while True:
                if decision.lower() == "move":
                    for record in valid_set:
                        self.move_files(record)
                    break
                elif decision.lower() == "basic":
                    break
                else:
                    print("Invalid Input")

    def _check_duplicate_extensions(self):
        """
        looking for duplicates in folders
        """
        result = []
        for folder in self.get_folders():
            result += folder.get_extensions()

        # omit files with no extension
        result = [occur for occur in result if occur is not ""]
        occur_list = [result.count(phrase) for phrase in result]

        validator = []
        if max(occur_list) > 1:
            for extension in range(len(result)):
                if occur_list[extension] > 1:
                    validator.append(result[extension])
        return set(validator)

    def move_files(self, extension):
        """
        Moving files by extension to chosen directory
        :param extension:
        :return:
        """
        if not self.possibilities:
            self.possibilities = {str(folder): folder for folder in self.folders}
        files_with_extension = self.collect_extensions(extension)
        folders_containing = set([file.split("/")[0] for file in files_with_extension])

        directory = input(f"Files with '{extension}' extension are scattered in your folders:\n"
                          f" {', '.join(folders_containing)}\n"
                          f"Where do you want to put them?\n"
                          f"{', '.join(self.possibilities.keys())}")
        result = []
        while True:
            if directory in self.possibilities:
                for file in files_with_extension:
                    temp_file = File(file.split("/")[-1])
                    if not file.startswith(directory):
                        result.append(file)
                    ordinal_number = self.check_same_objects(directory, temp_file)
                    temp_extension = ""
                    if temp_file.get_extension():
                        temp_extension = '.' + temp_file.get_extension()
                    target_name = (temp_file.get_just_name() + ordinal_number + temp_extension)
                    direction_file = get_name_with_escape_signs(target_name)
                    file = get_name_with_escape_signs(file)
                    call(f'mv {self.directory}/{file} {self.directory}/{directory}/{direction_file}', shell=True)
                print(f"Files:\n{', '.join(result)}\n moved to {directory} directory")
                break
            else:
                print("Invalid Input")

    def collect_extensions(self, extension):
        """ Collect all files with specific extension

        :param extension:
        :return:
        """
        occurs = os.popen(f'find {self.directory} -maxdepth 2 -name *.{extension}')
        result = []
        for occur in occurs:
            temp_path = occur.replace(f"{self.directory}/", "")[:-1]
            result.append(temp_path)
        return result


def get_name_with_escape_signs(item):
    return ''.join(["\\" + character for character in item])


def run_cleaning(underscore_flag=True):
    """ method designed for running program, like basic interface

    :param underscore_flag:
    :return:
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

    cleaner = DownloadsFolder(default_directory)
    cleaner.organize()
    cleaner.clean(underscore_flag=underscore_flag)


if __name__ == '__main__':
    run_cleaning()
