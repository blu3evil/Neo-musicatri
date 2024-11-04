""" 单例模板 """
class SingletonMeta(type):
    """ 单例元类 """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class BaseSingleton(metaclass=SingletonMeta):
    """ 单例基类，可以通过实现这个类来快速构建单例类 """
    pass
