from typing import List
from typing_extensions import override

from repository.transaction_manager import TransactionManager
from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database
from datetime import datetime

from domain.entity.permission_entity import PermissionEntity, UserPermissionEntity
from repository.mapper.permission_mapper import PermissionMapper, UserPermissionMapper
from repository.mongodb.mongodb_entity_adaptor import MongodbEntityAdaptor

# noinspection PyShadowingBuiltins
class PermissionMapperImpl(PermissionMapper):
    """ 权限等级详情映射器，通过权限等级id查询权限等级详细说明 """
    def __init__(self, database: Database, transaction_manager: TransactionManager, table_name: str = 'permissions'):  # 初始化数据库表
        self.table: Collection = database[table_name]
        self.transaction_manager = transaction_manager

    @override
    def insert(self, record: PermissionEntity) -> bool:
        """ 插入权限等级详情记录，返回值标识是否插入成功 """
        record.created_at = datetime.now()  # 设置时间相关字段
        record.updated_at = datetime.now()
        document = MongodbEntityAdaptor.serialize(record)
        return self.table.insert_one(document, session=self.transaction_manager.get_session()).acknowledged

    @override
    def insert_batch(self, records: List[PermissionEntity]) -> int:
        """ 插入多条permission数据 """
        documents = []  # 重置id字段为_id，适配为mongodb格式
        for record in records:
            record.created_at = datetime.now()  # 设置时间相关字段
            record.updated_at = datetime.now()
            document = MongodbEntityAdaptor.serialize(record)
            documents.append(document)  # 将格式化之后的数据添加到documents
        # 执行多条插入
        return len(self.table.insert_many(documents, session=self.transaction_manager.get_session()).inserted_ids)

    @override
    def select_by_id(self, id: int) -> PermissionEntity:
        """ 根据id查询某一条权限等级详情信息，若无查询结果返回None """
        document = self.table.find_one({'_id': id})  # 通过id执行查询
        return MongodbEntityAdaptor.deserialize(document, PermissionEntity)

    # todo: permission mapper未实现函数
    @override
    def select_all(self) -> List[PermissionEntity]:
        """ 查询所有可用的权限等级 """
        documents = self.table.find()  # 查询所有
        records = []
        for document in documents:
            record = MongodbEntityAdaptor.deserialize(document, PermissionEntity)
            records.append(record)
        return records

    @override
    def update(self, record: PermissionEntity) -> bool:
        """ 更新权限等级信息 """
        result = self.table.update_one(
            {'_id': record.id},
            {'$set': {k: v for k, v in MongodbEntityAdaptor.serialize(record).items() if k != '_id' and v is not None and v != ''}},
            session=self.transaction_manager.get_session()
        )
        return result.matched_count != 0

    @override
    def delete_by_id(self, id: int) -> bool:
        """ 通过id删除某一条权限等级 """
        result = self.table.delete_one({'_id': id}, session=self.transaction_manager.get_session())
        return result.deleted_count > 0

    @override
    def delete_all(self) -> int:
        """ 删除所有数据 """
        result = self.table.delete_many({}, session=self.transaction_manager.get_session())
        return result.deleted_count

# noinspection PyShadowingBuiltins
class UserPermissionMapperImpl(UserPermissionMapper):
    def __init__(self, database: Database, transaction_manager: TransactionManager, table_name: str = 'user_permissions'):  # 初始化数据库表
        self.table: Collection = database[table_name]
        self.transaction_manager = transaction_manager

    """ 用户权限等级映射，记录用户的权限等级 """
    @override
    def insert(self, record: UserPermissionEntity) -> bool:
        """ 插入一条用户id到用户权限的映射，返回值标识是否插入成功 """
        document = MongodbEntityAdaptor.serialize(record)
        return self.table.insert_one(document, session=self.transaction_manager.get_session()).acknowledged

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
            session=self.transaction_manager.get_session()
        )
        return result.matched_count != 0

    @override
    def delete_by_id(self, id: int) -> bool:
        """ 通过记录id删除某一条用户id到权限等级的映射 """
        result = self.table.delete_one({'_id': id}, session=self.transaction_manager.get_session())
        return result.deleted_count > 0

    @override
    def delete_by_user_id(self, user_id: int) -> bool:
        """ 根据用户id删除此用户到权限等级的映射 """
        result = self.table.delete_one({'user_id': user_id}, session=self.transaction_manager.get_session())
        return result.deleted_count > 0
