from __future__ import annotations

import asyncio
from abc import abstractmethod
from asyncio import Future

from aiohttp import ClientConnectorError
from discord import Intents, LoginFailure, HTTPException
from discord.ext import commands

from utils.config_old import default_config, DefaultConfigTag
from utils.locale import default_locale as _
from utils.logger import log
from utils.result import BotResult, BotCode

class Atri(commands.AutoShardedBot):
    """
    音乐机器人——音乐亚托莉(Music Atri)
    """
    def __init__(self, command_prefix: str, intents: Intents):
        super().__init__(command_prefix=command_prefix, intents=intents)

class AtriFactory:
    """ 亚托莉工厂 """
    @staticmethod
    def assemble_atri(command_prefix: str, intents: Intents) -> Atri:
        """ 创建新的亚托莉对象 """
        atri = Atri(command_prefix=command_prefix, intents=intents)

        # # todo: atri事件绑定
        # @atri.event
        # async def on_connect():
        #     log.info("musicatri has connected to discord")

        @atri.event
        async def on_disconnect():
            log.debug(_("atri hibernate"))  # 亚托莉进入休眠

        # todo: atri命令绑定

        return atri


class AtriState:
    """ 亚托莉状态接口 """
    @abstractmethod
    async def start(self, ctx: AtriContext) -> BotResult:
        """ 启动亚托莉 """
        pass
    @abstractmethod
    async def stop(self, ctx: AtriContext) -> BotResult:
        """ 停止亚托莉 """
        pass

class AtriStopped(AtriState):
    """ 亚托莉停止 """
    async def start(self, ctx: AtriContext) -> BotResult:
        """ 建立到discord的连接 """
        ctx.state = AtriAwaiting()  # 切换到awaiting状态 pythonic
        if ctx.atri.is_closed():  # 若亚托莉处于休眠状态, 唤醒亚托莉
            command_prefix = default_config.get(DefaultConfigTag.DISCORD_BOT_COMMAND_PREFIX)
            atri = AtriFactory.assemble_atri(command_prefix, Intents.all())
            ctx.atri = atri

        # 使用闭包的形式传递
        @ctx.atri.event
        async def on_connect():
            # 亚托莉启动成功
            result = BotResult.success(BotCode.SUCCESS, _("atri started"))
            print(result.to_dict())

        # 异步启动亚托莉
        async def async_start():
            message = None
            token = default_config.get(DefaultConfigTag.DISCORD_BOT_TOKEN)
            try: await ctx.atri.start(token)  # 尝试启动亚托莉
            except LoginFailure as exception:
                # 亚托莉登录失败
                message = _("atri start failed, got loging failure: %(exception)s") % {"exception": exception}
            except HTTPException as exception:
                # 发生http错误
                message = _("atri start failed, got HTTP exception: %(exception)s") % {"exception": exception}
            except ClientConnectorError as exception:
                # 客户端连接错误，通常是由于代理
                message = _("atri start failed, got client connection error: %(exception)s") % {"exception": exception}
            except RuntimeError as exception:
                # todo: 记录亚托莉启动未知错误日志
                message = _("atri start failed, got unknown error: %(exception)s") % {"exception": exception}
                # raise exception
            if message:
                # 存在错误
                await ctx.atri.close()  # 关闭亚托莉
                error = BotResult.error(BotCode.ERROR, message)
                print(error.to_dict())

        task = asyncio.create_task(async_start())  # 异步启动亚托莉
        return BotResult.success(BotCode.SUCCESS, _("atri start successfully"))

    async def stop(self, ctx: AtriContext) -> BotResult:
        log.debug(_("atri has already stopped"))
        return BotResult.success(BotCode.SUCCESS, _("atri has already stopped"))


class AtriAwaiting(AtriState):
    """ 亚托莉等待 """
    async def start(self, ctx: AtriContext):
        AtriAwaiting.__forbidden()

    async def stop(self, ctx: AtriContext):
        AtriAwaiting.__forbidden()

    @staticmethod
    def __forbidden():
        log.debug(_("atri is in awaiting state"))


class AtriStarted(AtriState):
    """ 亚托莉启动 """
    async def start(self, ctx: AtriContext):
        pass

    async def stop(self, ctx: AtriContext):
        pass


class AtriContext:
    """ 上下文 """
    def __init__(self, atri: Atri, state: AtriState):
        """ 上下文初始化 """
        self._atri = atri
        self._state = state  # 初始化为停止状态

    async def start(self) -> BotResult:
        """ 启动亚托莉 """
        # 要小心阻塞
        return await self._state.start(self)

    async def stop(self) -> BotResult:
        """ 停止亚托莉 """
        # 当心阻塞
        return await self._state.stop(self)

    @property
    def atri(self) -> Atri:
        """ atri """
        return self._atri

    @property
    def state(self) -> AtriState:
        """ 机器人当前状态 """
        return self._state

    @state.setter
    def state(self, state: AtriState):
        self._state = state

    @atri.setter
    def atri(self, atri: Atri):
        self._atri = atri


class AtriFacade:
    """ 亚托莉外观类，控制亚托莉的生命周期 """
    ctx: AtriContext  # 上下文
    _instance = None

    def __new__(cls):
        if cls._instance is None:  # 初始化
            log.debug(_("initializing musicatri facade"))
            cls._instance = super().__new__(cls)
            AtriFacade.__init_facade()
        return cls._instance

    @classmethod
    def __init_facade(cls):
        """ 初始化外观 """
        command_prefix = default_config.get(DefaultConfigTag.DISCORD_BOT_COMMAND_PREFIX)

        atri = AtriFactory.assemble_atri(command_prefix=command_prefix, intents=Intents.all())
        ctx = AtriContext(atri=atri, state=AtriStopped())
        cls._instance.ctx = ctx  # 初始化上下文

    async def start_atri(self) -> BotResult:
        """ 启动亚托莉 """
        # 当心阻塞
        return await self.ctx.start()

    async def stop_atri(self) -> BotResult:
        """ 停止亚托莉 """
        # 当心阻塞
        return await self.ctx.stop()

# 外观
atri_facade = AtriFacade()