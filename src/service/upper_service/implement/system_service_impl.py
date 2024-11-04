import time
from datetime import datetime

from domain.vo.system_vo import SystemStatusVO, SystemConfigVO
from service.upper_service.system_service import SystemService
from utils import default_locale as _, default_config, HttpResult, HttpCode, DefaultConfigTag
from utils.toolkit import BaseConfig

start_time = time.time()
created_at = datetime.now()

class SystemServiceImpl(SystemService):
    def status(self) -> HttpResult[SystemStatusVO]:
        """ 获得服务状态信息 """
        import time, math
        # 计算当前服务运行时长，使用math去除小数部分
        current_time = time.time()
        uptime = math.floor(current_time - start_time)

        # todo: 修改版本信息来源于resource_utils的config
        from utils.result import HttpCode, HttpResult

        # 构建Result
        vo = SystemStatusVO(
            uptime=uptime,
            created_at=created_at,
            version='1.0.0'
        )

        result = HttpResult[SystemStatusVO].success(HttpCode.SUCCESS, _("service_healthy"), vo)
        return result


    @staticmethod
    def __load_config(vo: SystemConfigVO, base_config: BaseConfig) -> SystemConfigVO:
        configurations = base_config.get_all()
        dev_mode = default_config.get(DefaultConfigTag.DEV_MODE)
        for configuration in configurations:
            if dev_mode: setattr(vo, configuration.name, configurations[configuration])
            elif configuration.sensitive(): setattr(vo, configuration.name, '...')
            else: setattr(vo, configuration.name, configurations[configuration])
        return vo

    def config(self) -> HttpResult[SystemConfigVO]:
        """ 获得服务配置文件详情信息 """
        from utils.config import default_config as def_cfg
        from utils.locale import locale_config as loc_cfg

        vo = SystemConfigVO()  # 构建配置文件信息
        self.__load_config(vo, def_cfg)  # 加载默认配置文件
        self.__load_config(vo, loc_cfg)  # 加载本地化配置文件

        # 构建Result对象
        result = HttpResult[SystemConfigVO].success(HttpCode.SUCCESS, HttpCode.SUCCESS.describe, vo)
        return result
