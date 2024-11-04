"""
适用于controller控制器的注解，用于对一些接口进行审计
"""
import logging
from functools import wraps
from flask import request
from utils.locale import default_locale as _
from utils.logger import log

# todo : 记录请求URL地址 记录请求方法
def client_info_aware(route_path: str,
                      client_ip_aware=True,  # 记录请求ip
                      referer_aware=False,  # 记录请求来源引用
                      user_agent_aware=False):  # 记录请求代理（浏览器信息）
    """
    标注此注解以通过日志记录请求客户端的地址、请求、代理信息默认仅仅开启ip记录，
    引用信息和客户端代理信息需要手动开启
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logging_info = []

            # 根据参数控制是否记录特定信息
            if client_ip_aware:  # 记录客户端ip
                client_ip = request.remote_addr
                logging_info.append("remote_addr: %s" % client_ip)

            if referer_aware:  # 记录客户端引用信息
                referer = request.headers.get('Referer', 'No Referer')
                logging_info.append("Referer: %s" % referer)

            if user_agent_aware:  # 记录代理信息
                user_agent = request.headers.get('User-Agent', 'No User-Agent')
                logging_info.append("User-Agent: %s" % user_agent)

            # 将所有日志信息整合并记录
            log_message = " | ".join(logging_info)
            log.info(_("route logging: %(route_path)s : %(log_message)s")
                     % {"route_path": route_path,"log_message": log_message})

            # 执行原始路由逻辑
            return func(*args, **kwargs)

        return wrapper
    return decorator


def time_consuming_aware(route_path: str):
    """
    标记此注解来记录某个接口对于请求处理的耗时信息
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            start_time = time.time()  # 记录开始时间
            response = func(*args, **kwargs)  # 执行原始路由逻辑

            end_time = time.time()  # 记录结束时间
            time_consuming = end_time - start_time  # 记录耗时
            log.info(_("route time consuming: %(route_path)s : %(time_consuming).6f seconds") %
                     {"route_path": route_path, "time_consuming": time_consuming})
            return response
        return wrapper
    return decorator


def timeout_aware(route_path: str, threshold: float):
    """
    使用这个接口来标记路由，若路由响应时间超时之后会触发记录日志
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            start_time = time.time()  # 记录开始时间
            response = func(*args, **kwargs)  # 执行原始路由逻辑

            end_time = time.time()  # 记录结束时间
            time_consuming = end_time - start_time  # 记录耗时

            if time_consuming > threshold:
                # 若超出时间阈值则记录日志
                log.info(_("route_timeout: %(route_path)s : %(time_consuming).6f seconds, higher than setting threshold %(threshold).6f seconds") %
                         {"route_path": route_path, "time_consuming": time_consuming, "threshold": threshold})

            return response
        return wrapper
    return decorator


def custom_event_aware(route_path: str,  # 路由路径，方便参考日志
                       event_name="default_event",  # 事件名称
                       before_execute=lambda : None,  # 路由触发前
                       after_execute=lambda : None,  # 路由触发后
                       ):
    """
    自定义事件注解，当路由被触发时会直接打印日志，也可以通过这个装饰器直接传入一个闭包，当路由执行的时候
    对应的闭包将会被执行
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logging.info(_("route_event_triggered: %(route_path) : %(event_name)")
                         % {"route_path": route_path, "event_name": event_name})
            # 执行前置函数
            before_execute()
            # 执行路由逻辑
            response = func(*args, **kwargs)
            # 执行后置函数
            after_execute()
            return response
        return wrapper
    return decorator
