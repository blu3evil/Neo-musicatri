from toollib.guid import SnowFlake
from typing_extensions import override

from container import mappers
from domain.entity.permission_entity import PermissionEntity, UserPermissionEntity
from repository.abs.permission_mapper import PermissionMapper
from repository.abs.user_permission_mapper import UserPermissionMapper
from service.abs.permission_service import PermissionService, PermissionTag
from utils import log
from utils.locale import default_locale as _

class PermissionServiceImpl(PermissionService):
    """ 权限相关api """

    def __init__(self):
        # 初始化数据库
        self.__init_permission_table()

    @staticmethod
    def __init_permission_table():
        # 注入mapper，校验默认权限级别是否存在
        permission_mapper = mappers.get(PermissionMapper)
        records = permission_mapper.select_all()

        defaults = []  # 默认权限等级
        for tag in PermissionTag: defaults.append(tag.value)
        flag = set(defaults) == set(records)

        if not flag:
            log.debug(_("permission table got error status, reinitialize table..."))
            # 两者不相等，重新初始化权限等级数据库表
            permission_mapper.delete_all()
            count = permission_mapper.insert_batch(defaults)
            log.debug(_('done initializing permission table, %(count)s documents inserted') % ({'count': count}))

    @override
    def verify_user_permission(self, user_id: str, permission: PermissionEntity) -> bool:
        """ 校验用户权限， """
        # 注入user_permission_mapper
        user_permission_mapper = mappers.get(UserPermissionMapper)
        # 注入permission_mapper
        permission_mapper = mappers.get(PermissionMapper)
        # 通过user_permission_mapper查询user_id到permission_id映射
        user_permission_record: UserPermissionEntity = user_permission_mapper.select_by_user_id(user_id)

        if not user_permission_record:
            user_rank = PermissionTag.GUEST.rank()   # 记录不存在，用户权限为GUEST级别权限
        else:
            # 记录存在，查询权限记录，使用记录的rank
            permission_record = permission_mapper.select_by_id(user_permission_record.permission_id)
            user_rank = permission_record.rank

        # 检查权限等级是否大于等于给定的rank
        return user_rank >= permission.rank


    @override
    def upsert_user_permission(self, user_id: int, permission: PermissionEntity) -> bool:
        # 注入mapper
        permission_mapper = mappers.get(PermissionMapper)
        # 检查权限是否存在
        permission_record = permission_mapper.select_by_id(permission.id)
        if not permission_record: return False  # 权限不存在，返回false

        # 权限存在，修改用户权限等级
        # 注入mapper
        user_permission_mapper = mappers.get(UserPermissionMapper)

        # 检查记录是否已经存在
        user_permission_record = user_permission_mapper.select_by_user_id(user_id)
        if not user_permission_record:
            # 记录不存在，创建新的记录
            record = UserPermissionEntity(
                id=SnowFlake().gen_uid(),  # 使用雪花算法生成id
                user_id=user_id,  # 用户id
                permission_id=permission.id,  # 权限等级id
            )
            user_permission_mapper.insert(record)
        else:  # 记录已经存在执行更新
            user_permission_record.permission_id = permission.id
            user_permission_mapper.update(permission_record)

        return True  # 设置成功


    @override
    def get_user_permission(self, user_id: int) -> PermissionEntity:
        user_permission_mapper = mappers.get(UserPermissionMapper)  # 注入mapper
        user_permission_record = user_permission_mapper.select_by_user_id(user_id)  # 通过userid请求获取数据

        # 若用户不存在那么返回访客权限
        if not user_permission_record: return PermissionTag.GUEST.value

        # 记录存在，查询用户的权限信息
        permission_mapper = mappers.get(PermissionMapper)
        permission_id = user_permission_record.permission_id
        permission_record = permission_mapper.select_by_id(permission_id)

        return permission_record  # 返回查询结果