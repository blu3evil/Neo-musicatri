from server_auth.context import context
gunicorn_config = context.gunicorn_config

workers = gunicorn_config.workers  # 进程数
threads = gunicorn_config.threads  # 线程数
bind = gunicorn_config.bind  # 端口ip
daemon = gunicorn_config.daemon  # 是否后台运行
worker_class = gunicorn_config.worker_class  # 工作模式协程
worker_connections = gunicorn_config.worker_connections  # 最大连接数（并发量）
