from server_bot.bot.atri.context import BotAtriContext
from events import BotEvent
from server_bot.bot.atri.events import AtriEvent

def register_bot_event_listeners(ctx: BotAtriContext):
    # 注册事件监听，当状态变化时打印信息
    def handle_bot_state_change(identify):
        """ 处理机器人状态变化回调函数 """
        ctx.logger.info(f'atri state change to {identify}')
    ctx.bot_eventbus.on(BotEvent.STATE_CHANGE, handle_bot_state_change)

    def handle_voice_channel_connect(guild_id):
        """ 处理亚托莉连接到语音频道的回调函数 """
        ctx.logger.info(f'atri successfully connect to voice channel with guild id: {guild_id}')
    ctx.bot_eventbus.on(AtriEvent.VOICE_CHANNEL_CONNECT_SUCCESS, handle_voice_channel_connect)

    def handle_voice_channel_disconnect(guild_id):
        """ 处理亚托莉从语音频道断开 """
        ctx.logger.info(f'atri disconnect from voice channel with guild id: {guild_id}')
    ctx.bot_eventbus.on(AtriEvent.VOICE_CHANNEL_DISCONNECT_SUCCESS, handle_voice_channel_disconnect)

    def handle_song_play_success(guild_id):
        """ 处理音乐播放回调 """
        ctx.logger.info(f'atri play song with guild id: {guild_id}')
    ctx.bot_eventbus.on(AtriEvent.SONG_PLAY_SUCCESS, handle_song_play_success)

    def handle_song_play_done():
        """ 处理音乐播放完成 """
        ctx.logger.debug(f'atri done playing a song!')
    ctx.bot_eventbus.on(AtriEvent.SONG_PLAY_DONE, handle_song_play_done)

