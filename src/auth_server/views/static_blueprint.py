import os
from flask import Blueprint, send_from_directory
from common import root_path

static_dir = os.path.join(root_path, 'resources', 'api-server', 'static')
static_bp_v1 = Blueprint('static_bp_v1', __name__, static_folder=static_dir)  # 静态资源蓝图

@static_bp_v1.route("/", methods=["GET"])
def index():
    """
    网站主页
    ---
    description: |
      项目后端主页，没有功能实现
    tags:
      - 资源接口
    responses:
      20000:
        description: 返回主页信息
    """
    return send_from_directory(static_bp_v1.static_folder, "index.html")

@static_bp_v1.route('/favicon.ico', methods=["GET", "POST"])
def favicon():
    """
    网站图标接口
    ---
    tags:
      - 资源接口
    description: |
      返回项目后端的图标资源，并不会用到
    responses:
      200:
        description: 返回网站的图标
        content:
          image/png:
            schema:
              type: string
              format: binary
    """
    return send_from_directory(static_bp_v1.static_folder, 'favicon.ico')