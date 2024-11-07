"""
测试用控制器，请不要在生产环境暴露接口
"""
from flask import Blueprint, jsonify
from utils.result import HttpResult, HttpCode
from container.mapper_context import mappers
from repository.abs.discord_user_mapper import DiscordUserMapper
from utils import log

test_bp = Blueprint('test_bp', __name__, url_prefix='/test')

@test_bp.route('/mapper', methods=['GET'])
def mapper_test():
    """
    mapper测试接口
    ---
    tags:
      - 测试接口
    responses:
      20000:
        description: 测试代码正常
    """
    # 测试代码
    discord_user_mapper = mappers.get(DiscordUserMapper)

    # 测试成功，返回DiscordUserMapperMongodbImpl，说明注入成功
    log.debug(type(discord_user_mapper))

    result = HttpResult.success(HttpCode.SUCCESS, "test pass")
    return jsonify(result.to_dict())

