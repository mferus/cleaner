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
