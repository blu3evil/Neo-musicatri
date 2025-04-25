from auth_server.context import context
from auth_server.domain.models import DiscordUser, Role, UserRole, model_to_dict, db
from auth_server.services.cache_service import cache_service
from common.domain.models import Result

locale = context.locale

class UserService:
    @staticmethod
    def get_user_info(user_id):
        """ 获取用户discord账户信息 """
        _ = locale.get()

        # 命中缓存
        result = cache_service.get_user_info(user_id)
        if result.code == 200: return result

        # 未命中缓存，读取数据库到缓存当中
        user = db.session.query(DiscordUser).get(user_id)  # 缓存不存在，从数据库查询
        if user:
            user_info = model_to_dict(user)
            cache_service.set_user_info(user_id, user_info)
            # cache.set(f'{users_prefix}:{user_id}:{info_prefix}', user_info)
            return Result(200, _('miss hit cache'), user_info)
        return Result(404, _('no such user'))  # 用户不存在

    @staticmethod
    def get_user_roles(user_id) -> Result:
        """ 获取用户权限信息 """
        _ = locale.get()
        # role_names = cache.get(f'{users_prefix}:{user_id}:{roles_prefix}')
        result = cache_service.get_user_roles(user_id)
        if result.code == 200: return result

        # 缓存不存在，从数据库查询
        user = db.session.query(DiscordUser).get(user_id)
        if not user: return Result(404, _('no such user'))

        user_roles = user.roles
        if not user_roles: return Result(404, _('user has no roles'))

        role_names = [role.name for role in user_roles]  # 返回权限名称
        # cache.set(f'{users_prefix}:{user_id}:{roles_prefix}', role_names)  # 写入缓存
        cache_service.set_user_roles(user_id, role_names)

        return Result(200, _('miss hit cache'), data=role_names)

    @staticmethod
    def get_user_details(user_id):
        """ 获取用户详细信息，用于全局展示数据 """
        info_result = user_service.get_user_info(user_id)  # 获取用户信息
        if info_result.code != 200: return info_result

        role_result = user_service.get_user_roles(user_id)  # 获取用户权限信息
        if role_result.code != 200: return role_result

        info_result.data['roles'] = role_result.data  # 成功获取用户以及权限信息
        info_result.data['id'] = str(info_result.data['id'])  # 转string防止精度丢失
        return info_result

    @staticmethod
    def get_all_users_preview(condition: dict):
        """
        获取全部用户简要信息，用于前端表格展示，应当使用分页查询方法，而不是此方法
        """
        # 通过discord user查询基础数据
        user_query = db.session.query(DiscordUser)
        # 标识名查询
        if condition.get('username'):
            pattern = condition.get('username').replace('*', '%')
            user_query = user_query.filter(DiscordUser.username.like(pattern))  # 模糊查询

        # 全局名查询
        if condition.get('global_name'):
            pattern = condition.get('global_name').replace('*', '%')
            user_query = user_query.filter(DiscordUser.global_name.like(pattern))

        # 状态查询
        if condition.get('is_active') is not None and condition.get('is_active') != -1:
            user_query = user_query.filter(DiscordUser.is_active == condition.get('is_active'))

        match_users = user_query.all()  # 查询获取所有匹配的用户结果
        preview_data = []

        for user in match_users:
            user_id = str(user.id)  # 根据用户id查询中间表获取用户所有权限，转字符串避免精度丢失
            user_roles_query = db.session.query(UserRole).filter(UserRole.user_id == user_id)
            user_roles = user_roles_query.all()  # 获取用户所有的权限
            roles_name_list = []

            for user_role in user_roles:  # 通过role_id获取role_name
                role_id = user_role.role_id
                roles_query = db.session.query(Role).filter(Role.id == role_id)
                user_role = roles_query.first()
                if user_role:
                    roles_name_list.append(user_role.name)

            preview_data.append({
                'id': user_id,
                'roles': roles_name_list,
                'username': user.username,
                'global_name': user.global_name,
                'is_active': user.is_active
            })

        return Result(200, data=preview_data)

    @staticmethod
    def get_users_preview(condition: dict, current_page: int, page_size: int):
        """
        分页查询获取全部用户简要信息，用于前端表格展示
        """
        # 通过discord user查询基础数据
        user_query = db.session.query(DiscordUser)
        # 标识名查询
        if condition.get('username'):
            pattern = condition.get('username').replace('*', '%')
            user_query = user_query.filter(DiscordUser.username.like(pattern))  # 模糊查询

        # 全局名查询
        if condition.get('global_name'):
            pattern = condition.get('global_name').replace('*', '%')
            user_query = user_query.filter(DiscordUser.global_name.like(pattern))

        # 状态查询
        if condition.get('is_active') is not None and condition.get('is_active') != -1:
            user_query = user_query.filter(DiscordUser.is_active == condition.get('is_active'))

        total = user_query.count()  # 统计检索结果条目数
        offset = (current_page - 1) * page_size  # 偏移值
        paginated_users = user_query.offset(offset).limit(page_size).all()

        preview_data = []
        for user in paginated_users:
            user_id = str(user.id)  # 根据用户id查询中间表获取用户所有权限，转字符串避免精度丢失
            user_roles_query = db.session.query(UserRole).filter(UserRole.user_id == user_id)
            user_roles = user_roles_query.all()  # 获取用户所有的权限
            roles_name_list = []

            for user_role in user_roles:  # 通过role_id获取role_name
                role_id = user_role.role_id
                roles_query = db.session.query(Role).filter(Role.id == role_id)
                user_role = roles_query.first()
                if user_role:
                    roles_name_list.append(user_role.name)

            preview_data.append({
                'id': user_id,
                'roles': roles_name_list,
                'username': user.username,
                'global_name': user.global_name,
                'is_active': user.is_active
            })

        return Result(200, data={
            'total': total,
            'users': preview_data
        })


    @staticmethod
    def get_all_roles():
        """ 获取所有可用的权限级别 """
        roles_query = db.session.query(Role)
        roles = roles_query.all()
        return Result(200, data=[{
            'id': role.id,
            'name': role.name,
            'description': role.description,
            'disabled': role.disabled
        } for role in roles])


    @staticmethod
    def _update_user_status(user: DiscordUser, is_active: bool):
        """ 更新用户账户当前状态 """
        user.is_active = is_active


    @staticmethod
    def _update_user_roles(user: DiscordUser, role_names: list[str]):
        """ 更新用户当前的权限等级 """
        roles = db.session.query(Role).filter(Role.name.in_(role_names)).all()
        if len(roles) != len(set(role_names)):
            _ = locale.get()
            raise RuntimeError(_('One or more roles are invalid'))
        user.roles = roles  # 修改用户权限


    @staticmethod
    def update_user(user_id: int, data: dict):
        """ 部分更新更新用户数据 """
        _ = locale.get()
        user = db.session.query(DiscordUser).get(user_id)
        if not user:
            return Result(404, _('User not found'))

        if 'is_active' in data:
            try:
                UserService._update_user_status(user, data['is_active'])
            except Exception as e:
                return Result(500, _('failed in updating user active status: %s') % e)

        if 'roles' in data:
            try:
                UserService._update_user_roles(user, data['roles'])
            except Exception as e:
                return Result(500, _('failed in updating user roles: %s') % e)

        db.session.commit()  # 修改成功，清理用户数据缓存，使更新生效
        cache_service.clear_user_info(user_id)
        return Result(200, _('user updated successfully'))


    @staticmethod
    def delete_user(user_id: int):
        """ 删除用户数据，首先删除用户权限数据，然后删除用户数据 """
        _ = locale.get()
        user = db.session.query(DiscordUser).get(user_id)
        if not user:
            return Result(404, _('no such user'))

        user.roles.clear()  # 删除用户关联权限外键
        db.session.delete(user)  # 删除用户数据
        db.session.commit()

        result = cache_service.clear_user_session(user_id=user_id)  # 注销用户会话
        if result.code != 200: return result

        result = cache_service.clear_user_info(user_id=user_id)  # 清理用户数据缓存
        if result.code != 200: return result

        return Result(200, _('user deleted successfully'))


user_service = UserService()