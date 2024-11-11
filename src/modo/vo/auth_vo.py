""" 认证vo """

from dataclasses import dataclass

from modo.base_domain import BaseVO


@dataclass
class CredentialVO(BaseVO):
    """ 认证结果 """
    access_token: str = None        # access token
    expires_in: int = None          # access token过期时间


@dataclass
class AccessTokenVO(BaseVO):
    """ 认证结果vo，仅仅包含jwt和jwt expires in，不包含refresh token """
    access_token: str = None        # access token
    expires_in: int = None          # access token过期时间