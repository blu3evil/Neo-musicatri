from __future__ import annotations

from abc import abstractmethod
from enum import Enum

from domain.entity.permission_entity import PermissionEntity


class PermissionService:
    # 权限相关接口
    """ 安全校验业务层接口 """
    @abstractmethod
    def verify_user_permission(self, user_id: int, permission: PermissionEntity) -> bool:
        """
        通过用户id检索用户权限等级，设定检查权限等级，若用户权限等级大于等于此
        等级，那么返回true，如果低于给定的权限等级，返回false

        * 注: 若用户数据不存在，则将用户视为GUEST级别，拥有GUEST级别数值的rank
        """
        pass

    @abstractmethod
    def upsert_user_permission(self, user_id: int, permission: PermissionEntity) -> bool:
        """
        更新用户的权限等级，若用户权限记录不存在，那么创建权限记录，如果权限记录已经存在
        则之间更新旧数据
        """
        pass

    @abstractmethod
    def get_user_permission(self, user_id: int) -> PermissionEntity:
        """ 获取用户的权限等级，如果用户不存在，那么会返回GUEST用户等级 """
        pass


class PermissionTag(Enum):
    """ 默认权限等级枚举 """
    ADMIN = PermissionEntity(id=0, name="admin", rank=10, description="Administrator access")  # 管理员
    GUEST = PermissionEntity(id=1, name="guest", rank=0, description="Guest access")  # 未注册用户
    USER = PermissionEntity(id=2, name="user", rank=1, description="User access")  # 普通用户
    PREMIUM = PermissionEntity(id=3, name="premium", rank=2, description="Premium access")  # 高级用户
    BLOCKED = PermissionEntity(id=4, name="blocked", rank=-1, description="Blocked access")  # 封禁用户

    def rank(self):
        return self.value.rank

    def description(self):
        return self.value.description

    def name(self):
        return self.value.name
