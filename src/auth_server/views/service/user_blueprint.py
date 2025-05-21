""" 服务用户查询接口 """

from flask import Blueprint, request
from auth_server.services.auth_service import service_auth_service_v2
from auth_server.services.user_service import user_service_v1
from auth_server.context import context

service_user_bp_v1 = Blueprint('service_user_bp_v1', __name__, url_prefix='/api/v1/service/users')
session = context.session
logger = context.logger
locale = context.locale
aspect = context.aspect


@service_user_bp_v1.route('/<string:user_id>/tokens', methods=['GET'])
@service_auth_service_v2.validate_required(roles=['plain'])
def get_user_tokens(user_id):
    result = user_service_v1.get_all_tokens(user_id)
    return result.as_response()
