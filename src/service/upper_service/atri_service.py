"""
Musicatri音乐机器人业务层
"""
from abc import abstractmethod

from flask import Response


class AtriService:
    @abstractmethod
    async def start_atri(self) -> Response:
        """ 音乐机器人启动业务方法 """
        pass





















