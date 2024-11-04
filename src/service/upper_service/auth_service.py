"""
oauth授权业务层
"""
from __future__ import annotations

from abc import abstractmethod
from datetime import datetime, timedelta

import flask
import jwt
from flask import Response
from jwt import ExpiredSignatureError, InvalidTokenError

from config.exception_configuration import BusinessException
from domain.base_domain import BaseDomain
from domain.dto.session_dto import TokenPayloadDTO

from domain.vo.auth_vo import CredentialVO
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


class AuthStrategy:
    """
    认证策略，discord_login接口通过前端传入参数的种类不同，采用不同的认证策略实现登入
    """
    @abstractmethod
    def authenticate(self) -> CredentialVO:
        """ 登录校验 """
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
