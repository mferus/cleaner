import configparser
import os


class ConfigHandler:
    cleaner_path = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(cleaner_path, "cleaner.ini")

    @classmethod
    def get(cls, parameter):
        config = configparser.ConfigParser()
        config.read(cls.config_file)
        return config['DEFAULT'][parameter]

    @classmethod
    def add(cls, **kwargs):
        config_container = {}
        for kwarg in kwargs:
            config_container.update({kwarg: kwargs[kwarg]})

        config = configparser.ConfigParser()
        config['DEFAULT'] = config_container

        with open(cls.config_file, 'w') as configFile:
            config.write(configFile)
