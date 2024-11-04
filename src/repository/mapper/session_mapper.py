"""
会话管理相关mapper
"""

from __future__ import annotations

from abc import abstractmethod
from typing import List

from domain.entity.session_entity import UserSessionEntity, SocketIOSessionEntity, DiscordOAuth2SessionEntity
from repository.mapper.base_mapper import BaseMapper


# noinspection PyShadowingBuiltins
class UserSessionMapper(BaseMapper):
    """ 用户JWT认证会话相关映射器，主要处理应用程序的登录认证逻辑 """
    @abstractmethod
    def insert(self, record: UserSessionEntity) -> bool:
        """ 插入一条jwt token认证会话数据，返回值标识是否插入成功 """
        pass

    @abstractmethod
    def select_by_id(self, id: int) -> UserSessionEntity:
        """ 根据id会话数据，返回jwt查询结果，若id不存在返回None """
        pass

    @abstractmethod
    def select_by_user_id(self, user_id: int) -> UserSessionEntity:
        """ 根据用户id查询(这里是discord用户id)查询jwt会话数据，获取会话详情信息 """
        pass

    @abstractmethod
    def select_by_condition(self, condition: UserSessionEntity) -> List[UserSessionEntity]:
        """ 根据条件查询用户下的会话信息 """
        pass

    @abstractmethod
    def delete_by_condition(self, condition: UserSessionEntity) -> int:
        """ 根据条件删除 """
        pass

    @abstractmethod
    def delete_by_ids(self, ids: List[int]) -> int:
        """ 使用id集合执行多条删除 """
        pass

    @abstractmethod
    def select_all(self) -> List[UserSessionEntity]:
        """ 查询所有存储的用户jwt认证信息对象 """
        pass

    @abstractmethod
    def update(self, record: UserSessionEntity) -> bool:
        """ 全量更新，将传入的数据用于更新记录，数据不存在也不会创建新数据 """
        pass

    @abstractmethod
    def delete_by_id(self, id: int) -> bool:
        """ 根据传入的id删除指定jwt会话记录 """
        pass

    @abstractmethod
    def delete_by_user_id(self, user_id: int) -> bool:
        """ 根据传入的用户id删除此用户关联的jwt会话记录 """
        pass


# noinspection PyShadowingBuiltins
class SocketIOSessionMapper(BaseMapper):
    """ 用户权限等级映射，记录用户的权限等级 """
    @abstractmethod
    def insert(self, record: SocketIOSessionEntity) -> bool:
        """ 插入一条socketIO会话信息，通常在SocketIO连接建立之后 """
        pass

    @abstractmethod
    def select_by_id(self, id: int) -> SocketIOSessionEntity:
        """ 通过记录id查询的到对应的UserSocketIOEntity对象 """
        pass

    @abstractmethod
    def select_by_user_id(self, user_id: int) -> SocketIOSessionEntity:
        """ 根据用户id查询(这里是discord用户id)查询用户对应地SocketIO连接信息 """
        pass

    @abstractmethod
    def select_all(self) -> List[SocketIOSessionEntity]:
        """ 查询所有的SocketIO连接会话记录 """
        pass

    @abstractmethod
    def update(self, record: SocketIOSessionEntity) -> bool:
        """ 全量更新，用于更新用户的SocketIO连接信息 """
        pass

    @abstractmethod
    def delete_by_id(self, id: int) -> bool:
        """ 通过记录id直接删除某一个用户的SocketIO连接信息 """
        pass

    @abstractmethod
    def delete_by_user_id(self, user_id: int) -> bool:
        """ 根据用户ID删除用户的SocketIO连接信息 """
        pass


# noinspection PyShadowingBuiltins
class DiscordOAuth2SessionMapper(BaseMapper):
    """ discord oauth2认证信息映射器，存储用户的oauth2认证信息 """
    @abstractmethod
    def insert(self, record: DiscordOAuth2SessionEntity) -> bool:
        """ 插入一条Discord OAuth2认证会话数据，返回值标识是否插入成功 """
        pass

    @abstractmethod
    def select_by_id(self, id: int) -> DiscordOAuth2SessionEntity:
        """ 根据id会话数据，返回查询结果，若id不存在返回None """
        pass

    @abstractmethod
    def select_by_user_id(self, user_id: int) -> DiscordOAuth2SessionEntity:
        """ 根据用户id查询(这里是discord用户id)查询会话数据，获取会话详情信息 """
        pass

    @abstractmethod
    def select_all(self) -> List[DiscordOAuth2SessionEntity]:
        """ 查询所有存储的Discord OAuth2认证信息对象 """
        pass

    @abstractmethod
    def update(self, record: DiscordOAuth2SessionEntity) -> bool:
        """ 全量更新，将传入的数据用于更新记录，数据不存在也不会创建新数据 """
        pass

    @abstractmethod
    def delete_by_id(self, id: int) -> bool:
        """ 根据传入的id删除指定记录 """
        pass

    @abstractmethod
    def delete_by_user_id(self, user_id: int) -> bool:
        """ 根据传入的用户id删除此用户关联的oauth2会话记录 """
        pass
