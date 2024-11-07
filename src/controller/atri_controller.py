"""
Musicatri机器人RESTFUL API接口
"""
from flask import Blueprint, jsonify
from discord_bot.atri import atri_facade
from service.abs.atri_service import AtriService
from container.service_context import services
from utils.result import HttpResult, HttpCode, BotCode

# 音乐机器人蓝图
atri_bp = Blueprint('atri_bp', __name__, url_prefix='/admin/atri')

@atri_bp.route('/start', methods=['POST'])
async def start_atri():
    """ 启动Musicatri机器人 """
    # atri_service = mvc.get(AtriService)
    # response = await atri_service.start_atri()
    # return response
    bot_result = await atri_facade.start_atri()

    if bot_result.code == BotCode.SUCCESS.code:
        result = HttpResult.success(HttpCode.SUCCESS, bot_result.message)  # 启动成功
    else:
        result = HttpResult.success(HttpCode.INTERNAL_SERVER_ERROR, bot_result.message)  # 登录失败
    return jsonify(result.to_dict())


@atri_bp.route('/stop', methods=['DELETE'])
async def stop_atri():
    """ 停止atri机器人 """
    atri_service = services.get(AtriService)  # mvc
    bot_result = await atri_facade.stop_atri()
    if bot_result.code == BotCode.SUCCESS.code:
        result = HttpResult.success(HttpCode.SUCCESS, bot_result.message)
    else:
        result = HttpResult.success(HttpCode.INTERNAL_SERVER_ERROR, bot_result.message)
    return jsonify(result.to_dict())

