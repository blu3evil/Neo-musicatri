"""
异常处理模块，此模块编写了函数处理器，用于处理程序当中出现的业务级别异常BusinessException，系统级别异常SystemException
"""
from typing import Any

from flask import jsonify, Response, Flask

from utils.locale import default_locale as _
from utils.logger import log
from utils.result import HttpResult, HttpCode


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

def handle_404(exception) -> Response:
    """ 404 NOT FOUND处理 """
    log.debug(str(exception))
    result = HttpResult.error(HttpCode.NOT_FOUND, HttpCode.NOT_FOUND.describe)
    return jsonify(result.to_dict())

def handle_500(exception) -> Response:
    """ 500 INTERNAL SERVER ERROR处理 """
    log.debug(str(exception))
    result = HttpResult.error(HttpCode.INTERNAL_SERVER_ERROR, HttpCode.INTERNAL_SERVER_ERROR.describe)
    return jsonify(result.to_dict())

def handle_business(exception: BusinessException) -> Response:
    """ 业务级别异常处理 """
    code = exception.code
    log.error(_("%(code)s %(description): %(message)s")
              % {'code': code, 'description': code.describe , 'message': exception.message})
    result = HttpResult.error(exception.code, exception.message, exception.data)
    return jsonify(result.to_dict())  # 序列化成json后返回

def handle_system(exception: SystemException) -> Response:
    """ 系统级别异常处理 """
    code = exception.code
    log.error(_("%(code)s %(description): %(message)s")
              % {'code': code, 'description': code.describe, 'message': exception.message})
    result = HttpResult.error(exception.code, exception.message, exception.data)
    # todo: 向开发者提交系统级别异常消息，并记录错误日志信息
    return jsonify(result.to_dict())


def handle_generic(generic_exception: Exception) -> Response:
    """
    通用类型异常处理器，当业务级别异常和系统级别异常无法处理的时候，
    此异常处理进行兜底避免程序报错

    在开发阶段应该避免使用这个异常处理，会导致错误堆栈输出遗漏，难以排查错误原因
    """
    log.error(_("unknown: %s") % generic_exception)
    # todo: 此处向开发者提交未知异常消息，记录错误日志信息
    result = HttpResult.error(HttpCode.INTERNAL_SERVER_ERROR, HttpCode.INTERNAL_SERVER_ERROR.describe)
    return jsonify(result.to_dict())


def exception_handler_configure(app: Flask) -> None:
    """ 注册异常处理器，在app.py中使用此方法注册异常处理器 """
    @app.errorhandler(404)
    def not_found_exception_handle(exception: Exception) -> Response:
        """ 404资源未找到异常处理器 """
        return handle_404(exception)

    @app.errorhandler(500)
    def internal_server_error_handle(exception: Exception) -> Response:
        """ 500服务器异常处理器 """
        return handle_500(exception)

    @app.errorhandler(BusinessException)
    def business_exception_handler(exception: BusinessException) -> Response:
        """ 业务级别异常处理器 """
        return handle_business(exception)

    @app.errorhandler(SystemException)
    def system_exception_handler(exception: SystemException) -> Response:
        """ 系统级别异常处理器 """
        return handle_system(exception)

    @app.errorhandler(Exception)
    def generic_exception_handler(exception: Exception) -> Response:
        """ 未知异常处理器 """
        return handle_generic(exception)
