""" pymongo事务管理器实现 """
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from pymongo.synchronous.client_session import ClientSession
from typing_extensions import override, Optional
from utils.locale import default_locale as _

from repository.abs.transaction_manager import TransactionManager

class TransactionManagerMongoImpl(TransactionManager):
    """ 事务管理器Mongodb数据库实现 """
    def __init__(self, client: MongoClient):
        self._client = client
        self._session: Optional[ClientSession] = None

    @override
    def is_active(self):
        """ 当前事务是否开启 """
        return self.session is not None

    @override
    def begin(self):
        """ 开启事务 """
        # 检查是否已经存在事务
        if self.is_active():
            raise OperationFailure(_("session already begin"))

        # 不存在事务，开启事务
        self.session = self._client.start_session()
        self.session.start_transaction()  # 开启事务

    @override
    def commit(self):
        """ 提交事务 """
        if self.session:  # 若会话存在，那么提交会话
            self.session.commit_transaction()  # 提交会话
        else:
            # 事务不存在
            raise OperationFailure(_("no session to commit"))

    @override
    def rollback(self):
        """ 回滚事务 """
        if self.session:
            self.session.abort_transaction()  # 回滚
        else:
            # 事务不存在
            raise OperationFailure(_("no session to rollback"))

    @override
    def close(self):
        """ 终止会话 """
        if self.session:
            self.session.end_session()
            self.session = None
        else:
            raise OperationFailure(_('no session to close'))

    @property
    def session(self):
        """ session getter """
        return self.session

    @session.setter
    def session(self, session):
        """ session setter """
        self._session = session


