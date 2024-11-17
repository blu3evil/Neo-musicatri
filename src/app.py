"""
Musicatri启动入口模块
"""
import os

from flask import Flask, request, g, jsonify, Response
from utils import config, ConfigEnum, locale_factory, log

dev_mode = False                                                        # dev mode
debug_mode = False                                                      # debug mode
app = Flask(__name__)                                                   # flak app

def main():
    init_config()  # 配置文件初始化
    init_handlers()  # 初始化异常处理器
    init_cors()  # 初始化cores
    init_app_event()  # 初始化生命事件钩子
    init_views()  # 初始化蓝图
    init_flasgger()  # 初始化接口文档

    init_core()  # 初始化核心
    print_banner()  # 打印旗帜

    run_server()  # 运行服务

def init_config():
    """ 配置文件初始化 """
    global dev_mode
    global debug_mode
    dev_mode = config.get(ConfigEnum.APP_DEV_MODE)
    debug_mode = config.get(ConfigEnum.APP_DEBUG_MODE)

    if dev_mode: log.warning(
        "dev mode is enabled, know more about development mode at README.md, this mode is only used for "
        "development and testing, do not enable this mode in production environment")

    if debug_mode: log.warning(
        "debug mode is still on testing, which might cause unpredictable problems, this mode is only "
        "used for development and testing, do not enable this mode in production environment")

    app.config['SECRET_KEY'] = config.get(ConfigEnum.APP_SECURITY_SECRET_KEY)
    # ============================================== OAUTH =============================================================
    # oauth2开启https
    if config.get(ConfigEnum.APP_SECURITY_OAUTH_INSECURE_TRANSPORT):
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # 允许oauth2动态权限调整
    if config.get(ConfigEnum.APP_SECURITY_OAUTH_RELAX_TOKEN_SCOPE):
        os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

def init_core():
    import core
    core.init(app)


def init_cors():
    """ 前后端项目需要配置适当跨域 """
    from flask_cors import CORS
    log.debug(f'initialize cores...')
    # 启用CORS对所有路由，并允许携带Access token在Authorization请求头
    origins = config.get(ConfigEnum.APP_NETWORK_CORS_ALLOW_ORIGINS)
    headers = config.get(ConfigEnum.APP_NETWORK_CORS_ALLOW_HEADERS)
    methods = config.get(ConfigEnum.APP_NETWORK_CORS_ALLOW_METHODS)
    supports_credentials = config.get(ConfigEnum.APP_NETWORK_CORS_SUPPORTS_CREDENTIALS)

    CORS(app, resources={
        # 支持前端调用后端RESTFUL api
        # 如果手动携带Authorization请求头，需要明确来源，而非'*'，浏览器可能对'*'来源的响应不作答复
        r"/api/*": {
            "origins": origins,
            "allow_headers": headers,
            "allow_methods": methods,
        }
    }, supports_credentials=supports_credentials)  # 允许cookie session凭证


def init_flasgger():
    """ 初始化项目接口文档(flasgger) """
    if not dev_mode: return  # 仅在开发者模式下开启swagger文档
    log.debug(f'initialize flasgger...')
    from flasgger import Swagger
    swagger_config = {  # swagger初始化
        "title": "Musicatri后端项目API文档",
        "uiversion": 3,
        "description": "Musicatri后端项目API说明文档",
        "version": "0.1.0",
        "termsOfService": "https://blu3evil.github.io/musicatri1",
        "contact": {
            "name": "pineclone",
            "email": "pineclone@outlook.com",
            "url": "https://github.com/eyespore"
        },
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
    }

    app.config['SWAGGER'] = swagger_config
    Swagger(app)


def init_handlers():
    """ 初始化项目异常处理器 """
    log.debug(f'initialize error handlers...')
    # 注册异常拦截器，不会覆盖原始异常
    def register_errorhandler(status, error_consumer):
        @app.errorhandler(status)
        def handler(e):
            _ = g.t
            log.error(e)  # 记录日志
            response = error_consumer(e, _)
            response.status_code = status
            return response

    register_errorhandler(400, lambda e, _: jsonify({'message': _('Bad Request')}))
    register_errorhandler(401, lambda e, _: jsonify({'message': _('Unauthorized')}))
    register_errorhandler(403, lambda e, _: jsonify({'message': _('Forbidden')}))
    register_errorhandler(404, lambda e, _: jsonify({'message': _('NotFound')}))
    register_errorhandler(500, lambda e, _: jsonify({'message': _('Internal Server Error')}))

    if dev_mode: return  # 兜底用的异常处理器，开发者模式下并不会注册这一项
    @app.errorhandler(Exception)
    def handle_uncaught(e: Exception) -> Response:
        _ = g.t
        # todo: 此处向开发者提交未知异常消息，记录错误日志信息
        log.error(_("unknown: %s") % e)
        response = jsonify({'message': str(e)})
        response.status_code = 400  # 将异常原因归咎于用户
        return response


def init_app_event():
    """ 初始化flask app生命周期 """
    log.debug(f'initialize event binding...')
    @app.before_request
    def before_request():
        accept_language = request.headers.get('Accept-Language')  # zh-CN
        g.t = locale_factory.get(accept_language)  # 请求到达前挂载本地化


def init_views():
    log.debug(f'initialize views...')
    """ 蓝图初始化，路由中绝大多数接口使用RESTFUL风格编写 """
    from views.static_blueprint import static_bp
    from views.system_blueprint import status_bp_v1
    from views.auth_blueprint import auth_bp_v1

    app.register_blueprint(static_bp)
    app.register_blueprint(status_bp_v1)
    app.register_blueprint(auth_bp_v1)


def print_banner():
    """ 打印musicatri旗帜，好康的旗帜 """
    if config.get(ConfigEnum.APP_LOG_PRINT_BANNER):
        log.info("""
    ______  ___                _____                _____         _____ 
    ___   |/  /____  _____________(_)_____________ ___  /____________(_)
    __  /|_/ / _  / / /__  ___/__  / _  ___/_  __ `/_  __/__  ___/__  / 
    _  /  / /  / /_/ / _(__  ) _  /  / /__  / /_/ / / /_  _  /    _  /  
    /_/  /_/   \__,_/  /____/  /_/   \___/  \__,_/  \__/  /_/     /_/   """)

def run_server():
    host = config.get(ConfigEnum.APP_NETWORK_HOST)  # 服务器主机名
    port = config.get(ConfigEnum.APP_NETWORK_PORT)  # 服务器端口号

    if not dev_mode:
        # 开发模式下有wsgi自己的地址绑定回显，不需要额外打印
        # noinspection HttpUrlsUsage
        log.info(f"services listening on: http://{host}:{port}")

    log.info("musicatri launch successfully")

    # 使用生产级别的WSGI服务器来支持socketio
    from core import socketio
    flask_logging_enable = config.get(ConfigEnum.APP_LOG_FLASK_LOGGING_ENABLE)  # 是否打印flask日志
    socketio.run(app=app, host=host, port=port, debug=debug_mode, log_output=flask_logging_enable)
    log.info("musicatri teardown")

if __name__ == '__main__':
    main()

