"""
系统业务类
"""
from abc import abstractmethod

from domain.vo.system_vo import SystemStatusVO, SystemConfigVO
from utils import HttpResult


class SystemService:
    @abstractmethod
    def status(self) -> HttpResult[SystemStatusVO]:
        """ 获取服务端健康状态 """
        pass

    @abstractmethod
    def config(self) -> HttpResult[SystemConfigVO]:
        """ 获取服务端配置信息 """
        pass
