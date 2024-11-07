from datetime import datetime
from typing import List

from typing_extensions import override

from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database

from domain.entity.permission_entity import PermissionEntity
from repository.abs.permission_mapper import PermissionMapper
from repository.mongo.mongo_entity_adaptor import MongodbEntityAdaptor
from repository.mongo.mongo_transaction_manager import TransactionManagerMongoImpl


# noinspection PyShadowingBuiltins
class PermissionMapperMongoImpl(PermissionMapper):
    """ 权限等级详情映射器，通过权限等级id查询权限等级详细说明 """
    def __init__(self, database: Database, transaction_manager: TransactionManagerMongoImpl, table_name: str = 'permissions'):  # 初始化数据库表
        self.table: Collection = database[table_name]
        self.tm = transaction_manager

    @override
    def insert(self, record: PermissionEntity) -> bool:
        """ 插入权限等级详情记录，返回值标识是否插入成功 """
        record.created_at = datetime.now()  # 设置时间相关字段
        record.updated_at = datetime.now()
        document = MongodbEntityAdaptor.serialize(record)
        return self.table.insert_one(document, session=self.tm.session).acknowledged

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
        return len(self.table.insert_many(documents, session=self.tm.session).inserted_ids)

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
            session=self.tm.session
        )
        return result.matched_count != 0

    @override
    def delete_by_id(self, id: int) -> bool:
        """ 通过id删除某一条权限等级 """
        result = self.table.delete_one({'_id': id}, session=self.tm.session)
        return result.deleted_count > 0

    @override
    def delete_all(self) -> int:
        """ 删除所有数据 """
        result = self.table.delete_many({}, session=self.tm.session)
        return result.deleted_count


