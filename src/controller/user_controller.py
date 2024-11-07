"""
用户级别接口
"""
from flask import Blueprint

system_bp = Blueprint('user_bp', __name__, url_prefix='/api/user')

