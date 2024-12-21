from api_server.app_context import cache, db, locales
from api_server.domain.models import DiscordUser, to_dict
from common import Result

users_prefix = 'users'
roles_prefix = 'roles'
info_prefix = 'info'

class UserService:
    @staticmethod
    def get_info(user_id):
        _ = locales.get()
        user_info = cache.get(f'{users_prefix}:{user_id}:{info_prefix}')
        if user_info: return Result(200, _('hit cache'), user_info)
        user = db.session.query(DiscordUser).get(user_id)  # 缓存不存在，从数据库查询
        if user:  # 用户存在，缓存数据
            user_info = to_dict(user)
            cache.set(f'{users_prefix}:{user_id}:{info_prefix}', user_info)
            return Result(200, _('miss hit cache'), user_info)
        return Result(404, _('no such user'))  # 用户不存在

    @staticmethod
    def get_roles(user_id):
        _ = locales.get()
        role_names = cache.get(f'{users_prefix}:{user_id}:{roles_prefix}')
        if role_names: return Result(200, _('hit cache'), role_names)

        # 缓存不存在，从数据库查询
        user = db.session.query(DiscordUser).get(user_id)
        if not user: return Result(404, _('no such user'))

        user_roles = user.roles
        if not user_roles: return Result(404, _('user has no roles'))

        role_names = [role.name for role in user_roles]  # 返回权限名称
        cache.set(f'{users_prefix}:{user_id}:{roles_prefix}', role_names)  # 写入缓存

        return Result(200, _('miss hit cache'), role_names)

    @staticmethod
    def clear_cache(user_id):
        """ 清理用户缓存信息 """
        cache.delete(f'{users_prefix}:{user_id}:{roles_prefix}')  # 清理权限信息缓存
        cache.delete(f'{users_prefix}:{user_id}:{info_prefix}')  # 清理用户数据缓存

    @staticmethod
    def get_details(user_id):
        """ 获取用户详细信息，用于全局展示数据 """
        info_result = user_service.get_info(user_id)  # 获取用户信息
        if info_result.code != 200: return info_result

        role_result = user_service.get_roles(user_id)  # 获取用户权限信息
        if role_result.code != 200: return role_result

        info_result.data['roles'] = role_result.data  # 成功获取用户以及权限信息
        info_result.data['id'] = str(info_result.data['id'])  # 转string防止精度丢失
        return info_result

user_service = UserService()