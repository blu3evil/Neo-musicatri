"""
异常处理注解
"""
from functools import wraps
from typing import Callable, Any, Type

from utils.locale import default_locale as _
from utils.logger import log


# 继续抛出异常
def rethrow(old_error: Exception, new_error: Exception):
    """
    异常包装注解，你可能需要先捕获异常然后将异常转化为另一种异常
    继续向上抛出?
    """
    def decorated(*args, **kwargs):
        def wrapper(func):
            try:
                return func(*args, **kwargs)
            except old_error as error:
                raise new_error   # 继续抛出异常
        return wrapper
    return decorated

# 返回默认值
def fallback(val_supplier: Callable[[Exception], Any], target: Type[Exception]=Exception):
    """
    捕获异常，当异常发生后调用提供的val_supplier，并将结果作为返回值返回
    (你甚至可以添加多个fallback来捕获不同的异常，这真是太酷了(这句划掉))
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except target as error:
                return val_supplier(error)  # 返回默认值
        return wrapper
    return decorator

# 仅记录异常，不抛出或返回
def log_error(func):
    """
    自动捕获异常，将异常记录进入日志后退出，不作额外处理
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as error:
            log.error(_("logged an exception occur : %(exception)s") % {'exception': error})
            # 不抛出，也不返回新的结果
    return wrapper