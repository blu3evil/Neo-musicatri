import asyncio

from aiohttp import ClientConnectorError
from discord import LoginFailure, HTTPException
from flask import Response, jsonify

from discord_bot.atri import atri_facade
from service.upper_service.atri_service import AtriService
from utils import default_config, DefaultConfigTag, log, default_locale as _, HttpResult, HttpCode


class AtriServiceImpl(AtriService):
    async def start_atri(self) -> Response:
        token = default_config.get(DefaultConfigTag.DISCORD_BOT_TOKEN)
        try:  # 尝试登录
            log.debug(_("connecting musicatri to discord server..."))

            # 异步启动任务
            task = asyncio.create_task(atri_facade.start_atri(token))
            result = HttpResult.success(HttpCode.SUCCESS, _("atri run successfully"))

            return jsonify(result.to_dict())
        except LoginFailure as exception:
            # 登陆失败
            await atri_facade.close()
            result = HttpResult.success(HttpCode.INTERNAL_SERVER_ERROR, str(exception))
            return jsonify(result.to_dict())
        except HTTPException as exception:
            # HTTP错误
            await atri_facade.close()
            result = HttpResult.success(HttpCode.CLIENT_ERROR, str(exception))
            return jsonify(result.to_dict())
        except ClientConnectorError as exception:
            # 客户端连接错误，通常是由于代理
            await atri_facade.close()
            result = HttpResult.success(HttpCode.CLIENT_ERROR, str(exception))
            return jsonify(result.to_dict())
