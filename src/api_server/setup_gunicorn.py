from api_server.base_app import app, setup_app

# 使用gunicorn启动flask
# 启动命令: gunicorn -c gunicorn.conf.py run_gunicorn:app

setup_app()
app = app
