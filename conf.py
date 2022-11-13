from typing import List
from os import environ

from configparser import ConfigParser, NoSectionError


class BaseConfLoader:
    """
    Loader 的基类，他很简单，实现 get_val 就可以了
    """

    def get_val(self, key):
        raise NotImplemented


class INILoader(BaseConfLoader):
    """
    *.ini 文件的加载器
    """

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
    """
    环境变量的加载器
    """

    def get_val(self, key: str):
        val = environ.get(key.upper())
        return val or None


class ConfType(type):
    """
    Configuration 的元类，用来从其他配置文件加载配置
    """

    def __new__(mcs, name, bases, attrs: dict):
        # 取出当前 Configuration 子类中配置的 loaders 变量
        loaders: List[BaseConfLoader] = attrs.get('loaders') or tuple()

        '''
        取出当前 Configuration 子类的 __annotations__
        类变量的注解都放到这个特殊属性中了, 这是 python 的特性
        
        比如: 
        class TestConf(Configuration):
            loaders = [ENVLoader()]

            path: str = ''
            
        path 类属性加了 str 注解，path 就会出现在 __annotations__ 中 
        '''
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
    """
    自动从各种地方加载配置信息的类

    该功能分成了三个类来实现
    Configuration 和 ConfType 负责更新以类变量形式定义的配置项
    BaseConfLoader 由用户继承定义具体加载配置项的逻辑
    由此可以适应多种配置文件的加载
    """

    # 加载配置的 loader, 可以从环境变量, *.ini, *.yaml, 等等加载配置
    loaders = []


if __name__ == '__main__':
    class TestConf(Configuration):
        loaders = [ENVLoader()]

        # 配置项
        path: str = ''

    print(TestConf.path)
