"""
跨域相关配置
"""
from flask import Flask
from flask_cors import CORS

from utils.logger import log
from utils.locale import default_locale as _

def cors_configure(app: Flask, dev_mode: bool):
    # 检查是否处在开发者模式
    if dev_mode:  # 开发者模式下允许所有跨域
        log.debug(_('enable cors for all router'))
        # 启用CORS对所有路由，并允许携带Access token在Authorization请求头
        CORS(app, resources={r"/*": {
            # 如果手动携带Authorization请求头，需要明确来源，而非'*'
            # 因为浏览器可能对'*'来源的响应不作答复
            "origins": "http://localhost:5173",
            "allow_headers": ["Content-Type", "X-Requested-With", "Authorization", "Device-ID"],
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"],
        }}, supports_credentials=False)

        # 如果使用cookie携带access token，那么supports_credentials应该为True
        # 如果手动设置请求头Authorization携带access token，那么supports_credentials可以为False

    # todo: 非开发模式下的跨域
    # todo: 将跨域配置到config

