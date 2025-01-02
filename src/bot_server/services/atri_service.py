from bot_server.bot.atri import atri_context
from common import Result

class AtriService:
    @staticmethod
    def start_atri():
        return atri_context.start()

    @staticmethod
    def get_atri_status():
        # 获取亚托莉状态
        return Result(200, data={
            'status': atri_context.identify
        })

    @staticmethod
    def stop_atri():
        return atri_context.stop()

    @staticmethod
    def initialize_atri():
        return atri_context.initialize()

    @staticmethod
    def terminate_atri():
        return atri_context.terminate()
    @staticmethod
    def playsongbyid(id):
        return atri_context.play(id)

atri_service = AtriService()

