from api_server.app_context import config, ConfigKey
from utils import root_path
from os import path

workers = config.get(ConfigKey.APP_WSGI_GUNICORN_WORKERS)  # 进程数
threads = config.get(ConfigKey.APP_WSGI_GUNICORN_THREADS)  # 线程数
bind = f'{config.get(ConfigKey.APP_WSGI_HOST)}:{config.get(ConfigKey.APP_WSGI_PORT)}'  # 端口ip
daemon = config.get(ConfigKey.APP_WSGI_GUNICORN_DAEMON)  # 是否后台运行
worker_class = config.get(ConfigKey.APP_WSGI_GUNICORN_WORKER_CLASS)  # 工作模式协程
worker_connections = config.get(ConfigKey.APP_WSGI_GUNICORN_WORKER_CONNECTIONS)  # 最大连接数（并发量）

pidfile = path.join(root_path, 'temp', config.get(ConfigKey.APP_WSGI_GUNICORN_PIDFILE))  # gunicorn进程文件'/var/run/gunicorn.pid'
accesslog = path.join(root_path, 'temp', config.get(ConfigKey.APP_WSGI_GUNICORN_ACCESSLOG))  # 设置访问日志和错误信息日志路径'/var/log/gunicorn_access.log'
errorlog = path.join(root_path, 'temp', config.get(ConfigKey.APP_WSGI_GUNICORN_ERRORLOG))  # '/var/log/gunicorn_error.log'

loglevel = config.get(ConfigKey.APP_WSGI_GUNICORN_LOGLEVEL)  # 设置日志记录水平 warning