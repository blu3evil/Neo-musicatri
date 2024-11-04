from datetime import datetime
from typing import List

from typing_extensions import override

from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database

from domain.entity.session_entity import DiscordOAuth2SessionEntity, UserSessionEntity, SocketIOSessionEntity
from repository.mapper.session_mapper import DiscordOAuth2SessionMapper, UserSessionMapper, SocketIOSessionMapper
from repository.mongodb.mongodb_entity_adaptor import MongodbEntityAdaptor
from repository.transaction_manager import TransactionManager
from utils import log, default_locale as _

# noinspection PyShadowingBuiltins
class DiscordOAuth2SessionMapperImpl(DiscordOAuth2SessionMapper):
    """ discord oauth2认证信息映射器，存储用户的oauth2认证信息 """
    def __init__(self, database: Database, transaction_manager: TransactionManager, table_name: str = 'discord_oauth2_sessions'):  # 初始化数据库表
        self.table: Collection = database[table_name]
        self.transaction_manager = transaction_manager

    @override
    def insert(self, record: DiscordOAuth2SessionEntity) -> bool:
        """ 插入一条Discord OAuth2认证会话数据，返回值标识是否插入成功 """
        # 插入库表，设置时间相关字段
        record.created_at = datetime.now()
        record.updated_at = datetime.now()
        document = MongodbEntityAdaptor.serialize(record)
        return self.table.insert_one(document, session=self.transaction_manager.get_session()).acknowledged  # 响应是否添加成功

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
            log.error(_("discord oauth session mapper error: cannot inserting data %(data)s, 'id' is invalid")
                      % {'data': record.to_dict()})
            return False  # id不存在更新失败

        record.updated_at = datetime.now()  # 修改更新时间
        result = self.table.update_one(
            {'_id': record_id},  # 针对_id和记录id相同的数据执行更新操作
            {'$set': {k: v for k, v in MongodbEntityAdaptor.serialize(record).items() if k != '_id' and v is not None and v != ''}},
            # 仅在字段不为空的时候更新
            session=self.transaction_manager.get_session()
        )

        # 检查是否匹配到文档并且进行了修改
        return result.matched_count != 0  # 若成功匹配文档那么返回true

    @override
    def delete_by_id(self, id: int) -> bool:
        """ 根据传入的id删除指定记录 """
        result = self.table.delete_one({'_id': id}, session=self.transaction_manager.get_session())
        return result.deleted_count > 0  # 响应是否删除成功

    @override
    def delete_by_user_id(self, user_id: int) -> bool:
        """ 根据传入的用户id删除此用户关联的oauth2会话记录 """
        result = self.table.delete_one({'user_id': user_id}, session=self.transaction_manager.get_session())
        return result.deleted_count > 0

# noinspection PyShadowingBuiltins
class UserSessionMapperImpl(UserSessionMapper):
    """ 用户JWT认证会话相关映射器，主要处理应用程序的登录认证逻辑 """
    def __init__(self, database: Database, transaction_manager: TransactionManager, table_name: str = 'user_sessions'):  # 初始化数据库表
        self.table: Collection = database[table_name]
        self.transaction_manager = transaction_manager

    @override
    def insert(self, record: UserSessionEntity) -> bool:
        """ 插入一条jwt token认证会话数据，返回值标识是否插入成功 """
        record.updated_at = datetime.now()  # 设置时间相关字段
        record.created_at = datetime.now()
        document = MongodbEntityAdaptor.serialize(record)
        result = self.table.insert_one(document, session=self.transaction_manager.get_session())
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
        result = self.table.delete_many(query, session=self.transaction_manager.get_session())
        return result.deleted_count  # 返回被删除文档数量

    @override
    def delete_by_ids(self, ids: List[int]) -> int:
        if not ids: return 0  # 给定空数组不执行删除
        result = self.table.delete_many(
            {'_id': {'$in': ids}},
            session=self.transaction_manager.get_session()
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
            session=self.transaction_manager.get_session()
        )
        return result.matched_count != 0

    @override
    def delete_by_id(self, id: int) -> bool:
        """ 根据传入的id删除指定jwt会话记录 """
        result = self.table.delete_one({'_id': id}, session=self.transaction_manager.get_session())
        return result.deleted_count > 0

    @override
    def delete_by_user_id(self, user_id: int) -> bool:
        """ 根据传入的用户id删除此用户关联的jwt会话记录 """
        result = self.table.delete_one({'user_id': user_id}, session=self.transaction_manager.get_session())
        return result.deleted_count > 0

# noinspection PyShadowingBuiltins
class SocketIOSessionMapperImpl(SocketIOSessionMapper):
    def __init__(self, database: Database, transaction_manager: TransactionManager, table_name = 'socketio_sessions'):  # 初始化数据库表
        self.table: Collection = database[table_name]
        self.transaction_manager = transaction_manager

    """ 用户权限等级映射，记录用户的权限等级 """
    @override
    def insert(self, record: SocketIOSessionEntity) -> bool:
        """ 插入一条socketIO会话信息，通常在SocketIO连接建立之后 """
        record.created_at = datetime.now()
        record.updated_at = datetime.now()
        document = MongodbEntityAdaptor.serialize(record)
        result = self.table.insert_one(document, session=self.transaction_manager.get_session())
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
            session=self.transaction_manager.get_session()
        )
        return result.matched_count != 0

    @override
    def delete_by_id(self, id: int) -> bool:
        """ 通过记录id直接删除某一个用户的SocketIO连接信息 """
        result = self.table.delete_one({'_id': id}, session=self.transaction_manager.get_session())
        return result.deleted_count > 0

    @override
    def delete_by_user_id(self, user_id: int) -> bool:
        """ 根据用户ID删除用户的SocketIO连接信息 """
        result = self.table.delete_one({'user_id': user_id}, session=self.transaction_manager.get_session())
        return result.deleted_count > 0
