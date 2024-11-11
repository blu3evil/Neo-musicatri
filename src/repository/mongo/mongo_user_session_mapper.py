from datetime import datetime
from typing import List

from typing_extensions import override

from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database

from modo.entity.session_entity import UserSessionEntity
from repository.abs.user_session_mapper import UserSessionMapper
from repository.mongo.mongo_entity_adaptor import MongodbEntityAdaptor
from repository.mongo.mongo_transaction_manager import TransactionManagerMongoImpl

# noinspection PyShadowingBuiltins
class UserSessionMapperImpl(UserSessionMapper):
    """ 用户JWT认证会话相关映射器，主要处理应用程序的登录认证逻辑 """
    def __init__(self, database: Database, transaction_manager: TransactionManagerMongoImpl, table_name: str = 'user_sessions'):  # 初始化数据库表
        self.table: Collection = database[table_name]
        self.tm = transaction_manager

    @override
    def insert(self, record: UserSessionEntity) -> bool:
        """ 插入一条jwt token认证会话数据，返回值标识是否插入成功 """
        record.updated_at = datetime.now()  # 设置时间相关字段
        record.created_at = datetime.now()
        document = MongodbEntityAdaptor.serialize(record)
        result = self.table.insert_one(document, session=self.tm.session)
        return result.acknowledged

    @override
    def select_by_id(self, id: int) -> UserSessionEntity:
        """ 根据id会话数据，返回jwt查询结果，若id不存在返回None """
        document = self.table.find_one({'_id': id})
        return MongodbEntityAdaptor.deserialize(document, UserSessionEntity)

    @override
    def select_by_user_id(self, user_id: int) -> UserSessionEntity:
        """ 根据用户id查询(这里是discord用户id)查询jwt会话数据，获取会话详情信息 """
        document = self.table.find_one({'user_id': user_id})
        return MongodbEntityAdaptor.deserialize(document, UserSessionEntity)

    @override
    def select_by_condition(self, condition: UserSessionEntity) -> List[UserSessionEntity]:
        """ 根据给定条件查询 """
        query = {}  # 查询条件
        if condition.id: query['_id'] = condition.id
        if condition.user_id: query['user_id'] = condition.user_id
        if condition.device_id: query['device_id'] = condition.device_id
        if condition.access_token: query['access_token'] = condition.access_token
        if condition.is_active: query['is_active'] = condition.is_active
        documents = self.table.find(query)
        records = []
        for document in documents:
            record = MongodbEntityAdaptor.deserialize(document, UserSessionEntity)
            records.append(record)
        return records

    @override
    def delete_by_condition(self, condition: UserSessionEntity) -> int:
        query = {}  # 查询条件
        if condition.id: query['id'] = condition.id
        if condition.user_id: query['user_id'] = condition.user_id
        if condition.device_id: query['device_id'] = condition.device_id
        if condition.access_token: query['access_token'] = condition.access_token
        if condition.is_active: query['is_active'] = condition.is_active
        result = self.table.delete_many(query, session=self.tm.session)
        return result.deleted_count  # 返回被删除文档数量

    @override
    def delete_by_ids(self, ids: List[int]) -> int:
        if not ids: return 0  # 给定空数组不执行删除
        result = self.table.delete_many(
            {'_id': {'$in': ids}},
            session=self.tm.session
        )  # 根据给定id数组执行删除
        return result.deleted_count


    @override
    def select_all(self) -> List[UserSessionEntity]:
        """ 查询所有存储的用户jwt认证信息对象 """
        documents = self.table.find()
        records = []
        for document in documents:
            record = MongodbEntityAdaptor.deserialize(document, UserSessionEntity)
            records.append(record)
        return records

    @override
    def update(self, record: UserSessionEntity) -> bool:
        """ 全量更新，将传入的数据用于更新记录，数据不存在也不会创建新数据 """
        result = self.table.update_one(
            {'_id': record.id},
            {'$set': {k: v for k, v in MongodbEntityAdaptor.serialize(record).items() if k != '_id' and v is not None and v != ''}},
            session=self.tm.session
        )
        return result.matched_count != 0

    @override
    def delete_by_id(self, id: int) -> bool:
        """ 根据传入的id删除指定jwt会话记录 """
        result = self.table.delete_one({'_id': id}, session=self.tm.session)
        return result.deleted_count > 0

    @override
    def delete_by_user_id(self, user_id: int) -> bool:
        """ 根据传入的用户id删除此用户关联的jwt会话记录 """
        result = self.table.delete_one({'user_id': user_id}, session=self.tm.session)
        return result.deleted_count > 0
