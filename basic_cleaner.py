import os
from subprocess import call


class Folder:
    """
    Class to represent a folder with assigned extensions

    Attributes:
        folder (str): folder name
        extensions (list): list of assigned extensions
    """
    def __init__(self, folder):
        """
        Folder init method

        Args:

        :param folder: folder name
        """
        self.folder = folder
        self.extensions = []

    def __str__(self):
        return self.folder

    def __repr__(self):
        return self.__str__()

    def add_extension(self, item):
        self.extensions.append(item)

    def get_name(self):
        """
        :return: end path of the folder
        """
        return self.folder + "/"

    def get_extensions(self):
        """
        :return: list of all extensions written as .val
        """
        return self.extensions


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

    def get_name_with_escape_signs(self):
        return ''.join(["\\" + character for character in self.name])


class Cleaner:
    """
    Object to represent path for cleaning

    Attributes:
        directory (str): path to directory to make
        folders (list): list containing all folders in directory
        # extensions (list): list containing all extensions supported by our current setup
    """
    def __init__(self, directory):
        self.directory = directory
        self.folders = []

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
            self._add_all_extensions(temp_folder)

    def clean(self):
        """
        Using stored data (found by organize method) to move files in main directory to specific folders
        """

        # file list in main directory
        clean_list = [pos for pos in (os.popen(f'ls {self.directory}').read()).split("\n")[:-1]
                      if os.path.isfile(f"{self.directory}/{pos}")]

        for file in clean_list:
            temp_file = File(file)

            # get extension from file
            temp_extension = temp_file.get_extension()
            if not temp_extension:
                temp_extension = self._file_with_no_extension(temp_file)

            # create file path with escape signs
            temp_position = temp_file.get_name_with_escape_signs()

            # check if extension is supported
            checker = self._search_for_extension(temp_extension)
            if checker[0] is True:
                directory_name = checker[1]
            else:
                directory_name = self._create_or_define(file, temp_extension)

            call(f'mv /{self.directory}/{temp_position} /{self.directory}/{directory_name}', shell=True)

        if not clean_list:
            print("No actions were taken")
        elif len(clean_list) == 1:
            print("1 file were moved")
            print(f"{clean_list[0]}")
        else:
            print(f"{len(clean_list)} files were moved")
            print(f"{', '.join(clean_list)}")

    def _add_all_extensions(self, folder):
        """add all extensions found in folder
        Args:
            folder (Folder): folder as holder of possible extensions
        """
        file_list = [pos for pos in os.popen(f'ls {self.directory}/{folder.get_name()}').read().split("\n")[:-1]
                     if os.path.isfile(f"{self.directory}/{folder.get_name()}/{pos}")]
        result = set()
        for position in file_list:
            temp_file = File(position)
            temp_extension = temp_file.get_extension()
            if temp_extension:
                result.add(temp_extension)
        for extension in result:
            folder.add_extension(extension)

    def _create_or_define(self, file, extension):
        """method to define solution for unsupported extensions: create new folder or add to existing one?

        :param file: file with unsupported extension
        :param extension: unsupported extension
        :return folder ready where program should move file
        """

        possibility_list = {str(folder): folder for folder in self.folders}

        while True:
            create_folder = input(f"File {file} has unsupported extension: '{extension}'.\n "
                                  f"Do you want to create new folder? [y/N]:\n"
                                  f"(Folders: {', '.join(possibility_list.keys())}) ")
            if create_folder.lower() == "y":
                return self._create_folder(extension)

            elif create_folder.lower() == "n" or create_folder is None:
                return self._define_extension_folder(extension)
            else:
                print("Invalid input")

    def _create_folder(self, extension):
        """create folder for unsupported extension

        :param extension: unsupported extension
        :return folder (str) created for purpose specific extension
        """
        while True:
            folder_name = input("Please enter directory name: ")
            checker = [True if char.isalnum() else False for char in folder_name]
            if False not in checker:
                call(f"mkdir {self.directory}/{folder_name}", shell=True)
                temp_folder = Folder(folder_name)
                self._add_folder(temp_folder)
                temp_folder.add_extension(extension)
                return folder_name
            else:
                print("Invalid input")

    def _define_extension_folder(self, extension):
        """ Define folder for unsupported extension

        :param extension: unsupported extension
        :return: directory (str) where file should be moved
        """
        possibility_list = {str(folder): folder for folder in self.folders}
        while True:
            directory = input(f"Pick folder where files with {extension} extension should be moved: ")
            if directory in possibility_list:
                possibility_list[directory].add_extension(extension)
                return directory
            else:
                print("Invalid input")

    def _file_with_no_extension(self, file):
        """method for situation when file has no extension

        :param file: file with no extension
        :return: extension for file to work with chosen folder
        """
        possibility_list = {str(folder): folder for folder in self.folders}
        while True:
            directory = input(f"File called '{file}' has no extension.\n"
                              f"From list below pick folder where this file should be moved\n"
                              f"{', '.join(possibility_list.keys())}\n")
            if directory in possibility_list:
                if possibility_list[directory].get_extensions():
                    return possibility_list[directory].get_extensions()[0]
                else:
                    temp_extension = f"Valid-{file}"
                    possibility_list[directory].add_extension(temp_extension)
                    return temp_extension
            else:
                print("Invalid input")


if __name__ == '__main__':
    populate = Cleaner('/home/mferus/Downloads')
    populate.organize()
    populate.clean()
