from typing import List
from os import environ

from configparser import ConfigParser, NoSectionError


class BaseConfLoader:
    def get_val(self, key):
        raise NotImplemented


class INILoader(BaseConfLoader):
    def __init__(self, file):
        self.file = file
        self.parser = ConfigParser()
        self.parser.read(file, encoding='utf-8')

    def get_val(self, key: str):
        scope, field = key.split('_', 1)
        try:
            return self.parser.get(scope, field)
        except NoSectionError as e:
            return None


class ENVLoader(BaseConfLoader):
    def get_val(self, key: str):
        val = environ.get(key.upper())
        return val or None


class ConfType(type):
    def __new__(mcs, name, bases, attrs: dict):
        loaders: List[BaseConfLoader] = attrs.get('loaders') or tuple()

        annotations = attrs.get('__annotations__')
        annotations = annotations or {}

        for field, type_ in annotations.items():
            for loader in loaders:
                val = loader.get_val(field)
                if val is None:
                    continue
                attrs[field] = type_(val)
                break
        return type.__new__(mcs, name, bases, attrs)


class Configuration(metaclass=ConfType):
    loaders = []


if __name__ == '__main__':
    class TestConf(Configuration):
        loaders = [ENVLoader()]

        path: str = ''

    print(TestConf.path)
