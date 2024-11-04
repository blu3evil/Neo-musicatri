"""
用户级别接口
"""
from flask import Blueprint, jsonify

from container import services
from service.upper_service.system_service import SystemService

system_bp = Blueprint('user_bp', __name__, url_prefix='/api/user')

