"""
异常处理模块，此模块编写了函数处理器，用于处理程序当中出现的业务级别异常BusinessException，系统级别异常SystemException
"""
from typing import Any

from flask import jsonify, Response, Flask

from utils.locale import default_locale as _
from utils.logger import log
from utils.result import HttpResult, HttpCode


def handle_404_not_found_exception(not_found_exception) -> Response:
    """
    404资源未找到异常
    """
    # 构建Result对象
    log.debug(_("404_resource_not_found: %s") % not_found_exception)
    result = HttpResult.error(HttpCode.NOT_FOUND,
                              HttpCode.NOT_FOUND.describe,
                              None)
    return jsonify(result.to_dict())

def handle_500_not_found_exception(internal_server_error) -> Response:
    """
    服务器内部异常
    """
    # 构建Result对象
    log.debug(_("500_internal_server_error: %s") % internal_server_error)
    result = HttpResult.error(HttpCode.INTERNAL_SERVER_ERROR,
                              HttpCode.INTERNAL_SERVER_ERROR.describe,
                              None)
    return jsonify(result.to_dict())


class BusinessException(Exception):
    """
    业务级别异常，这一类异常通常与应用程序的业务逻辑相关，一般是在业务流程执行过程中发生的特定错误
    例如验证失败，数据不一致或者业务规则不符合等等

    由于仅影响特定的业务流程或者操作，只会影响当前用的或当前请求
    """
    def __init__(self, code: HttpCode, message: str, data: Any=None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.data = data


def handle_business_exception(business_exception: BusinessException) -> Response:
    """
    业务级别异常处理器，处理业务级别异常并构建Result对象返回前端进行渲染
    """
    # 构建result对象
    log.error(_("business_exception_occur: %s") % business_exception.message)
    result = HttpResult.error(business_exception.code,
                              business_exception.message,
                              business_exception.data)
    # 序列化成json后返回
    return jsonify(result.to_dict())


class SystemException(Exception):
    """
    系统级别异常，系统级别异常通常由更高级别的错误捕获程序捕获，并尽可能详细记录错误信息以便后续调查
    这一类异常通常不涉及用户，由开发者或者运维人员负责调查和修复

    可能影响整个应用程序的可用性或者性能
    """
    def __init__(self, code: HttpCode, message: str, data: Any=None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.data = data


def handle_system_exception(system_exception: SystemException) -> Response:
    """
    业务级别异常处理器，处理业务级别异常并构建Result对象返回前端进行渲染
    """
    # 构建result对象
    log.error(_("system_exception_occur: %s") % system_exception)
    result = HttpResult.error(system_exception.code,
                              system_exception.message,
                              system_exception.data)
    # 序列化成json后返回到前端

    # todo: 向开发者提交系统级别异常消息，并记录错误日志信息

    return jsonify(result.to_dict())


def handle_generic_exception(generic_exception: Exception) -> Response:
    """
    通用类型异常处理器，当业务级别异常和系统级别异常无法处理的时候，
    此异常处理进行兜底避免程序报错

    在开发阶段应该避免使用这个异常处理，会导致错误堆栈输出遗漏，难以排查错误原因
    """
    log.error(_("unknown_exception_occur: %s") % generic_exception)

    # todo: 此处向开发者提交未知异常消息，记录错误日志信息

    result = HttpResult.error(HttpCode.INTERNAL_SERVER_ERROR,
                              HttpCode.INTERNAL_SERVER_ERROR.describe,
                              None)
    return jsonify(result.to_dict())


def exception_handler_configure(app: Flask) -> None:
    """
    注册异常处理器，在app.py中使用此方法注册异常处理器
    """
    @app.errorhandler(404)
    def not_found_exception_handle(exception: Exception) -> Response:
        """
        404资源未找到异常处理器
        """
        return handle_404_not_found_exception(exception)


    @app.errorhandler(500)
    def internal_server_error_handle(exception: Exception) -> Response:
        """
        500服务器内部错误
        """
        return handle_500_not_found_exception(exception)


    @app.errorhandler(BusinessException)
    def business_exception_handler(business_exception: BusinessException) -> Response:
        """
        业务级别异常处理
        """
        return handle_business_exception(business_exception)

    @app.errorhandler(SystemException)
    def system_exception_handler(system_exception: SystemException) -> Response:
        """
        系统级别异常处理
        """
        return handle_system_exception(system_exception)

    @app.errorhandler(Exception)
    def generic_exception_handler(generic_exception: Exception) -> Response:
        """
        处理未知异常
        """
        return handle_generic_exception(generic_exception)
