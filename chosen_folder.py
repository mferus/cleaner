import os
from typing import Dict

from file import File, PlaceHolderFile
from folder import Folder


class ChosenFolderHandler:
    """
    Object to represent path for cleaning

    Attributes:
        directory: path to directory to make
        folders: containing all folders in directory
        underscore_flag: store if we want to replace spaces with underscores
        dry_run: test program
    """

    def __init__(self, directory, dry_run, underscore_flag):
        self.directory: str = directory
        self.folders: [Folder] = []
        self.underscore_flag: bool = underscore_flag
        self.dry_run: bool = dry_run
        os.chdir(self.directory)

    @property
    def possibilities(self) -> Dict[str, Folder]:
        return {str(folder): folder for folder in self.folders}

    def _search_for_extension(self, searched_extension):
        """Searching for extensions in folders that exists in DownloadsFolders
        :param searched_extension: extension to search
        :return: folder if extension, or empty string if extension is not found
        """
        for folder in self.folders:
            for extension in folder.get_extensions():
                if searched_extension == extension:
                    return str(folder)
        return ""

    def organize(self):
        """
        search for all folders and file with specific extensions stored within them
        """
        for position in os.listdir():
            if os.path.isdir(position):
                temp_folder = Folder(position)
                self.folders.append(temp_folder)
                self._add_all_files(temp_folder)

        self._validate_extensions()

    def clean(self):
        """Using stored data (found by organize method) to move files in main directory to specific folders"""
        clean_list = [
            position
            for position in os.listdir()
            if os.path.isfile(position) and not position.startswith(".")
        ]
        self.move_files(clean_list)

    def check_same_objects(self, directory_name: str, temp_file: File) -> int:
        """method to look for duplicates
        :param directory_name: directory to search for duplicates
        :param temp_file: file object to look for
        """
        number = 0
        if directory_name in self.possibilities:
            files = self.possibilities[directory_name].files
            for file in files:
                if not isinstance(file, PlaceHolderFile) and file == temp_file:
                    number = file.get_next_number()
        return number

    @staticmethod
    def _add_all_files(folder):
        """add all extensions found in folder
        Args:
            folder (Folder): folder as holder of possible extensions
        """
        file_list = [
            position
            for position in os.listdir(str(folder))
            if os.path.isfile(os.path.join(str(folder), position))
            and not position.startswith(".")
        ]
        for position in file_list:
            temp_file = File(position)
            folder.files.append(temp_file)

    def _create_or_define(self, unsupported_file) -> str:
        """method to define solution for unsupported extensions: create new folder or add to existing one?
        :param unsupported_file: file with unsupported extension
        :return folder ready where program should move file
        """

        if self.possibilities:
            if unsupported_file.get_extension():
                search = self._search_for_extension(unsupported_file.get_extension())
                if search:
                    return search
                print(
                    f"----\nFile {unsupported_file} has unsupported extension: '{unsupported_file.get_extension()}'."
                )
            else:
                print(f"----\nFile '{unsupported_file}' has no extension.")
            while True:
                if self.dry_run:
                    print(f"Skipped folder creating for {unsupported_file}")
                    return ""

                create_folder = input(
                    f"Do you want to create new folder for this file? [y/N]:\n"
                    f"(Folders: {', '.join(self.possibilities.keys())})\n"
                )
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
            print(
                f"----\nNo folders found in directory. Please enter directory name for "
                f"{unsupported_file} file:\n"
            )
        else:
            print("Please enter directory name:")

        while True:
            folder_name = input()
            checker = [True if char.isalnum() else False for char in folder_name]
            if False not in checker and folder_name not in self.possibilities.keys():
                os.makedirs(folder_name)
                temp_folder = Folder(folder_name)
                self.folders.append(temp_folder)
                if unsupported_file.get_extension():
                    temp_folder.files.append(unsupported_file)
                return folder_name
            else:
                print("Invalid input")

    def _define_extension_folder(self, unsupported_file):
        """Define folder for unsupported extension

        :param unsupported_file: unsupported file
        :return: directory (str) where file should be moved
        """
        while True:
            directory = input(
                f"Pick folder where file {unsupported_file} extension should be moved: \n"
            )
            if directory in self.possibilities:
                if unsupported_file.get_extension():
                    self.possibilities[directory].files.append(
                        PlaceHolderFile(unsupported_file.name)
                    )
                return directory
            else:
                print("Invalid input")

    def _validate_extensions(self):
        """
        Interface for checking duplicates
        """
        valid_set = self._check_duplicate_extensions()

        if valid_set:
            while True:
                decision = input(
                    "Extensions are scattered in your folders.\n"
                    "Do you want to move them all to specific folder\n"
                    "or just run basic cleaning? [move/basic]: "
                )
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
        for folder in self.folders:
            result += folder.get_extensions()

        # omit files with no extension
        result = [occur for occur in result if occur]
        occurrences = [result.count(phrase) for phrase in result]

        validator = []
        if occurrences:
            for extension in range(len(result)):
                if occurrences[extension] > 1:
                    validator.append(result[extension])
        return set(validator)

    def move_files(self, files, directory=""):
        """moving file to specific directory
        :param files: files to move
        :param directory: where to move (if empty, defined during program run)
        """
        result = []
        for file in files:
            if directory == "":
                temp_file = File(file)
                new_directory = self._create_or_define(temp_file)
                origin_folder = ""
            else:
                new_directory = directory
                origin_folder = os.path.basename(os.path.dirname(file))
                temp_file = File(os.path.basename(file))

            if not file.startswith(new_directory):
                if temp_file.get_extension():
                    temp_extension = "." + temp_file.get_extension()
                else:
                    temp_extension = ""

                ordinal_number = self.check_same_objects(new_directory, temp_file)
                target_name = temp_file.get_just_name() + temp_extension
                if ordinal_number:
                    formatted_ordinal_number = f" ({ordinal_number - 1})"
                    target_name = (
                        temp_file.get_just_name()
                        + formatted_ordinal_number
                        + temp_extension
                    )

                if self.underscore_flag:
                    target_name = target_name.replace(" ", "_")

                new_position = os.path.join(self.directory, new_directory, target_name)

                file_position = os.path.join(
                    self.directory, origin_folder, str(temp_file)
                )
                if file_position != os.path.join(
                    self.directory,
                    new_directory,
                    temp_file.get_just_name() + temp_extension,
                ):
                    result.append(os.path.join(origin_folder, str(temp_file)))
                    self.possibilities[new_directory].files.append(temp_file)
                    if not self.dry_run:
                        os.rename(file_position, new_position)
                    else:
                        print(f"{file_position} would be moved to {new_position}")
                elif self.dry_run:
                    print(
                        f"{file_position} won't be move since the location is the same"
                    )

        self.log_result(result, directory)

    def move_files_with_extension(self, extension):
        """
        Moving files by extension to chosen directory
        :param extension:
        :return:
        """

        while True:
            files_with_extension = self.collect_files_with_extensions(extension)
            print(files_with_extension)
            folders_containing = set(
                [
                    os.path.basename(os.path.dirname(file))
                    for file in files_with_extension
                ]
            )
            directory = input(
                f"Files with '{extension}' extension are scattered in your folders:\n"
                f" {', '.join(folders_containing)}\n"
                f"Where do you want to put them?\n"
                f"({', '.join(self.possibilities.keys())})\n"
            )
            if directory in self.possibilities:
                self.move_files(files_with_extension, directory)
                break
            else:
                print("Invalid Input")

    def collect_files_with_extensions(self, extension):
        """Collect all files with specific extension

        :param extension:
        :return:
        """
        occurrences = []
        for position in os.listdir(self.directory):
            if os.path.isdir(position):
                for file in os.listdir(position):
                    if os.path.isfile(os.path.join(position, file)) and file.endswith(
                        extension
                    ):
                        occurrences.append(os.path.join(self.directory, position, file))
        return occurrences

    def log_result(self, result_list, directory=None):
        """
        printing effects of work to console
        """
        if not result_list:
            result = "No cleaning was required"
        else:
            if self.dry_run:
                file_verb = ("file" if len(result_list) == 1 else "files") + " would be"
            else:
                file_verb = "file was" if len(result_list) == 1 else "files were"
            directory_verb = f" to directory {directory}" if directory else ""
            result = f"{len(result_list)} {file_verb} moved{directory_verb}:\n{', '.join(result_list)}"
        print(result)
