from discord import app_commands
import discord
from bot_server.bot.atri.context import BotAtriContext
from bot_server.bot.atri.events import AtriEvent

from typing import Any

def register_bot_command(ctx: BotAtriContext):
    """ 创建亚托莉命令组，命令为/atri """
    atri_command_group = app_commands.Group(name='atri', description='atri command group, top command')

    @app_commands.command(name="connect", description='connect atri to your current voice chanel')
    async def connect(interaction: discord.Interaction):
        """ 使亚托莉加入语音频道 """
        voice_state = interaction.user.voice
        if voice_state is None or voice_state.channel is None:
            # 当前用户没有处于任何语音频道
            await interaction.response.send_message('you are not in any voice channel, join a voice channel first')
            return

        _ = ctx.locale.get()
        guild = interaction.guild  # 执行命令时所在的组
        if not ctx.voice_clients.get(guild.id):
            # 并未建立voice_client，需要建立连接
            await voice_state.channel.connect()  # 加入到当前命令发送者所在的语音频道
            voice_client = discord.utils.get(ctx.bot_instance.voice_clients, guild=guild)  # 获取此组的语音频道

            # noinspection PyTypeChecker
            ctx.voice_clients[guild.id] = voice_client  # 建立guild_id到voice_client的映射
            await interaction.response.send_message(_('atri connects to voice channel successfully!'))
            ctx.bot_eventbus.emit(AtriEvent.VOICE_CHANNEL_CONNECT_SUCCESS, guild.id)  # 发送事件
            return

        await interaction.response.send_message(_('atri already connected to a voice channel!'))

    @app_commands.command(name='disconnect', description='disconnect atri from your current voice chanel')
    async def disconnect(interaction: discord.Interaction):
        """ 使亚托莉退出所在的语音频道 """
        guild = interaction.guild  # 执行命令时所在的组
        _ = ctx.locale.get()
        if not ctx.voice_clients.get(guild.id):
            # 亚托莉不处于任何语音频道当中
            await interaction.response.send_message(_('atri is currently not in any voice channel'))
            return

        voice_client = ctx.voice_clients[guild.id]
        await voice_client.disconnect()  # 退出语音频道
        ctx.voice_clients.pop(guild.id)  # 清理映射
        await interaction.response.send_message(_('atri disconnected from current voice channel!'))
        ctx.bot_eventbus.emit(AtriEvent.VOICE_CHANNEL_DISCONNECT_SUCCESS, guild.id)

    @app_commands.command(name='play', description='play a target song with specified id')
    @app_commands.describe(
        song_id='id of the song which you would like to play'
    )
    async def play(
            interaction: discord.Interaction,
            song_id: str='-1'
    ):
        """ 使亚托莉退出所在的语音频道 """
        guild = interaction.guild  # 执行命令时所在的组
        _ = ctx.locale.get()
        if not ctx.voice_clients.get(guild.id):
            # 亚托莉不处于任何语音频道当中
            await interaction.response.send_message(_('atri is currently not in any voice channel'))
            return

        voice_client = ctx.voice_clients[guild.id]
        song_file_path = ctx.songcache_directory_path / f'{song_id}.m4a'

        if not song_file_path.exists():
            # 指定id的音乐文件不存在
            await interaction.response.send_message(
                _('cannot found a song with specified id {song_id}!')
                .format(song_id=song_id))
            return

        def handle_song_play_done(exception: Exception | None) -> Any:
            """ 处理音乐播放完成 """
            ctx.bot_eventbus.emit(AtriEvent.SONG_PLAY_DONE)
        voice_client.play(discord.FFmpegPCMAudio(str(song_file_path)), after=handle_song_play_done)  # 播放音乐
        await interaction.response.send_message(_('successfully play song with id {song_id}!').format(song_id=song_id))
        ctx.bot_eventbus.emit(AtriEvent.SONG_PLAY_SUCCESS, guild.id)

    # @app_commands.command(name='play', description='play a target song with specified id')
    # @app_commands.describe(
    #     song_id='id of the song which you would like to play'
    # )
    # async def stop(interaction: discord.Interaction):
    #     """ 停止亚托莉当前正在播放的音乐 """

    atri_command_group.add_command(connect)
    atri_command_group.add_command(disconnect)
    atri_command_group.add_command(play)

    async def setup_bot():
        """ 初始化亚托莉命令组 """
        ctx.bot_instance.tree.add_command(atri_command_group)
        await ctx.bot_instance.tree.sync()

    ctx.bot_instance.setup_hook = setup_bot

