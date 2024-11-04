"""
权限校验相关装饰器，将装饰器标注在路由上，可以在请求打入路由之前执行权限校验
逻辑，将权限不符合的请求屏蔽
"""
from functools import wraps

def require_user_permission(strict_mode=False):
    """
    用户权限校验器，针对路由进行标注，路由需要拥有至少USER级别的权限才可以访问
    strict_mode参数定义是否开启严格检查模式，在严格检查模式下，不论access token是否有效
    都会保持检查discord oauth2有效性，以提高性能消耗为前提，提高校验安全性
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            pass

























