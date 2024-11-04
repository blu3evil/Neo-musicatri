""" flask生命周期配置 """
from flask import Flask, request, g, make_response
from utils.locale import locales

def lifecycle_configure(app: Flask):
    """ 配置flask生命周期事件 """

    @app.before_request
    def before_request():
        """ 接收请求前事件挂载 """
        # 处理OPTIONS预检请求，支持Accept-Language头信息
        # todo: 使用事件总线来处理flask生命周期，简化触发逻辑
        # 使用flask_cors处理，简化OPTIONS预检请求处理逻辑
        # if request.method == 'OPTIONS':
        #     response = make_response()
        #     # 允许Accept-Language请求头，用于根据用户本地化发送本地化响应信息
        #     response.headers['Access-Control-Allow-Headers'] = 'Accept-Language, Content-Type, Authorization, X-Requested-With, Device-ID'
        #     response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
        #     response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        #     return response

        accept_language = request.headers.get('Accept-Language')  # zh-CN
        g.t = locales.get(accept_language)  # 请求到达前挂载本地化

