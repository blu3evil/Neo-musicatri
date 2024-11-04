"""
权限管理相关mapper
"""

from __future__ import annotations

from abc import abstractmethod
from typing import List

from domain.entity.permission_entity import PermissionEntity, UserPermissionEntity
from repository.mapper.base_mapper import BaseMapper
# 默认权限等级


# noinspection PyShadowingBuiltins
class PermissionMapper(BaseMapper):
    """ 权限等级详情映射器，通过权限等级id查询权限等级详细说明 """
    @abstractmethod
    def insert(self, record: PermissionEntity) -> bool:
        """ 插入权限等级详情记录，返回值标识是否插入成功 """
        pass

    @abstractmethod
    def insert_batch(self, records: List[PermissionEntity]) -> int:
        """ 插入多条数据 """
        pass

    @abstractmethod
    def select_by_id(self, id: int) -> PermissionEntity:
        """ 根据id查询某一条权限等级详情信息，若无查询结果返回None """
        pass

    @abstractmethod
    def select_all(self) -> List[PermissionEntity]:
        """ 查询所有可用的权限等级 """
        pass

    @abstractmethod
    def update(self, record: PermissionEntity) -> bool:
        """ 更新权限等级信息 """
        pass

    @abstractmethod
    def delete_by_id(self, id: int) -> bool:
        """ 通过id删除某一条权限等级 """
        pass

    @abstractmethod
    def delete_all(self) -> int:
        """ 删除全部数据 """
        pass

# noinspection PyShadowingBuiltins
class UserPermissionMapper(BaseMapper):
    """ 用户权限等级映射，记录用户的权限等级 """
    @abstractmethod
    def insert(self, record: UserPermissionEntity) -> bool:
        """ 插入一条用户id到用户权限的映射，返回值标识是否插入成功 """
        pass

    @abstractmethod
    def select_by_id(self, id: int) -> UserPermissionEntity:
        """ 根据id查询对应的userid对应的权限状态，若无查询结果返回None """
        pass

    @abstractmethod
    def select_by_user_id(self, user_id: int) -> UserPermissionEntity:
        """ 根据用户id查询(这里是discord用户id)查询用户对应的权限等级 """
        pass

    @abstractmethod
    def select_all(self) -> List[UserPermissionEntity]:
        """ 查询所有用户和权限等级的映射关系 """
        pass

    @abstractmethod
    def update(self, record: UserPermissionEntity) -> bool:
        """ 全量更新，用于更新用户的权限等级 """
        pass

    @abstractmethod
    def delete_by_id(self, id: int) -> bool:
        """ 通过记录id删除某一条用户id到权限等级的映射 """
        pass

    @abstractmethod
    def delete_by_user_id(self, user_id: int) -> bool:
        """ 根据用户id删除此用户到权限等级的映射 """
        pass
