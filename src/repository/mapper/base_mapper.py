from __future__ import annotations

from pattern.singleton import BaseSingleton

class BaseMapper(BaseSingleton):
    """
    mapper基类，基类通过数据库连接客户端抽象工厂进行聚合，可以根据不同的数据库
    进行不同的实现
    """
