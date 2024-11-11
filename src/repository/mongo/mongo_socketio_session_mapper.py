from datetime import datetime
from typing import List

from typing_extensions import override

from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database

from modo.entity.session_entity import SocketIOSessionEntity
from repository.abs.socketio_session_mapper import SocketIOSessionMapper
from repository.mongo.mongo_entity_adaptor import MongodbEntityAdaptor
from repository.mongo.mongo_transaction_manager import TransactionManagerMongoImpl

# noinspection PyShadowingBuiltins
class SocketIOSessionMapperImpl(SocketIOSessionMapper):
    def __init__(self, database: Database, transaction_manager: TransactionManagerMongoImpl, table_name = 'socketio_sessions'):  # 初始化数据库表
        self.table: Collection = database[table_name]
        self.tm = transaction_manager

    """ 用户权限等级映射，记录用户的权限等级 """
    @override
    def insert(self, record: SocketIOSessionEntity) -> bool:
        """ 插入一条socketIO会话信息，通常在SocketIO连接建立之后 """
        record.created_at = datetime.now()
        record.updated_at = datetime.now()
        document = MongodbEntityAdaptor.serialize(record)
        result = self.table.insert_one(document, session=self.tm.session)
        return result.acknowledged

    @override
    def select_by_id(self, id: int) -> SocketIOSessionEntity:
        """ 通过记录id查询的到对应的UserSocketIOEntity对象 """
        document = self.table.find_one({'_id': id})
        return MongodbEntityAdaptor.deserialize(document, SocketIOSessionEntity)

    @override
    def select_by_user_id(self, user_id: int) -> SocketIOSessionEntity:
        """ 根据用户id查询(这里是discord用户id)查询用户对应地SocketIO连接信息 """
        document = self.table.find_one({'user_id': user_id})
        return MongodbEntityAdaptor.deserialize(document, SocketIOSessionEntity)

    @override
    def select_all(self) -> List[SocketIOSessionEntity]:
        """ 查询所有的SocketIO连接会话记录 """
        documents = self.table.find()
        records = []
        for document in documents:
            record = MongodbEntityAdaptor.deserialize(document, SocketIOSessionEntity)
            records.append(record)
        return records

    @override
    def update(self, record: SocketIOSessionEntity) -> bool:
        """ 全量更新，用于更新用户的SocketIO连接信息 """
        result = self.table.update_one(
            {'_id': record.id},
            {'$set': {k: v for k, v in MongodbEntityAdaptor.serialize(record).items() if k != '_id' and v is not None and v != ''}},
            session=self.tm.session
        )
        return result.matched_count != 0

    @override
    def delete_by_id(self, id: int) -> bool:
        """ 通过记录id直接删除某一个用户的SocketIO连接信息 """
        result = self.table.delete_one({'_id': id}, session=self.tm.session)
        return result.deleted_count > 0

    @override
    def delete_by_user_id(self, user_id: int) -> bool:
        """ 根据用户ID删除用户的SocketIO连接信息 """
        result = self.table.delete_one({'user_id': user_id}, session=self.tm.session)
        return result.deleted_count > 0
