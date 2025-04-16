from server_bot.context import context
from common import Result

atri_context = context.atri_context

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
    def launch_atri():
        return atri_context.launch()

    @staticmethod
    def terminate_atri():
        return atri_context.terminate()

atri_service = AtriService()

