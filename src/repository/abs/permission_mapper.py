"""
权限管理相关mapper
"""

from __future__ import annotations

from abc import abstractmethod
from typing import List

from domain.entity.permission_entity import PermissionEntity
from repository.abs.base_mapper import BaseMapper
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


