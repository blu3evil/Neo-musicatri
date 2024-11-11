from typing import List

from typing_extensions import override

from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database

from modo.entity.permission_entity import UserPermissionEntity
from repository.abs.user_permission_mapper import UserPermissionMapper
from repository.mongo.mongo_entity_adaptor import MongodbEntityAdaptor
from repository.mongo.mongo_transaction_manager import TransactionManagerMongoImpl

# noinspection PyShadowingBuiltins
class UserPermissionMapperImpl(UserPermissionMapper):
    def __init__(self, database: Database, transaction_manager: TransactionManagerMongoImpl, table_name: str = 'user_permissions'):  # 初始化数据库表
        self.table: Collection = database[table_name]
        self.tm = transaction_manager

    """ 用户权限等级映射，记录用户的权限等级 """
    @override
    def insert(self, record: UserPermissionEntity) -> bool:
        """ 插入一条用户id到用户权限的映射，返回值标识是否插入成功 """
        document = MongodbEntityAdaptor.serialize(record)
        return self.table.insert_one(document, session=self.tm.session).acknowledged

    @override
    def select_by_id(self, id: int) -> UserPermissionEntity:
        """ 根据id查询对应的userid对应的权限状态，若无查询结果返回None """
        document = self.table.find_one({'_id': id})
        return MongodbEntityAdaptor.deserialize(document, UserPermissionEntity)

    @override
    def select_by_user_id(self, user_id: int) -> UserPermissionEntity:
        """ 根据用户id查询(这里是discord用户id)查询用户对应的权限等级 """
        document = self.table.find_one({'user_id': user_id})
        return MongodbEntityAdaptor.deserialize(document, UserPermissionEntity)

    @override
    def select_all(self) -> List[UserPermissionEntity]:
        """ 查询所有用户和权限等级的映射关系 """
        documents = self.table.find()
        records = []
        for document in documents:
            record = MongodbEntityAdaptor.deserialize(document, UserPermissionEntity)
            records.append(record)
        return records

    @override
    def update(self, record: UserPermissionEntity) -> bool:
        """ 全量更新，用于更新用户的权限等级 """
        result = self.table.update_one(
            {'_id': record.id},
            {'$set': {k: v for k, v in MongodbEntityAdaptor.serialize(record).items() if k != '_id' and v is not None and v != ''}},
            session=self.tm.session
        )
        return result.matched_count != 0

    @override
    def delete_by_id(self, id: int) -> bool:
        """ 通过记录id删除某一条用户id到权限等级的映射 """
        result = self.table.delete_one({'_id': id}, session=self.tm.session)
        return result.deleted_count > 0

    @override
    def delete_by_user_id(self, user_id: int) -> bool:
        """ 根据用户id删除此用户到权限等级的映射 """
        result = self.table.delete_one({'user_id': user_id}, session=self.tm.session)
        return result.deleted_count > 0
