from core import session, cache, db
from dao import DiscordUser, to_dict
from utils import locales
from common.result import Result

users_prefix = 'users'
roles_prefix = 'roles'
info_prefix = 'info'

class UserService:
    @staticmethod
    def get_info() -> Result:
        """ 获取当前用户信息 """
        _ = locales.get()
        user_id = session['user_id']
        user_info = cache.get(f'{users_prefix}:{user_id}:{info_prefix}')
        if user_info: return Result(200, _('hit cache'), user_info)

        # 缓存不存在，从数据库查询
        user = db.session.query(DiscordUser).get(user_id)
        if user:  # 用户存在，缓存数据
            user_info = to_dict(user)
            cache.set(f'{users_prefix}:{user_id}:{info_prefix}', user_info)
            return Result(200, _('miss hit cache'), user_info)
        return Result(404, _('no such user'))  # 用户不存在

    @staticmethod
    def get_roles():
        """ 获取当前用户权限 """
        _ = locales.get()
        user_id = session['user_id']
        user_roles = cache.get(f'{users_prefix}:{user_id}:{roles_prefix}')
        if user_roles: return Result(200, _('hit cache'), user_roles)

        # 缓存不存在，从数据库查询
        user = db.session.query(DiscordUser).get(user_id)
        if not user: return Result(404, _('no such user'))

        user_roles = user.roles
        if not user_roles: return Result(404, _('user has no roles'))
        return Result(200, _('miss hit cache'), user_roles)


user_service = UserService()