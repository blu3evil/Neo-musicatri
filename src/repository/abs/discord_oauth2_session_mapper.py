from __future__ import annotations

from abc import abstractmethod
from typing import List

from domain.entity.session_entity import DiscordOAuth2SessionEntity
from repository.abs.base_mapper import BaseMapper


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
