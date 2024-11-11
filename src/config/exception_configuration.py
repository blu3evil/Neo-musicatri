"""
异常处理模块，此模块编写了函数处理器，用于处理程序当中出现的业务级别异常BusinessException，系统级别异常SystemException
"""
from typing import Any

from flask import jsonify, Response, Flask, g

from utils.logger import log
from utils.result import HttpCode


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

def exception_handler_configure(app: Flask) -> None:
    """ 注册异常处理器，在app.py中使用此方法注册异常处理器 """
    @app.errorhandler(404)  # not found
    def handle_404(exception: Exception) -> Response:
        _ = g.t
        return jsonify({'message': _('not found')})

    @app.errorhandler(500)
    def handle_500(exception: Exception) -> Response:
        _ = g.t
        # todo: 此处向开发者提交未知异常消息，记录错误日志信息
        log.debug(str(exception))
        return jsonify({'message': _('internal error')})

    @app.errorhandler(Exception)
    def handle_uncaught(exception: Exception) -> Response:
        _ = g.t
        # todo: 此处向开发者提交未知异常消息，记录错误日志信息
        log.error(_("unknown: %s") % exception)
        return jsonify({'message': _('uncaught error')})