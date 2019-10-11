import os
import re
from subprocess import call
import getpass


class Folder:
    def __init__(self, folder):
        self.folder = folder
        self.files = []

    def __str__(self):
        return self.folder

    def __repr__(self):
        return self.__str__()

    def add_file(self, item):
        self.files.append(item)

    def get_name(self):
        return self.folder

    def get_extensions(self):
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
        """ create extension for file if extension doesn't exist"""
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
        """get name without extension"""
        if '.' in self.name:
            return ''.join(self.name.split(".")[:-1])
        else:
            return self.__str__()

    def get_next_number(self):
        """get next number for file: case if file is duplicated"""
        if re.findall(r".+\([0-9]+\)" + "." + self.get_extension(), self.name):
            result = ""
            iterator = len(self.name) - 1
            not_found = True
            while iterator != 0 and not_found:
                if self.name[iterator] == "(":
                    result = self.name[iterator:]
                    not_found = False
                iterator -= 1
            return int(''.join([char for char in result if char.isdigit()]))+1
        else:
            return 2


class DownloadsFolder:
    """
    Object to represent path for cleaning

    Attributes:
        directory (str): path to directory to make
        folders (list): containing all folders in directory
        possibilities (dict): store folders name
        underscore_flag (bool): store if we want to replace spaces with underscores
    """
    def __init__(self, directory):
        self.directory = directory
        self.folders = []
        self.possibilities = {}
        self.underscore_flag = True

    def _add_folder(self, item):
        """ item (Folder): Folder object to add
        """
        self.folders.append(item)

    def get_flag(self):
        return self.underscore_flag

    def set_flag(self, boolean):
        self.underscore_flag = boolean

    def get_folders(self):
        """
        :return: (list) containing all folders objects in directory
        """
        return self.folders

    def _search_for_extension(self, searched_extension):
        """ Searching for extensions in folders that exists in DownloadsFolders
        :param searched_extension: extension to search
        :return: folder if extension, or empty string if extension is not found
        """
        for folder in self.folders:
            for extension in folder.get_extensions():
                if searched_extension == extension:
                    return folder.get_name()
        return ""

    def organize(self):
        """
        search for all folders and file with specific extensions stored within them
        """
        for position in (os.popen(f'ls {self.directory}').read()).split("\n")[:-1]:
            if os.path.isdir(f"{self.directory}/{position}"):
                temp_folder = Folder(position)
                self._add_folder(temp_folder)
                self._add_all_files(temp_folder)

        self._validate_extensions()

    def clean(self):
        """Using stored data (found by organize method) to move files in main directory to specific folders"""
        # file list in main directory
        clean_list = [pos for pos in (os.popen(f'ls {self.directory}').read()).split("\n")[:-1]
                      if os.path.isfile(f"{self.directory}/{pos}")]
        self.move_files(clean_list)

    def check_same_objects(self, directory_name, temp_file):
        """ method to look for duplicates
        :param directory_name: directory to search for duplicates
        :param temp_file: file object to look for
        :return: next number, if required
        """
        ordinal_number = ""
        if directory_name in self.possibilities:
            files = self.possibilities[directory_name].get_files()

            for file in files:
                if file.get_name() == temp_file.get_name():
                    number = file.get_next_number()
                    ordinal_number = f" ({number})"
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

    def _create_or_define(self, unsupported_file):
        """method to define solution for unsupported extensions: create new folder or add to existing one?
        :param unsupported_file: file with unsupported extension
        :return folder ready where program should move file
        """
        self.possibilities = {str(folder): folder for folder in self.folders}

        if self.possibilities:
            if unsupported_file.get_extension():
                search = self._search_for_extension(unsupported_file.get_extension())
                if search:
                    return search
                print(f"----\nFile {unsupported_file} has unsupported extension: '{unsupported_file.get_extension()}'.")
            else:
                print(f"----\nFile '{unsupported_file}' has no extension.")
            while True:
                create_folder = input(f"Do you want to create new folder for this file? [y/N]:\n"
                                      f"(Folders: {', '.join(self.possibilities.keys())})\n")
                if create_folder.lower() == "y":
                    return self._create_folder(unsupported_file)

                elif create_folder.lower() == "n" or create_folder == "":
                    return self._define_extension_folder(unsupported_file)
                else:
                    print("Invalid input")
        else:
            return self._create_folder(unsupported_file)

    def _create_folder(self, unsupported_file):
        """create folder for unsupported extension

        :param unsupported_file: file object
        :return folder (str) created for purpose specific extension
        """
        if not self.possibilities:
            print(f"----\nNo folders found in directory. Please enter directory name for "
                  f"{unsupported_file} file:\n")
        else:
            print("Please enter directory name:")

        while True:
            folder_name = input()
            checker = [True if char.isalnum() else False for char in folder_name]
            if False not in checker and folder_name not in self.possibilities.keys():
                call(f"mkdir {self.directory}/{folder_name}", shell=True)
                temp_folder = Folder(folder_name)
                self._add_folder(temp_folder)
                if unsupported_file.get_extension():
                    temp_folder.add_file(unsupported_file)
                self.possibilities = {str(folder): folder for folder in self.folders}
                return folder_name
            else:
                print("Invalid input")

    def _define_extension_folder(self, unsupported_file):
        """ Define folder for unsupported extension

        :param unsupported_file: unsupported file
        :return: directory (str) where file should be moved
        """
        if not self.possibilities:
            self.possibilities = {str(folder): folder for folder in self.folders}
        while True:
            directory = input(f"Pick folder where file {unsupported_file.get_name()} extension should be moved: \n")
            if directory in self.possibilities:
                if unsupported_file.get_extension():
                    self.possibilities[directory].add_file(unsupported_file)
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
                        self.move_files_with_extension(record)
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
        if occur_list:
            for extension in range(len(result)):
                if occur_list[extension] > 1:
                    validator.append(result[extension])
        return set(validator)

    def move_files(self, work_list, directory=""):
        """ moving file to specific directory

        :param work_list: files to move
        :param directory: where to move (if empty, defined during program run)
        """
        result = []
        for file in work_list:
            if directory == "":
                temp_file = File(file)
                new_directory = self._create_or_define(temp_file)
                origin_folder = ""
            else:
                new_directory = directory
                origin_folder = "/" + file.split("/")[0]
                temp_file = File(file.split("/")[-1])

            if not file.startswith(new_directory):
                result.append(file)

                # same name case
                ordinal_number = self.check_same_objects(new_directory, temp_file)

                # extension case
                temp_extension = ""
                if temp_file.get_extension():
                    temp_extension = '.' + temp_file.get_extension()

                target_name = temp_file.get_just_name() + ordinal_number + temp_extension

                if self.underscore_flag:
                    target_name = target_name.replace(" ", "_")

                file_position = get_name_with_escape_signs(f"{self.directory}{origin_folder}/{temp_file.get_name()}")
                new_position = get_name_with_escape_signs(f"{self.directory}/{new_directory}/{target_name}")

                call(f'mv {file_position} {new_position}', shell=True)

        self.log_result(result)

    def move_files_with_extension(self, extension):
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
                          f"({', '.join(self.possibilities.keys())})\n")
        while True:
            if directory in self.possibilities:
                self.move_files(files_with_extension, directory)
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

    @staticmethod
    def log_result(result_list, directory=None):
        """
        printing effects of work to console
        """
        if not result_list:
            result = "No cleaning were required"
        else:
            file_verb = "file was" if len(result_list) == 1 else "files were"
            directory_verb = f" to directory {directory}" if directory else ""
            result = f"{len(result_list)} {file_verb} moved{directory_verb}:\n{', '.join(result_list)}"
        return print(result)


def get_name_with_escape_signs(item):
    return ''.join(["\\" + character for character in item])


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

    cleaner = DownloadsFolder(default_directory)
    cleaner.organize()
    cleaner.clean()


if __name__ == '__main__':
    run_cleaning()
