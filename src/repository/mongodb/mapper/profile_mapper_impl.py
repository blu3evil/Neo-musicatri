from datetime import datetime
from typing import List

from typing_extensions import override

from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database

from domain.entity.profile_entity import DiscordUserEntity
from repository.mapper.profile_mapper import DiscordUserMapper
from repository.mongodb.mongodb_entity_adaptor import MongodbEntityAdaptor
from repository.transaction_manager import TransactionManager
from utils import log, default_locale as _

# noinspection PyShadowingBuiltins
class DiscordUserMapperImpl(DiscordUserMapper):
    """ discord用户信息映射器抽象类，存储Discord用户信息 """
    def __init__(self, database: Database, transaction_manager: TransactionManager, table_name: str = 'discord_users'):  # 初始化数据库表
        self.table: Collection = database[table_name]
        self.transaction_manager = transaction_manager

    @override
    def insert(self, record: DiscordUserEntity) -> bool:
        """ 插入一条用户数据，返回值标识是否插入成功 """
        record.created_at = datetime.now()  # 设置时间相关字段
        record.updated_at = datetime.now()
        document = MongodbEntityAdaptor.serialize(record)  # 适配到mongodb格式
        return self.table.insert_one(document, session=self.transaction_manager.get_session()).acknowledged  # 插入数据

    @override
    def insert_batch(self, records: List[DiscordUserEntity]) -> int:
        """ 单次插入多条用户数据，返回值标识成功插入的数据条数 """
        documents = []
        for record in records:
            record.created_at = datetime.now()  # 设置时间相关字段
            record.updated_at = datetime.now()
            document = MongodbEntityAdaptor.serialize(record)  # 适配到mongodb格式
            documents.append(document)
        return len(self.table.insert_many(documents, session=self.transaction_manager.get_session()).inserted_ids)  # 多条插入

    @override
    def select_by_id(self, id: int) -> DiscordUserEntity:
        """ 根据id查询用户信息，返回查询结果，若id不存在返回None """
        return self.table.find_one({'_id': id})  # 使用_id查询

    @override
    def select_all(self) -> List[DiscordUserEntity]:
        """ 查询所有DiscordUserInfo对象 """
        records = []
        documents = self.table.find()  # 查询所有
        for document in documents:
            record = MongodbEntityAdaptor.deserialize(document, DiscordUserEntity)
            records.append(record)
        return records


    # @abstractmethod
    # def count(self) -> int:
    #     """ 查询用户数量 """
    #     pass

    @override
    def update(self, record: DiscordUserEntity) -> bool:
        """ 全量更新，将传入的数据用于更新记录，数据不存在也不会创建新数据 """
        record_id = record.id

        # 检查 _id 是否存在
        if record_id is None or record_id == '':
            log.error(_("discord user mapper error: cannot inserting data %(data)s, 'id' is invalid")
                      % {'data': record.to_dict()})
            return False  # id不存在更新失败

        record.updated_at = datetime.now()  # 修改更新时间
        result = self.table.update_one(
            {'_id': record_id},  # 针对_id和记录id相同的数据执行更新操作
            {'$set': {k: v for k, v in MongodbEntityAdaptor.serialize(record).items() if k != '_id' and v is not None and v != ''}},
            # 仅在字段不为空的时候更新
            session=self.transaction_manager.get_session()  # 设置会话
        )

        # 检查是否匹配到文档并且进行了修改
        return result.matched_count != 0  # 成功匹配文档则返回true

    @override
    def delete_by_id(self, id: int) -> bool:
        """ 根据传入的id删除指定记录 """
        result = self.table.delete_one({'_id': id}, session=self.transaction_manager.get_session())
        return result.deleted_count > 0
