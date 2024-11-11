from __future__ import annotations

from abc import abstractmethod
from typing import List

from modo.entity.profile_entity import DiscordUserEntity
from repository.abs.base_mapper import BaseMapper

# noinspection PyShadowingBuiltins
class DiscordUserMapper(BaseMapper):
    """ discord用户信息映射器抽象类，存储Discord用户信息 """
    @abstractmethod
    def insert(self, record: DiscordUserEntity) -> bool:
        """ 插入一条用户数据，返回值标识是否插入成功 """
        pass

    @abstractmethod
    def insert_batch(self, records: List[DiscordUserEntity]) -> int:
        """ 单次插入多条用户数据，返回值标识成功插入的数据条数 """
        pass

    @abstractmethod
    def select_by_id(self, id: int) -> DiscordUserEntity:
        """ 根据id查询用户信息，返回查询结果，若id不存在返回None """
        pass

    @abstractmethod
    def select_all(self) -> List[DiscordUserEntity]:
        """ 查询所有DiscordUserInfo对象 """
        pass

    # @abstractmethod
    # def count(self) -> int:
    #     """ 查询用户数量 """
    #     pass

    @abstractmethod
    def update(self, record: DiscordUserEntity) -> bool:
        """ 全量更新，将传入的数据用于更新记录，数据不存在也不会创建新数据 """
        pass

    @abstractmethod
    def delete_by_id(self, id: int) -> bool:
        """ 根据传入的id删除指定记录 """
        pass
