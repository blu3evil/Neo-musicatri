from __future__ import annotations

from datetime import datetime, timedelta
from typing import Tuple

import jwt
from flask import request, g
from jwt import ExpiredSignatureError, InvalidTokenError
from toollib.guid import SnowFlake
from typing_extensions import override

from client.discord_client import DiscordClient
from config.exception_configuration import SystemException, BusinessException
from container import services
from container.client_context import clients
from container.mapper_context import mappers
from domain.base_domain import BaseDomain
from domain.dto.discord_client_dto import DiscordOAuth2CredentialDTO, DiscordUserDTO
from domain.entity.profile_entity import DiscordUserEntity
from domain.entity.session_entity import DiscordOAuth2SessionEntity, UserSessionEntity
from domain.vo.auth_vo import CredentialVO
from repository.abs.discord_user_mapper import DiscordUserMapper
from repository.abs.user_session_mapper import UserSessionMapper
from repository.abs.discord_oauth2_session_mapper import DiscordOAuth2SessionMapper
from repository.abs.transaction_manager import TransactionManager
from service.abs.permission_service import PermissionTag, PermissionService
from service.abs.auth_service import AuthService, AuthStrategy, AuthStrategyContext
from utils import HttpResult, HttpCode, default_locale as _, log
from utils import default_config, DefaultConfigTag


# todo: controller本地化，需要替换所有的default_locale到g.t
class AuthServiceDiscordImpl(AuthService):
    """ 认证服务discord实现类 """
    user_session_mapper: UserSessionMapper
    def __init__(self):
        self.ctx = AuthStrategyContext()
        self.ctx.user_session_mapper = self.user_session_mapper

    @override
    def auth_code_authenticate(self) -> HttpResult[CredentialVO]:
        """ discord登录服务 """
        _ = g.t  # 重定向本地化到请求本地化
        missing_params = []  # 参数判断
        if not request.get_json().get('code'): missing_params.append('code')
        if not request.headers.get('device_id'): missing_params.append('device_id')

        if missing_params:
            message = ', '.join(missing_params)
            result = HttpResult.error(HttpCode.INVALID_REQUEST_PARAMS,_("missing param: %(params)s") % {'params': message})
            return result

        # 使用auth code认证策略
        log.info(_(f"Received authentication request: device_id: {request.headers.get('device_id')}"))
        self.ctx.set_strategy(DiscordOAuth2CodeStrategy())
        return self.__do_authenticate()

    @override
    def access_token_authenticate(self) -> HttpResult[CredentialVO]:
        """ 使用access token校验用户登录权限 """
        missing_params = []  # 参数判断
        if not request.headers.get('Authorization'): missing_params.append('code')
        if not request.headers.get('device_id'): missing_params.append('device_id')

        if missing_params:
            message = ', '.join(missing_params)
            result = HttpResult.error(HttpCode.INVALID_REQUEST_PARAMS,_("missing param: %(params)s") % {'params': message})
            return result

        # access token认证策略
        log.info(_(f"Received authentication request: device_id: {request.headers.get('device_id')}"))
        self.ctx.set_strategy(AccessTokenStrategy())
        return self.__do_authenticate()

    def __do_authenticate(self) -> HttpResult[CredentialVO]:
        transaction_manager = mappers.get(TransactionManager)
        transaction_manager.begin()  # 开启事务
        try:
            # 通过认证上下文执行认证策略
            credential_vo: CredentialVO = self.ctx.authenticate()
            transaction_manager.commit()  # 提交事务
            return HttpResult.success(HttpCode.SUCCESS, _("authenticate successfully"), credential_vo)
        except BusinessException as error:  # 客户端错误
            transaction_manager.rollback()
            return HttpResult.error(error.code, error.message)
        except SystemException as error:  # 服务端错误
            log.error(error.message)
            transaction_manager.rollback()
            return HttpResult.error(error.code, error.message)
        except Exception as error:  # 未知错误
            log.error(error)
            transaction_manager.rollback()
            return HttpResult.error(HttpCode.INTERNAL_SERVER_ERROR, HttpCode.INTERNAL_SERVER_ERROR.describe)
        finally:
            transaction_manager.close()  # 停止事务


class AccessTokenStrategy(AuthStrategy):

    """ 使用access token进行权限校验 """
    @override
    def authenticate(self, ctx: AuthStrategyContext) -> CredentialVO:
        """
        使用前端提交的jwt进行校验
        """
        access_token = request.headers.get('Authorization')  # access token
        device_id = request.headers.get('device_id')  # device_id

        # 1.校验access token有效性
        access_token_expired, user_id = self.verify_access_token(ctx, access_token, device_id)
        if not access_token_expired:
            # access token没有过期，可以直接返回结果放行
            return CredentialVO()
        else:

            # 2.access token过期，校验discord access token有效性
            discord_access_token_expired = self.verify_discord_access_token(user_id=user_id)
            if not discord_access_token_expired:
                # discord access token没有过期，需要刷新用户的access token
                new_access_token, expires_in = upsert_user_session(user_id=user_id, device_id=device_id)
                return CredentialVO(access_token=new_access_token, expires_in=expires_in)
            else:

                # 3.discord access token过期，需要刷新access token
                discord_refresh_token_expired = self.refresh_discord_access_token(user_id=user_id)
                if not discord_refresh_token_expired:
                    # discord access token没有过期，且成功刷新discord access token
                    # 需要刷新用户的access token
                    new_access_token, expires_in = upsert_user_session(user_id=user_id, device_id=device_id)
                    return CredentialVO(access_token=new_access_token, expires_in=expires_in)
                else:
                    # discord refresh token过期，需要用户重新登录
                    raise BusinessException(HttpCode.TOKEN_EXPIRED, _("Refresh token expired"))


    @staticmethod
    def verify_access_token(ctx:AuthStrategyContext, access_token: str, device_id: str) -> Tuple[bool, int]:
        """
        1.校验access token有效性
        返回access token是否过期，以及用户id，如果过期，应当执行discord access token验证流程

        - 如果access token有效，那么向前端响应认证通过
        - 如果access token过期，那么执行verify_discord_access_token校验discord oauth2凭证有效性
        - 如果access token无效，那么响应token无效，前端应当清除token，执行重新登入逻辑
        """
        token_expired = False
        try:
            app_secret_key = default_config.get(DefaultConfigTag.APP_SECRET_KEY)  # app密匙
            jwt.decode(access_token, app_secret_key, algorithms=['HS256'])
        except ExpiredSignatureError:  # token过期
            # raise BusinessException(HttpCode.TOKEN_EXPIRED, _('token is expired'))
            token_expired = True
        except InvalidTokenError:  # token非法
            raise BusinessException(HttpCode.TOKEN_INVALID, HttpCode.TOKEN_INVALID.describe)

        # 校验会话状态
        user_session_mapper = ctx.user_session_mapper
        user_session_condition = UserSessionEntity(access_token=access_token, device_id=device_id)
        user_session_records = user_session_mapper.select_by_condition(user_session_condition)

        if len(user_session_records) > 1:
            # 状态错误，device_id和access_token应当映射到某一个独立的会话
            raise SystemException(HttpCode.INTERNAL_SERVER_ERROR, _("more than one user session found"))

        if len(user_session_records) == 0:
            # 没有会话存在，需要用户重新验证
            raise BusinessException(HttpCode.TOKEN_INVALID, _("no session"))

        user_session_record = user_session_records[0]  # 获取会话，检查会话状态
        if not user_session_record.is_active:
            # 会话已经被关闭，状态为非活跃
            raise BusinessException(HttpCode.TOKEN_SESSION_INACTIVE, _("session closed"))

        user_id = user_session_record.user_id
        # token已经过期，使用mapper查询获取user_id
        # 校验用户是否存在
        discord_user_mapper = mappers.get(DiscordUserMapper)
        discord_user_record = discord_user_mapper.select_by_id(user_id)
        if not discord_user_record:
            raise BusinessException(HttpCode.NOT_FOUND, _("no such user"))

        # 校验用户权限
        permission_service = services.get(PermissionService)
        flag = permission_service.verify_user_permission(user_id, PermissionTag.USER.value)
        if not flag:
            raise BusinessException(HttpCode.PERMISSION_DENIED, _("profile blocked"))

        return token_expired, user_id

    @staticmethod
    def verify_discord_access_token(user_id: int) -> bool:
        """
        2.校验discord access token有效性
        返回discord access token是否过期，以及refresh token

        - 如果discord access token仍然有效，那么基于响应前端一个新的access token，同时更新user session数据
        - 如果discord access token过期，那么使用refresh_token方法尝试刷新access token
        - 如果discord access token无效，那么响应前端token失效，前端应当删除现有token执行重新登入逻辑
        """
        token_expired = False
        discord_oauth2_session_mapper = mappers.get(DiscordOAuth2SessionMapper)  # 获取discord oauth2会话mapper
        discord_oauth2_session_record = discord_oauth2_session_mapper.select_by_user_id(user_id)  # 获取discord oauth2会话对象

        # 检查access token有效性
        discord_client = clients.get(DiscordClient)
        discord_access_token = discord_oauth2_session_record.access_token  # discord access token
        result = discord_client.fetch_user(discord_access_token)  # 使用discord access token尝试拉取用户信息

        if result.code == HttpCode.SUCCESS.code:
            # 响应成功，access token有效，更新用户会话信息，响应新的access token到前端
            # 由前端更新access token
            token_expired = False
        elif result.code == HttpCode.TOKEN_INVALID.code:
            # token无效，应当尝试刷新token，且仅在这种情况下刷新token
            token_expired = True
        elif result.code == HttpCode.NETWORK_ERROR.code:
            # 网络错误，通常由于代理引起
            raise SystemException(HttpCode.NETWORK_ERROR, _("cannot validate discord access token"))
        elif result.code == HttpCode.INTERNAL_SERVER_ERROR:
            # 服务器内部错误
            raise SystemException(HttpCode.INTERNAL_SERVER_ERROR, _("invalid access token"))

        return token_expired

    @staticmethod
    def refresh_discord_access_token(user_id: int) -> bool:
        """
        仅仅在discord access token已经过期的前提下尝试刷新token，刷新token会导致discord access token，
        discord refresh token发生变化

        - 如果成功刷新access token，那么更新discord oauth2 session，同时生成新的access token响应给前端
        - 如果refresh token过期或无效，均响应前端token无效，前端应清除现有token，执行重新登入
        """
        token_expired = False
        discord_oauth2_session_mapper = mappers.get(DiscordOAuth2SessionMapper)  # 获取discord oauth2会话mapper
        discord_oauth2_session_record = discord_oauth2_session_mapper.select_by_user_id(user_id)  # 获取discord oauth2会话对象

        # 检查refresh token有效性
        discord_client = clients.get(DiscordClient)
        discord_refresh_token = discord_oauth2_session_record.refresh_discord_access_token  # discord refresh token
        result = discord_client.refresh_discord_access_token(discord_refresh_token)  # 使用discord access token尝试拉取用户信息

        if result.code == HttpCode.SUCCESS.code:
            # 响应成功，成功刷新discord access token，需要更新discord认证凭据信息
            # 同时更新用户的凭据信息，向前端返回新的access token

            # 此处更新discord oauth2 session信息
            data: DiscordOAuth2CredentialDTO = result.data
            BaseDomain.copy_properties(data, discord_oauth2_session_record)  # 将新的属性拷贝进入原来的pojo
            discord_oauth2_session_record.expires_at = datetime.now() + timedelta(seconds=data.expires_in)

            # 更新数据
            flag = discord_oauth2_session_mapper.update(discord_oauth2_session_record)
            if not flag:
                raise SystemException(HttpCode.INTERNAL_SERVER_ERROR, _("failed in updating discord oauth2 session"))
            token_expired = False
        elif result.code == HttpCode.TOKEN_INVALID.code:
            # token无效，应当尝试刷新token，且仅在这种情况下刷新token
            token_expired = True
        elif result.code == HttpCode.NETWORK_ERROR.code:
            # 网络错误，通常由于代理引起
            raise SystemException(HttpCode.NETWORK_ERROR, _("cannot validate discord access token"))
        elif result.code == HttpCode.INTERNAL_SERVER_ERROR:
            # 服务器内部错误
            raise SystemException(HttpCode.INTERNAL_SERVER_ERROR, _("invalid access token"))

        return token_expired


class DiscordOAuth2CodeStrategy(AuthStrategy):
    """ 使用discord授权code登入 """
    @override
    def authenticate(self, ctx: AuthStrategyContext) -> CredentialVO:
        """ 前端提供授权code参数进行校验 """
        code = request.get_json().get('code')   # code
        device_id = request.headers.get('device_id')  # device_id

        # 1.确保通过discord查询数据，将结果插入或者更新用户数据
        user_id, discord_oauth2_credential_dto = self.upsert_discord_user(code=code)

        # 2.确保用户的discord oauth2会话对象被创建或更新
        self.upsert_discord_oauth2_session(user_id=user_id, discord_oauth2_credential_dto=discord_oauth2_credential_dto)

        # 3.确保创建用户的设备会话信息
        access_token, expires_in = upsert_user_session(user_id=user_id, device_id=device_id)

        # 4.返回jwt和refresh token
        return CredentialVO(access_token=access_token, expires_in=expires_in)


    @staticmethod
    def upsert_discord_user(code) -> Tuple[int, DiscordOAuth2CredentialDTO]:
        """
        更新或者插入用户discord数据，
        - 当用户已经存在，校验用户是否拥有登入权限，并在权限允许时更新用户权限，返回用户id，
        - 如果用户不存在，直接插入新的用户数据

        返回用户的discord userid，
        """
        discord_client = clients.get(DiscordClient)  # 注入discord http客户端
        oauth2_credential_result = discord_client.fetch_oauth2_credential(code)  # 拉取discord oauth2凭证
        if oauth2_credential_result.code == HttpCode.INTERNAL_SERVER_ERROR.code:
            # discord client请求失败，服务器内部错误
            log.error(oauth2_credential_result.message)
            raise SystemException(HttpCode.INTERNAL_SERVER_ERROR, oauth2_credential_result.message)
        elif oauth2_credential_result.code != HttpCode.SUCCESS.code:
            # 请求不成功，客户端错误
            raise BusinessException(HttpCode.CLIENT_ERROR, oauth2_credential_result.message)

        discord_oauth2_credential_dto: DiscordOAuth2CredentialDTO = oauth2_credential_result.data
        log.info(discord_oauth2_credential_dto.to_dict())  # 打印discord oauth2 credential消息日志

        # 拉取用户信息
        discord_oauth2_access_token = discord_oauth2_credential_dto.access_token  # 获取access_token
        discord_user_result = discord_client.fetch_user(discord_oauth2_access_token)  # 拉取用户信息
        if discord_user_result.code == HttpCode.INTERNAL_SERVER_ERROR.code:
            # 服务器内部错误，记录日志
            log.error(discord_user_result.message)  # discord client请求失败
            raise SystemException(HttpCode.INTERNAL_SERVER_ERROR, discord_user_result.message)
        elif discord_user_result.code != HttpCode.SUCCESS.code:
            # 客户端错误
            raise BusinessException(HttpCode.CLIENT_ERROR, discord_user_result.message)

        discord_user_dto: DiscordUserDTO = discord_user_result.data
        user_id = discord_user_dto.id  # 获取id字段
        log.info(discord_user_result.to_dict())  # 打印discord user消息日志

        # 2.校验用户是否存在
        discord_user_mapper = mappers.get(DiscordUserMapper)  # 注入discord用户mapper
        discord_user_record = discord_user_mapper.select_by_id(user_id)

        if discord_user_record:
            # 3.若用户存在，校验用户权限，查询是否拥有登入权限
            permission_service: PermissionService = services.get(PermissionService)  # 使用权限校验相关service接口
            flag = permission_service.verify_user_permission(user_id=user_id, permission=PermissionTag.GUEST.value)  # 至少为访客权限

            if not flag:
                # 用户没有登陆权限，账号已经被禁用
                log.debug(_("prevent user login, user id : '%(id)s'") % {'id': user_id})
                raise BusinessException(HttpCode.PERMISSION_DENIED, _("profile blocked"))

            # 用户拥有登录权限，返回user_id以及discord oauth2授权凭证dto
            return user_id, discord_oauth2_credential_dto

        else:
            # 用户不存在，插入新的用户信息到数据库
            discord_user_entity = DiscordUserEntity()
            BaseDomain.copy_properties(discord_user_dto, discord_user_entity)
            discord_user_entity.id = user_id  # 单独设置用户id

            flag = discord_user_mapper.insert(discord_user_entity)  # 检查是否创建用户失败
            if not flag: raise SystemException(HttpCode.INTERNAL_SERVER_ERROR, _("failed in creating discord user, user id: '%(id)s'")
                                               % {'id': user_id})

            # 为用户创建权限信息，默认为USER权限
            permission_service: PermissionService = services.get(PermissionService)
            flag = permission_service.upsert_user_permission(user_id=user_id, permission=PermissionTag.USER.value)
            # 检查权限创建是否失败
            if not flag: raise SystemException(HttpCode.INTERNAL_SERVER_ERROR, _("failed in creating permission, user id: '%(id)s')'")
                                               % {'user_id': user_id})

            # 完成用户创建，返回user_id以及discord oauth2授权凭证dto
            return user_id, discord_oauth2_credential_dto

    @staticmethod
    def upsert_discord_oauth2_session(user_id: int, discord_oauth2_credential_dto: DiscordOAuth2CredentialDTO):
        """
        在确保用户拥有登陆权限，且用户已经被存储进入数据库的情况下，更新或者插入用户的discord oauth2会话信息
        """
        # 用户拥有登陆权限，更新用户discord oauth2 session信息(既然已经有了新的discord access token和discord refresh token，没有
        # 必要继续验证原来的token有效性，直接更新信息)
        discord_oauth2_session_mapper = mappers.get(DiscordOAuth2SessionMapper)  # 注入mapper
        discord_oauth2_session_record: DiscordOAuth2SessionEntity = discord_oauth2_session_mapper.select_by_user_id(user_id)

        # 检查是否已经存在discord oauth2会话记录
        if discord_oauth2_session_record:
            # 会话记录已经存在，那么更新已有的会话记录即可
            BaseDomain.copy_properties(discord_oauth2_credential_dto, discord_oauth2_session_record)  # 将新的属性拷贝到原有的属性上
            discord_oauth2_session_record.expires_at = datetime.now() + timedelta(seconds=discord_oauth2_credential_dto.expires_in)
            flag = discord_oauth2_session_mapper.update(discord_oauth2_session_record)  # 更新discord oauth2 session
            # 检查是否更新成功
            if not flag: raise SystemException(HttpCode.INTERNAL_SERVER_ERROR,
                                               _("failed in updating discord oauth2 session, user id: '%(id)s'")
                                               % {'id': user_id})

        else:
            # 会话记录尚且不存在，创建新的discord_oauth2_session会话记录
            discord_oauth2_session_entity = DiscordOAuth2SessionEntity(
                id=SnowFlake().gen_uid(),  # 生成雪花id
                user_id=user_id,  # discord userid
                expires_at = datetime.now() + timedelta(seconds=discord_oauth2_credential_dto.expires_in)  # 过期时间节点
            )
            BaseDomain.copy_properties(discord_oauth2_credential_dto, discord_oauth2_session_entity)  # 拷贝剩余属性
            flag = discord_oauth2_session_mapper.insert(discord_oauth2_session_entity)  # 创建会话数据
            # 检查会话数据创建情况
            if not flag: raise SystemException(HttpCode.INTERNAL_SERVER_ERROR,
                                               _("failed in creating discord session, user id '%(id)s'")
                                               % {'id': user_id})


def generate_token(user_id: int, expires_in: int) -> str:
    """ 生成jwt令牌 """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in)  # 使用utc时区时间
    }
    app_secret_key = default_config.get(DefaultConfigTag.APP_SECRET_KEY)  # 获取app密匙
    token = jwt.encode(payload, app_secret_key , algorithm='HS256')
    return token


def upsert_user_session(user_id: int, device_id: str) -> Tuple[str, int]:
    """
    插入或者更新用户会话数据，在确保用户已经存在的前提下，如果用户对于此device_id和user_id执行判断:
    - 已经存在会话，且会话只有一个，那么更新这个会话，
    - 如果会话有多个，那么更新最新的会话，删除其他所有旧的会话
    - 如果会话不存在，那么针对此user_id与device_id创建一个新的会话

    返回生成的access_token以及expired_in过期时间
    """
    user_session_mapper = mappers.get(UserSessionMapper)  # 注入用户会话mapper
    # 根据user_id和device_id查询原先的会话信息
    user_session_condition = UserSessionEntity(user_id=user_id, device_id=device_id)
    user_session_records = user_session_mapper.select_by_condition(user_session_condition)
    if not user_session_records:
        # 原先并没有相关会话，创建新的会话数据
        expires_in = default_config.get(DefaultConfigTag.ACCESS_TOKEN_EXPIRES)  # 获取access token有效时间
        access_token = generate_token(user_id=user_id, expires_in=expires_in)  # 生成新的access token
        user_session_entity = UserSessionEntity(
            id=SnowFlake().gen_uid(),  # 使用雪花算法生成id
            user_id=user_id,
            device_id=device_id,
            access_token=access_token,
            expires_at=datetime.now() + timedelta(seconds=expires_in),
            is_active=True
        )

        flag = user_session_mapper.insert(user_session_entity)  # 插入新的会话数据到数据库
        if not flag: raise SystemException(HttpCode.INTERNAL_SERVER_ERROR, _("failed creating user session"))

        return access_token, expires_in  # 返回结果

    elif len(user_session_records) > 1:
        # 存在多条会话文档记录，那么更新最新的那条，将其他会话记录全部删除
        # 获取最新的会话记录
        latest_user_session_record = max(user_session_records, key=lambda x: x['updated_at'])
        outdated_user_session_record_ids = []
        for record in user_session_records:
            if record.id != latest_user_session_record.id:
                outdated_user_session_record_ids.append(record.id)

        count = user_session_mapper.delete_by_ids(outdated_user_session_record_ids)  # 删除老旧文档
        if count <= 0: raise SystemException(HttpCode.INTERNAL_SERVER_ERROR, _("failed deleting outdated user session"))

        # 更新最新的文档
        expires_in = default_config.get(DefaultConfigTag.ACCESS_TOKEN_EXPIRES)  # 获取access token有效时间
        access_token = generate_token(user_id=user_id, expires_in=expires_in)  # 生成新的access token
        latest_user_session_record.access_token = access_token
        latest_user_session_record.expires_at = datetime.now() + timedelta(seconds=expires_in)
        latest_user_session_record.is_active = True

        flag = user_session_mapper.update(latest_user_session_record)  # 执行更新
        if not flag: raise SystemException(HttpCode.INTERNAL_SERVER_ERROR, _("failed updating user session"))
        return access_token, expires_in  # 返回结果

    elif len(user_session_records) == 1:
        # 仅仅只存在一条数据，那么更新这条数据即可
        updated_user_session_record = user_session_records[0]
        # 更新最新的文档
        expires_in = default_config.get(DefaultConfigTag.ACCESS_TOKEN_EXPIRES)  # 获取access token有效时间
        access_token = generate_token(user_id=user_id, expires_in=expires_in)  # 生成新的access token
        updated_user_session_record.access_token = access_token
        updated_user_session_record.expires_at = datetime.now() + timedelta(seconds=expires_in)
        updated_user_session_record.is_active = True

        flag = user_session_mapper.update(updated_user_session_record)  # 执行更新
        if not flag: raise SystemException(HttpCode.INTERNAL_SERVER_ERROR, _("failed updating user session"))
        return access_token, expires_in  # 返回结果

    else:
        raise SystemException(HttpCode.INTERNAL_SERVER_ERROR, _("unknown status upserting user session"))