""" 事务管理器 """
from abc import abstractmethod

class TransactionManager:
    @abstractmethod
    def begin(self):
        """
        开启事务，用于启动一个新的数据库事务。它会开始一个事务块，所有在该事务块内执行的数据库操作将被视为一个整体，
        可以在事务提交时一并提交，或者在发生错误时进行回滚

        * 如果当前已有一个活动事务，调用此方法时将抛出异常
        """
        pass

    @abstractmethod
    def commit(self):
        """
        提交事务，方法用于提交当前事务中的所有更改，将它们永久应用到数据库中。如果事务中没有错误或异常，
        调用该方法会将所有数据库操作的结果提交到数据库

        * 调用commit不会引起事务会话关闭
        * 如果当前没有活动事务，调用此方法时将抛出异常
        """
        pass

    @abstractmethod
    def rollback(self):
        """
        回滚事务，方法用于回滚当前事务中的所有更改，将事务中所做的所有操作撤销，并恢复到事务开始前的状态。
        通常用于在发生错误或异常时撤回事务，

        * 调用回滚不会引起事务会话关闭
        * 如果没有会话对象，调用此方法时将抛出异常
        """
        pass

    @abstractmethod
    def close(self):
        """
        关闭当前事务会话并清理相关资源。在调用 `commit` 或 `rollback` 后，应该调用 `close` 方法来结束当前事务。
        此方法会释放当前事务会话（session）所占用的资源，确保与数据库的连接被适当关闭，并清理可能占用的任何临时数据。

        * 调用close会引起会话关闭
        * 如果会话对象不存在，那么会抛出异常
        """
        pass

    @abstractmethod
    def is_active(self) -> bool:
        """
        当前是否开启事务，
        方法用于检查当前是否存在一个活动的事务。它返回一个布尔值，指示当前是否有事务正在进行。

        :return True: 当前存在事务， False: 当前不存在事务
        """
        pass