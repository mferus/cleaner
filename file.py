import re


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
        if re.findall(r".+\(\d+\)" + "." + self.get_extension(), self.name):
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


class PlaceHolderFile(File):
    pass
