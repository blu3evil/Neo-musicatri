from __future__ import annotations

import asyncio
from asyncio import AbstractEventLoop

from discord import Intents
from discord.ext import commands

from common import Result
from events import SocketioEvent, AtriEvent
from pyee.executor import ExecutorEventEmitter
from threading import Thread

from bot_server.bot_server_context import context, BotServerConfigKey

config = context.config  # 配置
logger = context.logger
locale = context.locale

bot_token = config.get(BotServerConfigKey.DISCORD_BOT_TOKEN)  # 机器人认证token

class Atri(commands.AutoShardedBot):
    """ 音乐机器人——音乐亚托莉(Music Atri) """
    def __init__(self, command_prefix: str, intents: Intents):
        super().__init__(command_prefix=command_prefix, intents=intents)

class AtriState:
    def __init__(self, identify):
        self._identify = identify

    @property
    def identify(self):
        return self._identify

    def enter(self, ctx: AtriContext):  # 状态变更
        # ctx.bot_eventbus.emit(AtriEvent.STATE_CHANGE, self.identify)  # 发布内部事件
        # from core import socketio
        # socketio.start_background_task(target=socketio.emit, event=SocketioEvent.ATRI_STATE_CHANGE, data=self.identify, namespace='/socket/admin')
        # socketio.emit(SocketioEvent.ATRI_STATE_CHANGE, self.identify, namespace='/socket/admin')
        logger.debug(f'musicatri change status to {self.identify}')

    def fadeout(self, ctx: AtriContext):
        pass

    # 启动亚托莉，用于启动机器人
    def start(self, ctx: AtriContext) -> Result:
        _ = locale.get()
        return Result(400, _('unsupported operation'))

    # 停止亚托莉，用于关闭机器人
    def stop(self, ctx: AtriContext) -> Result:
        _ = locale.get()
        return Result(400, _('unsupported operation'))

    # 初始化，在应用启动时初始化机器人线程
    def initialize(self, ctx: AtriContext) -> Result:
        """ 初始化实例 """
        _ = locale.get()
        return Result(400, _('unsupported operation'))

    # 用于线程退出的时候清理资源
    def terminate(self, ctx: AtriContext) -> Result:
        _ = locale.get()
        return Result(400, _('unsupported operation'))


# 线程启动前
class BotThreadIdle(AtriState):
    def __init__(self):
        super().__init__('created')

    def initialize(self, ctx: AtriContext) -> Result:
        def thread_target():
            ctx.bot_event_loop = asyncio.new_event_loop()  # 初始化事件循环
            asyncio.set_event_loop(ctx.bot_event_loop)  # 设置bot_thread的主事件循环
            ctx.bot_event_loop.run_forever()

        ctx.bot_thread = Thread(target=thread_target)
        ctx.bot_thread.start()
        logger.debug('bot thread start successfully')
        ctx.update_state(BotIdle())  # 机器人线程准备就绪，执行亚托莉初始化
        _ = locale.get()
        return Result(200, message=_('start atri thread'))


class BotThreadTerminated(AtriState):
    def __init__(self):
        super().__init__('terminated')


class BotThreadTerminating(AtriState):
    def __init__(self):
        super().__init__('terminating')

    def enter(self, ctx: AtriContext):
        super().enter(ctx)  # 触发事件


# 亚托莉初始化
class BotIdle(AtriState):
    def __init__(self):
        super().__init__('initializing')

    def enter(self, ctx: AtriContext):
        super().enter(ctx)  # 触发状态更新事件
        ctx.init_bot_instance()  # 初始化亚托莉实例
        ctx.update_state(BotStopped())  # 亚托莉准备就绪

class BotStopped(AtriState):
    def __init__(self):
        super().__init__('stopped')

    def start(self, ctx: AtriContext) -> Result:
        """ 启动亚托莉 """
        ctx.update_state(AtriStarting())   # 切换到starting状态

        @ctx.bot_instance.event  # 启动成功回调
        async def on_ready():
            logger.info(f"musicatri name: {ctx.bot_instance.user}; musicatri id: {ctx.bot_instance.user.id}")
            ctx.bot_eventbus.emit(AtriEvent.READY)
            ctx.update_state(BotStarted())  # 启动状态

        async def async_start():  # 异步启动亚托莉
            try:
                await ctx.bot_instance.start(bot_token, reconnect=False)  # 尝试启动亚托莉
            except Exception as e:  # 亚托莉登录失败
                ctx.bot_eventbus.emit(AtriEvent.CONNECT_FAILED, str(e))  # 亚托莉启动失败
                await ctx.bot_instance.close()  # 关闭实例
                ctx.init_bot_instance()  # 重新初始化
                ctx.update_state(BotStopped())  # 恢复状态到stopped

        asyncio.run_coroutine_threadsafe(async_start(), ctx.bot_event_loop)

        _ = locale.get()
        return Result(200, _("submit musicatri launching workflow task"))  # 执行亚托莉启动工作流

    def stop(self, ctx: AtriContext):
        _ = locale.get()
        return Result(200, _("musicatri already stopped"))

    def terminate(self, ctx: AtriContext):
        ctx.bot_instance.close()  # 关闭资源


class BotStarted(AtriState):
    def __init__(self):
        super().__init__('started')

    """ 亚托莉已启动 """
    def start(self, ctx: AtriContext) -> Result:
        _ = locale.get()
        return Result(200, _('musicatri already started'))

    def stop(self, ctx: AtriContext) -> Result:
        """ 停止亚托莉 """
        ctx.update_state(BotStopping())   # 切换到stopping状态
        async def async_stop():  # 异步停止亚托莉
            _ = locale.get()
            try:
                await ctx.bot_instance.close()  # 尝试关闭亚托莉
                # ctx.bot_eventbus.emit(AtriEvent.CLOSE)
                # 切换亚托莉到初始状态
                # 机器人在调用close方法之后会话会被关闭，因此需要重新初始化机器人
                ctx.update_state(BotIdle())
            except Exception as e:  # 亚托莉退出失败
                ctx.bot_eventbus.emit(AtriEvent.DISCONNECT_FAILED, str(e))
                ctx.update_state(BotStarted())  # 恢复到原始状态

        _ = locale.get()
        asyncio.run_coroutine_threadsafe(async_stop(), ctx.bot_event_loop)  # 停止机器人协程
        return Result(200, _("submit musicatri shutdown workflow task"))  # 执行亚托莉停止工作流


class BotStopping(AtriState):  # 正在停止
    def __init__(self):
        super().__init__('stopping')

    """ 亚托莉等待状态 """
    def start(self, ctx: AtriContext):
        _ = locale.get()
        return Result(400, _('musicatri is still stopping'))

    def stop(self, ctx: AtriContext):
        _ = locale.get()
        return Result(400, _('musicatri is still stopping'))


class AtriStarting(AtriState):  # 正在启动
    def __init__(self):
        super().__init__('starting')


class AtriContext:
    bot_instance: Atri  # 亚托莉实例
    bot_eventbus: ExecutorEventEmitter  # 事件总线，用于传递事件
    bot_thread: Thread  # 运行线程，运行事件循环
    bot_event_loop: AbstractEventLoop  # 亚托莉

    def __init__(self):
        self.init_bot_instance()
        self.bot_eventbus = ExecutorEventEmitter()  # 事件总线
        self._state = None
        self.pre_initialize()  # 绑定事件
        self.update_state(BotThreadIdle())  # 初始化状态

    def start(self):
        return self.state.start(self)  # 启动亚托莉

    def stop(self):
        return self.state.stop(self)  # 停止亚托莉

    def initialize(self):
        return self.state.initialize(self)  # 启动线程

    def terminate(self):
        return self.state.terminate(self)  # 停止线程

    @property
    def identify(self):
        return self.state.identify

    @property
    def state(self) -> AtriState:
        return self._state

    @state.setter
    def state(self, state: AtriState):
        self._state = state

    def update_state(self, state: AtriState):
        if self.state: self.state.fadeout(self)  # 状态切出
        self.state = state  # 状态切入
        if self.state: self.state.enter(self)

    def pre_initialize(self):  # 挂载事件
        def handle_atri_state_change(identify):
            from auth_server.sockets.dispatcher import admin_socket_dispatcher
            # socketio.start_background_task(target=socketio.emit, event=SocketioEvent.ATRI_STATE_CHANGE, data=self.identify, namespace='/socket/admin')
            admin_socket_dispatcher.emit(SocketioEvent.ATRI_STATE_CHANGE, self.identify)
            logger.debug(f'musicatri change status to {identify}')
        self.bot_eventbus.on(AtriEvent.STATE_CHANGE, handle_atri_state_change)

        self.bot_eventbus.on(AtriEvent.CONNECT, lambda: logger.info("musicatri connect"))
        # self.bot_eventbus.on(AtriEvent.DISCONNECT, lambda: log.info("musicatri disconnect"))
        # self.bot_eventbus.on(AtriEvent.RECONNECT, lambda: log.info("musicatri reconnect"))
        self.bot_eventbus.on(AtriEvent.READY, lambda: logger.info("musicatri ready"))
        # self.bot_eventbus.on(AtriEvent.CLOSE, lambda: log.info("musicatri close"))

        self.bot_eventbus.on(AtriEvent.CONNECT_FAILED, lambda message: logger.error(message))
        self.bot_eventbus.on(AtriEvent.DISCONNECT_FAILED, lambda message: logger.error(message))

    def init_bot_instance(self, command_prefix: str= 'a', intents: Intents=Intents.all()):
        """ 初始化上下文的亚托莉对象 """
        bot = Atri(command_prefix=command_prefix, intents=intents)
        # todo: atri事件绑定
        @bot.event
        async def on_connect():
            self.bot_eventbus.emit(AtriEvent.CONNECT)

        @bot.event
        async def on_disconnect():
            self.bot_eventbus.emit(AtriEvent.DISCONNECT)

        # todo: atri命令绑定...
        @bot.command()
        async def add(ctx, left: int, right: int):
            await ctx.send(left + right)

        @bot.command()
        async def repeat(ctx, times: int, content='repeating...'):
            """Repeats a message multiple times."""
            for i in range(times):
                await ctx.send(content)

        self.bot_instance = bot


atri_context = AtriContext()