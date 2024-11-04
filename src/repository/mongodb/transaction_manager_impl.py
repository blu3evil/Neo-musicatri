""" pymongo事务管理器实现 """
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from pymongo.synchronous.client_session import ClientSession
from typing_extensions import override, Optional
from utils import log
from utils.locale import default_locale as _

from repository.transaction_manager import TransactionManager

class TransactionManagerImpl(TransactionManager):
    """ 事务管理器Mongodb数据库实现 """
    def __init__(self, client: MongoClient):
        self.client = client
        self.session: Optional[ClientSession] = None

    @override
    def is_active(self):
        """ 当前事务是否开启 """
        return self.session is not None

    @override
    def begin(self):
        """ 开启事务 """
        self.session = self.client.start_session()
        self.session.start_transaction()  # 开启事务

    @override
    def commit(self):
        """ 提交事务 """
        if self.session:  # 若会话存在，那么提交会话
            self.session.commit_transaction()  # 提交会话

    @override
    def rollback(self):
        if self.session:
            try:
                self.session.abort_transaction()  # 回滚
            except OperationFailure as error:
                log.error(_('error occur while rollback transaction: %(error)s'), {'error': error})

    @override
    def get_session(self):
        return self.session

    @override
    def stop(self):
        """ 终止会话 """
        if self.session:
            self.session.end_session()
            self.session = None

    @override
    def set_isolation_level(self, level):
        """
        mongodb次啊用乐观并发控制而非悲观锁定，事务隔离级别由session对象的配置
        进行控制，不存在事务隔离级别的配置，保留空实现
        """
        pass

