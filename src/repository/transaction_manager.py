""" 事务管理器 """
from abc import abstractmethod

from pattern.singleton import BaseSingleton

class TransactionManager(BaseSingleton):
    @abstractmethod
    def begin(self):
        """ 开启事务 """
        pass

    @abstractmethod
    def commit(self):
        """ 提交事务 """
        pass

    @abstractmethod
    def rollback(self):
        """ 回滚事务 """
        pass

    @abstractmethod
    def get_session(self):
        """ 获得当前会话 """
        pass

    @abstractmethod
    def stop(self):
        """ 终止会话 """
        pass

    @abstractmethod
    def set_isolation_level(self, level):
        """ 设置事务隔离级别 """
        pass

    @abstractmethod
    def is_active(self):
        """ 当前是否开启事务 """
        pass