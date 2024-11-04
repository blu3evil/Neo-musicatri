from urllib.parse import urlparse

from pymongo import MongoClient
from typing_extensions import override

from repository.database_client import DatabaseClient
from repository.mongodb.mapper.session_mapper_impl import DiscordOAuth2SessionMapperImpl, UserSessionMapperImpl, \
    SocketIOSessionMapperImpl
from repository.mongodb.mapper.profile_mapper_impl import DiscordUserMapperImpl
from repository.mongodb.mapper.permission_mapper_impl import PermissionMapperImpl, UserPermissionMapperImpl
from repository.mongodb.transaction_manager_impl import TransactionManagerImpl
from utils import log, default_config, DefaultConfigTag
from utils.locale import default_locale as _


class MongodbClient(DatabaseClient):
    """ mongodb抽象工厂实现，使用pymongo实现数据库连接 """

    # todo: 抽离库表名称作为变量，集中定义

    def __init__(self):
        """ 初始化mongodb """
        database_url = default_config.get(DefaultConfigTag.DATABASE_URL)  # 获取连接路径
        self.__init_mongodb_client(database_url)  # 初始化mongodb client连接

    def __init_mongodb_client(self, database_url):
        """ 通过传入参数解析url，获取连接信息，初始化数据库 """
        log.debug(_("initializing mongodb client..."))
        result = urlparse(database_url)

        prototype = result.scheme
        if not prototype == 'mongodb':  # 校验协议
            prototype = 'mongodb'
            log.warning(_("MongodbClient initialization error: invalid prototype : %(prototype)s, fallback to 'mongodb' as prototype")
                      % {'prototype': prototype})

        host = result.hostname  # 主机名
        if not host or host == '':  # 主机名校验
            host = '127.0.0.1'
            log.warning(_("MongodbClient initialization error: invalid host : %(host)s, fallback to '127.0.0.1' as host")
                      % {'host': host})

        port = result.port  # 端口号
        if not port or port >= 65535 or port <= 0:  # 端口号校验
            port = 27017
            log.warning(_("MongodbClient initialization error: invalid port : %(port)s, fallback to '27017' as port")
                      % {'port': port})

        database = result.path[1:]  # 数据库名称
        if not database or database == '':  # 数据库校验
            database = 'musicatri'
            log.warning(_("MongodbClient initialization error: invalid database name : cannot be none or empty string, fall back to 'musicatri' as database name "))

        username = result.username  # 用户名
        password = result.password  # 密码

        client = MongoClient(host=host, port=port, username=username, password=password)  # 初始化mongodb连接
        log.debug(_("connecting to mongodb: host: %(host)s, port: %(port)s, username: %(username)s, password: %(password)s")
                  % {'host': host, 'port': port, 'username': username, 'password': password})

        # 初始化数据库
        self.database = client[database]
        # 配置平台事务管理器
        self.transaction_manager = TransactionManagerImpl(client)

    """ 数据库连接客户端抽象工厂，实现之后返回对应的mapper实例，从而实现底层数据库的连接驱动切换 """
    @override
    def get_discord_user_mapper(self) -> DiscordUserMapperImpl:
        """ 返回discord用户信息映射器 """
        return DiscordUserMapperImpl(self.database, self.transaction_manager)

    @override
    def get_discord_oauth_session_mapper(self) -> DiscordOAuth2SessionMapperImpl:
        """ 获取discord oauth认证会话信息映射器 """
        return DiscordOAuth2SessionMapperImpl(self.database, self.transaction_manager)

    @override
    def get_jwt_session_mapper(self) -> UserSessionMapperImpl:
        """ 获取jwt会话映射器 """
        return UserSessionMapperImpl(self.database, self.transaction_manager)

    @override
    def get_user_permission_mapper(self) -> UserPermissionMapperImpl:
        """ 获取用户权限信息映射器 """
        return UserPermissionMapperImpl(self.database, self.transaction_manager)

    @override
    def get_permission_mapper(self) -> PermissionMapperImpl:
        """ 获取权限信息详情映射器 """
        return PermissionMapperImpl(self.database, self.transaction_manager)

    @override
    def get_user_socketio_session_mapper(self) -> SocketIOSessionMapperImpl:
        """ 获取用户websocket连接信息表 """
        return SocketIOSessionMapperImpl(self.database, self.transaction_manager)

    @override
    def get_transaction_manager(self) -> TransactionManagerImpl:
        """ 获取平台事务管理器 """
        return self.transaction_manager