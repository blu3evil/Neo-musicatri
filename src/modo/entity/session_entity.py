from dataclasses import dataclass
from datetime import datetime

from modo.base_domain import BaseEntity


# noinspection PyShadowingBuiltins
@dataclass
class DiscordOAuth2SessionEntity(BaseEntity):
    """
    discord oauth2认证会话实体类，存储用户id到access token之间的关联，当涉及到请求用户信息的时候可以通过此表
    查询用户的access token从而获取访问权限，同时需要检查access token的过期时间
    """
    id: int = None                  # 数据id，推荐使用雪花算法生成
    user_id: int = None             # 外键，关联DiscordUserInfo表，标识此会话属于哪一个用户
    access_token: str = None        # 用户授权discord账号之后生成的access token
    expires_in: int = None          # access token的有效期
    refresh_token: str = None       # 用于刷新access token的有效期
    scope: str = None               # 此access token的授权范围
    token_type: str = None          # 认证token的类型，通常为Bearer
    created_at: datetime = None     # 记录的创建时间
    updated_at: datetime = None     # 记录最后更新时间
    expires_at: datetime = None     # access token的过期时间


# noinspection PyShadowingBuiltins
@dataclass
class UserSessionEntity(BaseEntity):
    """ 用户JWT认证实体类，存储用户的jwt信息，保存jwt的过期时间 """
    id: int = None                          # 数据id，推荐使用雪花算法生成
    user_id: int = None                     # 外键，关联DiscordUserInfo表，标识此会话属于哪一个用户
    access_token: str = None                # access_token
    device_id: str = None                   # 设备id号，用于区分多浏览器或设备
    created_at: datetime = None             # 记录的创建时间
    updated_at: datetime = None             # 记录最后更新时间
    expires_at: datetime = None             # jwt的过期时间，通常jwt有效期较短，例如15分钟
    is_active: bool = None                  # 记录状态，标识此连接是否仍然有效，可用于踢出用户


# noinspection PyShadowingBuiltins
@dataclass
class SocketIOSessionEntity(BaseEntity):
    """ 客户端建立Socketio连接之后生成的会话实体类，使sid(socketio id)与某个具体的用户id建立关联 """
    id: int = None                  # 数据id，推荐使用雪花算法生成
    user_id: int = None             # 外键，关联DiscordUserInfo表，标识此会话属于哪一个用户
    sid: str = None                 # SocketIO连接建立后生成的会话id
    created_at: datetime = None     # 记录的创建时间
    updated_at: datetime = None     # 记录最后更新时间
