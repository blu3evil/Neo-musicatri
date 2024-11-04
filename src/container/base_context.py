"""
项目上下文
"""
from abc import abstractmethod
from typing import Type, Union, TypeVar, Callable
from injector import Injector, ScopeDecorator, Scope, singleton, Module, provider

from pattern.singleton import BaseSingleton
class BaseContext(BaseSingleton):
    """
    项目运行环境上下文，在项目运行的过程中作为项目全局容器存在，管理项目配置、项目依赖信息，可以通过这个对象获取项目
    开发过程中所需的对象、配置信息

    可能由于循环依赖的方式导致注入失败，可以考虑直接引入静态类来尝试避免循环引用
    * 注：应当避免将仅包含静态方法的工具类注入ApplicationContext
    * 开发中应仅仅将需要[实例化]但是[单例]的对象注册进入容器，例如MVC组件

    用法示例:
    通过类型直接指定需要的实例，使用get方法来获取实例
    -   from logging import Logger
    -   from context import ApplicationContext
    -   ApplicationContext.get(Logger)  # 获取项目的日志类

    如何向ApplicationContext注入实例对象，直接在下面添加绑定信息即可
    ApplicationContext使用单例设计模式，通过在类方法中通过_cls._instance来访问Injector
    -   @classmethod
    -   def __initialize_context(cls):
    -       from injector import singleton
    -       cls._instance.binder.bind(str, to="pineclone", scope=singleton)
    """
    def __init__(self):
        self.injector: Injector = Injector()  # 容器
        self.setup()  # 容器初始化

    T = TypeVar('T')
    def get(self, interface: Type[T], scope: Union[ScopeDecorator, Type[Scope], None] = None) -> T:
        """ 获取上下文对象 """
        return self.injector.get(interface=interface, scope=scope)

    def register(self, interface: Type[T], to: object, scope=singleton):
        """ 饿汉式加载注册，不推荐使用这个方法注册实例，因为使用此方法注册需要特别注意循环依赖问题 """
        self.injector.binder.bind(interface, to, scope=scope)

    def lazy_register(self, interface: Type[T], supplier: Callable[[], any], scope=singleton):
        """ 懒加载，通过传入闭包实现懒加载，可以减少循环依赖问题的产生 """
        if scope is singleton:  # 单例注册
            class SingletonModule(Module):
                @provider
                @singleton
                def dynamic_provider(self) -> interface:   # 模块闭包
                    return supplier()
            self.injector.binder.install(SingletonModule())  # 下载模块

        else:  # 非单例注册
            class PrototypeModule(Module):
                @provider
                def dynamic_provider(self) -> interface:
                    return supplier()
            self.injector.binder.install(PrototypeModule())

    @abstractmethod
    def setup(self):
        """ 容器初始化，在其中向容器注入对象 """
        pass



