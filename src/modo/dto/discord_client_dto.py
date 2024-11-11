"""
discord_client_dto请求得到的响应dto
"""
from dataclasses import dataclass

from modo.base_domain import BaseDTO
@dataclass
class DiscordOAuth2CredentialDTO(BaseDTO):
    """ 请求discord oauth2接口获得的响应对象，包含access token等用户认证信息 """
    token_type: str = None  # token类型
    access_token: str = None  # access token
    expires_in: int = None  # 过期时间
    refresh_token: str = None  # refresh token
    scope: str = None  # access token权限范围


@dataclass
class DiscordUserDTO(BaseDTO):
    """ 通过discord client发送http到/user/@me请求获得的响应数据 """
    id: int = None                          # 数据id，在这里就是discord用户id
    username: str = None                    # discord用户名
    avatar: str = None                      # discord用户头像，可通过一定权限的access token获取用户头像
    discriminator: str = None               # 与username一同区别用户，例如username#1234，1234为用户的discriminator
    public_flags: int = None                # 公共标志，标识状态或身份特征
    flags: int = None                       # 标识用户的各种状态或特征
    banner: str = None                      # 用户自定义的横幅图片的 ID，可用于获取用户横幅图像
    accent_color: str = None                # 用户自定义的强调颜色
    global_name: str = None                 # 用户全局名称，即用户在所有服务器的统一名称
    avatar_decoration_data: str = None      # 用户头像装饰的JSON数据，例如特殊效果、额外图层
    banner_color: str = None                # 用户自定义的横幅颜色
    clan: str = None                        # 用户所属clan信息，可以表示用户在的顶游戏的团队或者组织
    mfa_enabled: bool = None                # 用户是否启用多因素身份验证(MFA)，启用时用户账号安全等级较高
    locale: str = None                      # 用户使用的语言种类
    premium_type: int = None                # 用户是否为高级订阅类型: 1.非高级用户 2.Nitro Classic用户 3.Nitro用户
