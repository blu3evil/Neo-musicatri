from __future__ import annotations

from abc import abstractmethod
from typing import List

from modo.entity.session_entity import SocketIOSessionEntity
from repository.abs.base_mapper import BaseMapper

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
