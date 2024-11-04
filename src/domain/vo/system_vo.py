""" system接口视图对象 """
from datetime import datetime

from dataclasses import dataclass

from domain.base_domain import BaseVO


@dataclass
class SystemStatusVO(BaseVO):
    """ 服务器状态视图对象 """
    version: str = None             # 服务端版本号
    uptime: int = None              # 服务端存活时间
    created_at: datetime = None     # 服务端上线时间


@dataclass
class SystemConfigVO(BaseVO):
    """ 服务器配置项视图对象 """
    # 使用反射动态添加属性
    pass
