"""
静态资源蓝图
"""

import os

from flask import Blueprint, send_from_directory

from utils.loggers import log
from utils.locales import default_locale as _

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
static_dir = os.path.join(root_dir, 'resources', 'static')
log.debug(_("static resource path locate in: %s") % static_dir)

static_bp = Blueprint('static_bp', __name__, static_folder=static_dir)  # 静态资源蓝图

@static_bp.route("/", methods=["GET"])
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
    return send_from_directory(static_bp.static_folder, "index.html")

@static_bp.route('/favicon.ico', methods=["GET", "POST"])
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
    return send_from_directory(static_bp.static_folder, 'favicon.ico')