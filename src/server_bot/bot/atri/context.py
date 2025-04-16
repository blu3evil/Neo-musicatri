from __future__ import annotations

from pathlib import Path
from pyee.executor import ExecutorEventEmitter
from utils.context import DiscordBotContextV1, BotInstance
from discord import VoiceClient

class BotAtriContextConfigKey:
    SONGCACHE_FILE_DIRECTORY = 'application.bot.songcache.file-directory'

class BotAtriContext(DiscordBotContextV1):
    voice_clients: dict[int, VoiceClient] = {}  # 当前机器人加入到的语音频道中的voice_client实例

    def __init__(self):
        super().__init__(namespace='bot-atri', command_prefix='atri')
        self.voice_clients = {}
        self.config_schema['application']['schema']['bot']['schema']['songcache'] = {
            'type': 'dict',
            'schema': {
                'file-directory': {'type': 'string', 'default': 'songcache'}  # 本地文件缓存
            }
        }

    def on_init(self):
        """ 初始化函数 """
        super().on_init()
        self._init_songcache_directory()  # 初始化音乐缓存目录

    def _init_songcache_directory(self):
        """ 初始化音乐缓存目录 """
        songcache_file_directory = self.config.get(BotAtriContextConfigKey.SONGCACHE_FILE_DIRECTORY)
        self.ensure_temp_directory(Path(songcache_file_directory))

    def init_bot_command(self, bot: BotInstance):
        """ 初始化亚托莉命令 """
        from server_bot.bot.atri.commands import register_bot_command
        register_bot_command(self)  # 执行注册

    def init_bot_event_listener(self, eventbus: ExecutorEventEmitter):
        """ 初始化机器人事件监听器 """
        from server_bot.bot.atri.listeners import register_bot_event_listeners
        register_bot_event_listeners(self)  # 执行注册

    @property
    def songcache_directory_path(self) -> Path:
        """ 音乐缓存目录，机器人将音乐文件(.mp3)格式缓存在此处 """
        songcache_file_directory = self.config.get(BotAtriContextConfigKey.SONGCACHE_FILE_DIRECTORY)
        return self.temp_directory_path / songcache_file_directory
