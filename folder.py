from file import File


class Folder:
    def __init__(self, name):
        self.name = name
        self.files: list[File] = []

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def get_extensions(self):
        return set([file.get_extension() for file in self.files])
