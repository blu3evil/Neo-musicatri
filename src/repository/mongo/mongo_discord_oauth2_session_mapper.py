from datetime import datetime
from typing import List

from typing_extensions import override

from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database

from domain.entity.session_entity import DiscordOAuth2SessionEntity
from repository.abs.discord_oauth2_session_mapper import DiscordOAuth2SessionMapper
from repository.mongo.mongo_entity_adaptor import MongodbEntityAdaptor
from repository.mongo.mongo_transaction_manager import TransactionManagerMongoImpl
from utils import log, default_locale as _

# noinspection PyShadowingBuiltins
class DiscordOAuth2SessionMapperMongoImpl(DiscordOAuth2SessionMapper):
    """ discord oauth2认证信息映射器，存储用户的oauth2认证信息 """
    def __init__(self, database: Database, transaction_manager: TransactionManagerMongoImpl, table_name: str = 'discord_oauth2_sessions'):  # 初始化数据库表
        self.table: Collection = database[table_name]
        self.tm = transaction_manager

    @override
    def insert(self, record: DiscordOAuth2SessionEntity) -> bool:
        """ 插入一条Discord OAuth2认证会话数据，返回值标识是否插入成功 """
        # 插入库表，设置时间相关字段
        record.created_at = datetime.now()
        record.updated_at = datetime.now()
        document = MongodbEntityAdaptor.serialize(record)
        return self.table.insert_one(document, session=self.tm.session).acknowledged  # 响应是否添加成功

    @override
    def select_by_id(self, id: int) -> DiscordOAuth2SessionEntity:
        """ 根据id会话数据，返回查询结果，若id不存在返回None """
        document = self.table.find_one({'_id': id})
        return MongodbEntityAdaptor.deserialize(document, DiscordOAuth2SessionEntity)

    @override
    def select_by_user_id(self, user_id: int) -> DiscordOAuth2SessionEntity:
        """ 根据用户id查询(这里是discord用户id)查询会话数据，获取会话详情信息 """
        document = self.table.find_one({'user_id': user_id})  # 根据用户id执行查询
        return MongodbEntityAdaptor.deserialize(document, DiscordOAuth2SessionEntity)

    @override
    def select_all(self) -> List[DiscordOAuth2SessionEntity]:
        """ 查询所有存储的Discord OAuth2认证信息对象 """
        documents = self.table.find()
        records = []
        for document in documents:
            record = MongodbEntityAdaptor.deserialize(document, DiscordOAuth2SessionEntity)
            records.append(record)
        return records  # 返回结果

    @override
    def update(self, record: DiscordOAuth2SessionEntity) -> bool:
        """ 全量更新，将传入的数据用于更新记录，数据不存在也不会创建新数据 """
        """ 全量更新，将传入的数据用于更新记录，数据不存在也不会创建新数据 """
        record_id = record.id

        # 检查 _id 是否存在
        if record_id is None or record_id == '':
            log.error(_("discord oauth session abs error: cannot inserting data %(data)s, 'id' is invalid")
                      % {'data': record.to_dict()})
            return False  # id不存在更新失败

        record.updated_at = datetime.now()  # 修改更新时间
        result = self.table.update_one(
            {'_id': record_id},  # 针对_id和记录id相同的数据执行更新操作
            {'$set': {k: v for k, v in MongodbEntityAdaptor.serialize(record).items() if k != '_id' and v is not None and v != ''}},
            # 仅在字段不为空的时候更新
            session=self.tm.session
        )

        # 检查是否匹配到文档并且进行了修改
        return result.matched_count != 0  # 若成功匹配文档那么返回true

    @override
    def delete_by_id(self, id: int) -> bool:
        """ 根据传入的id删除指定记录 """
        result = self.table.delete_one({'_id': id}, session=self.tm.session)
        return result.deleted_count > 0  # 响应是否删除成功

    @override
    def delete_by_user_id(self, user_id: int) -> bool:
        """ 根据传入的用户id删除此用户关联的oauth2会话记录 """
        result = self.table.delete_one({'user_id': user_id}, session=self.tm.session)
        return result.deleted_count > 0


