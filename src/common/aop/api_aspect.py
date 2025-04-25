from functools import wraps
from flask import request
from typing import TypeVar
from common.utils.context import WebApplicationContext
from common.domain.models import Result

T = TypeVar('T', bound=WebApplicationContext)
class ApiAspect:
    """ 应用api切面注解工具 """
    ctx: T  # 上下文
    def __init__(self, ctx: T):
        self.ctx = ctx

    @staticmethod
    def pagination_query():
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    current_page = request.args.get("page", 1, type=int)
                    page_size = request.args.get("page_size", 10, type=int)
                except ValueError:
                    return Result(400, message='Invalid pagination params').as_response()

                kwargs['current_page'] = current_page  # 注入分页参数
                kwargs['page_size'] = page_size
                return func(*args, **kwargs)
            return wrapper
        return decorator

