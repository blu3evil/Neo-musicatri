from __future__ import annotations
from enum import Enum
from typing import TypeVar

from typing_extensions import Generic

from domain.base_domain import BaseDomain
from utils.locale import default_locale as _

class Code(Enum):
    """ 响应码值 """
    @property
    def code(self) -> int:
        return self.value[0]
    @property
    def describe(self) -> str:
        """ 码值描述 """
        return self.value[1]

T = TypeVar('T', bound=BaseDomain)  # HttpResult data数据类型

class Result(Generic[T]):
    """
    响应基类，定义了一种基础的响应格式，即code, message, data的响应格式
    参数:
        code: 必选参数，响应码，使用Code基类
        message: 可选参数，当后端发生异常时，返回结果应当包含这个值
        data: 可选参数，当后端发生异常时此值可以为null
    示例:
        Result类提供了类静态方法作为工厂来快速构建Result对象，以提供前端视图进行展示
        对于后端RESTFUL API接口:
        return Result.success(Code.SELECT_SUCCESSFULLY, "响应成功", null)
    """
    def __init__(self, code: int, message: str, data: T):
        """ 不推荐使用构造方法手动构建Result对象，推荐使用工厂方法 """
        self._code: int = code
        self._message: str = message
        self._data: T = data

    def to_dict(self):
        """ 序列化 """
        return {
            "code": self.code,
            "message": self.message,
            "data": None if self._data is None else self._data.to_dict(),
        }

    @property
    def code(self) -> int:
        return self._code

    @property
    def message(self) -> str:
        return self._message

    @property
    def data(self) -> T:
        return self._data

CodeImpl = TypeVar('CodeImpl', bound=Code)
ResultImpl = TypeVar('ResultImpl', bound= Result)

class HttpCode(Code):
    """ 适用于Controller路由视图函数的响应码值 """
    # SUCCESS类别
    SUCCESS = (20000, _("operation successfully"))  # 操作成功

    # CLIENT级别错误
    CLIENT_ERROR = (40000, _("client error"))  # 客户端错误
    NOT_FOUND = (40400, _("resource not found"))  # 资源未找到
    INVALID_REQUEST_PARAMS = (40001, _("invalid request params"))  # 请求参数无效
    AUTHENTICATION_FAILED = (40002, _("authentication.py failed"))   # 认证失败
    PERMISSION_DENIED = (40003, _("permission denied"))  # 权限不足
    TOKEN_EXPIRED = (40004, _("token expired"))  # token过期
    TOKEN_INVALID = (40005, _("token invalid"))  # token无效
    TOKEN_SESSION_INACTIVE = (40006, _("token session has been closed"))  # jwt会话已经被关闭

    # SERVER级别错误
    INTERNAL_SERVER_ERROR = (50000, _("internal server error"))  # 服务器内部错误
    NETWORK_ERROR = (50001, _("network error"))  # 网络错误

class BotCode(Code):
    """ 适用于机器人操作的响应结果码值 """
    SUCCESS = (20000, _("operation successfully"))
    ERROR = (50000, _("operation error"))
    AWAITING = (30000, _("awaiting"))
    UNKNOWN = (30001, _("unknown"))


class HttpResult(Result, Generic[T]):
    def __init__(self, code: int, message=None, data: T=None):
        super(HttpResult, self).__init__(code, message, data)

    @staticmethod
    def success(code: HttpCode=HttpCode.SUCCESS, message: str=None, data: T=None) -> HttpResult[T]:
        """ 构建成功响应Result对象 """
        result = HttpResult(code.code, message, data)
        return result

    @staticmethod
    def error(code: HttpCode, message: str=None, data: T=None) -> HttpResult[T]:
        """ 构建错误响应Result对象 """
        # 使用私有构造函数构建Result对象
        result = HttpResult(code.code, message, data)
        return result

class BotResult(Result, Generic[T]):
    """ Bot机器人实例统一返回结果，机器人外观实例统一以此类实例作为返回结果 """
    def __init__(self, code: int, message: str=None, data: T=None):
        super(BotResult, self).__init__(code, message, data)

    @staticmethod
    def success(code: BotCode=BotCode.SUCCESS, message: str=None, data: T=None) -> BotResult[T]:
        """ 构建成功响应Result对象 """
        result = BotResult(code.code, message, data)
        return result

    @staticmethod
    def error(code: BotCode, message: str=None, data: T=None) -> BotResult[T]:
        """ 构建错误响应Result对象 """
        result = BotResult(code.code, message, data)
        return result
