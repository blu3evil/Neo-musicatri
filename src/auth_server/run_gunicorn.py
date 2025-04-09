from auth_server.auth_server_context import context

# 使用gunicorn启动flask
# 启动命令: gunicorn -c gunicorn.conf.py run_gunicorn:app
app = context.app
