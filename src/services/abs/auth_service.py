"""
oauth授权业务层
"""
from __future__ import annotations

from abc import abstractmethod
from datetime import datetime, timedelta

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from config.exception_configuration import BusinessException
from modo.base_domain import BaseDomain
from modo.dto.session_dto import TokenPayloadDTO
from modo.vo.auth_vo import CredentialVO
from repository.abs.user_session_mapper import UserSessionMapper
from utils import HttpResult, default_config, DefaultConfigTag, HttpCode, default_locale as _


class AuthService:
    @abstractmethod
    def auth_code_authenticate(self) -> HttpResult[CredentialVO]:
        """
        discord授权码验证登录
        """
        pass

    @abstractmethod
    def access_token_authenticate(self) -> HttpResult[CredentialVO]:
        """
        使用access token校验登陆权限
        """


class AuthStrategyContext:
    """
    认证策略上下文，通过认证策略上下文实现不同认证策略切换，然后执行authenticate方法完成认证流程
    """

    strategy: AuthStrategy  # 当前策略
    user_session_mapper: UserSessionMapper  # 用户会话映射

    def __init__(self,
                 user_session_mapper: UserSessionMapper
                 ):
        self.user_session_mapper = user_session_mapper

    def set_strategy(self, strategy: AuthStrategy):
        """ 切换认证策略 """
        self.strategy = strategy

    def authenticate(self) -> CredentialVO:
        """ 执行认证策略 """
        return self.strategy.authenticate(self)


class AuthStrategy:
    """
    认证策略，discord_login接口通过前端传入参数的种类不同，采用不同的认证策略实现登入，配合
    认证策略上下文使用
    """
    @abstractmethod
    def authenticate(self, ctx: AuthStrategyContext) -> CredentialVO:
        """
        认证流程具体实现
        """
        pass


class TokenHelper:
    """ 令牌助手，生成令牌或者验证令牌 """
    @staticmethod
    def generate_token(user_id: int, expires_in: int) -> str:
        """ 生成jwt令牌 """
        payload = {
            'user_id': user_id,
            'exp': datetime.now() + timedelta(seconds=expires_in)
        }
        app_secret_key = default_config.get(DefaultConfigTag.APP_SECRET_KEY)  # 获取app密匙
        token = jwt.encode(payload, app_secret_key , algorithm='HS256')
        return token

    @staticmethod
    def verify_token(token: str) -> TokenPayloadDTO:
        try:
            # token解码
            app_secret_key = default_config.get(DefaultConfigTag.APP_SECRET_KEY)
            payload = jwt.decode(token, app_secret_key, algorithms=['HS256'])
        except ExpiredSignatureError:  # token过期
            raise BusinessException(HttpCode.TOKEN_EXPIRED, _('token is expired'))
        except InvalidTokenError:  # token非法
            raise BusinessException(HttpCode.TOKEN_INVALID, _('token is invalid'))

        # 检查token有效性
        if not 'user_id' in payload:  # user_id字段不存在，或遭到篡改
            raise BusinessException(HttpCode.TOKEN_INVALID, _("Invalid token: missing userid"))

        dto = TokenPayloadDTO()
        BaseDomain.copy_properties(payload, dto)
        return dto  # 返回payload


