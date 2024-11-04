from dataclasses import dataclass
from datetime import datetime

from domain.base_domain import BaseEntity

# noinspection PyShadowingBuiltins
@dataclass
class UserPermissionEntity(BaseEntity):
    """ 用户权限实体类，保存用户的权限信息 """
    id: int = None,  # 数据id，推荐使用雪花算法生成
    user_id: int = None,  # 外键，关联DiscordUserInfo表，标识此会话属于哪一个用户
    permission_id: int = None  # 外键，关联到权限表

# noinspection PyShadowingBuiltins
@dataclass
class PermissionEntity(BaseEntity):
    """ 权限等级实体类，保存权限类的信息，用于用户权限校验 """
    id: int = None   # 权限id，推荐使用雪花算法生成
    name: str = None   # 权限名称
    rank: int = None   # 权限等级
    description: str = None   # 权限描述信息
    created_at: datetime = None   # 权限等级创建时间
    updated_at: datetime = None  # 权限等级最后修改时间

    def __eq__(self, other):  # 重写equals
        if not isinstance(other, type(self)):
            return NotImplemented
        return (
            self.id == other.id
            and self.name == other.name
            and self.rank == other.rank
            and self.description == other.description
        )

    def __hash__(self):  # 重写hash
        return hash((self.id, self.name, self.rank, self.description))



