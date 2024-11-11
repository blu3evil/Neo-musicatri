from __future__ import annotations

from abc import abstractmethod
from typing import List

from modo.entity.permission_entity import UserPermissionEntity
from repository.abs.base_mapper import BaseMapper


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
