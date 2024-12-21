from api_server.app_context import config, ConfigKey, socketio, app, setup_app, log


def do_run_werkzeug():
    host = config.get(ConfigKey.APP_WSGI_HOST)  # 服务器主机名
    port = config.get(ConfigKey.APP_WSGI_PORT)  # 服务器端口号
    debug_mode = config.get(ConfigKey.APP_WSGI_WERKZEUG_DEBUG_MODE)  # 调试模式
    log_output = config.get(ConfigKey.APP_WSGI_WERKZEUG_LOG_OUTPUT)  # 是否打印flask日志
    use_reloader = config.get(ConfigKey.APP_WSGI_WERKZEUG_USE_RELOADER)  # 使用热重载

    socketio.run(app=app,
                 host=host,
                 port=port,
                 debug=debug_mode,
                 log_output=log_output,
                 use_reloader=use_reloader,
                 allow_unsafe_werkzeug=True)  # 使用werkzeug启动flask

    log.info("musicatri teardown")

if __name__ == '__main__':
    setup_app()
    do_run_werkzeug()