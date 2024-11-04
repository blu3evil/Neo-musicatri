"""
日志模块
"""
import logging
import sys

import colorlog
from colorlog import ColoredFormatter

# flask风格的控制台输出
FLASK_STYLE_CONSOLE_FORMATTER = ColoredFormatter(
    fmt='%(log_color)s%(levelname)s: %(asctime)s %(filename)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d,%H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'bold_yellow',
        'ERROR': 'bold_red',
        'CRITICAL': 'bold_red,bg_white',
    },
    secondary_log_colors={}, style='%',
    reset=True)

FLASK_STYLE_FILELOG_FORMATTER = logging.Formatter(
    fmt='%(levelname)s: %(asctime)s %(filename)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d,%H:%M:%S')

# 控制台日志输出默认格式
DEFAULT_CONSOLE_FORMATTER = ColoredFormatter(
    fmt='%(log_color)s%(asctime)s [%(levelname)s] %(name)s %(filename)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d,%H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'bold_yellow',
        'ERROR': 'bold_red',
        'CRITICAL': 'bold_red,bg_white',
    },
    secondary_log_colors={}, style='%',
    reset=True)

# 带有背景色的日志输出
BACKGROUND_RENDER_CONSOLE_FORMATTER = ColoredFormatter(
    fmt='%(log_color)s%(asctime)s [%(levelname)s] %(name)s %(filename)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d,%H:%M:%S',
    log_colors={
        'DEBUG': 'black,bg_white',
        'INFO': 'bg_green',
        'WARNING': 'bg_yellow',
        'ERROR': 'bg_red',
        'CRITICAL': 'bg_purple'
    },
    secondary_log_colors={}, style='%',
    reset=True)

# 日志文件输出默认格式
DEFAULT_FILELOG_FORMATTER = logging.Formatter(
    fmt='%(asctime)s [%(levelname)s] %(name)s %(filename)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d,%H:%M:%S')

class LoggerFactory(object):
    """ 日志创建工厂 """
    @staticmethod
    def create_basic_logger(log_name: str, level=logging.DEBUG, propagate=False) -> logging.Logger:
        logger = logging.getLogger(log_name)
        logger.propagate=propagate
        logger.setLevel(level)
        return logger

    @staticmethod
    def create_console_handler(level=logging.INFO, formatter=DEFAULT_CONSOLE_FORMATTER) -> logging.StreamHandler:
        """ 启用控制台日志输出并配置 """
        console_handler = colorlog.StreamHandler(sys.stdout)  # 使用utf-8
        console_handler.setLevel(max(level, logging.INFO))  # 设置日志等级
        console_handler.setFormatter(formatter)  # 设置输出样式
        return console_handler

    @staticmethod
    def create_logfile_handler(logfile_path: str, level=logging.DEBUG, formatter=DEFAULT_FILELOG_FORMATTER) -> logging. FileHandler:
        """ 启用日志文件输出并配置 """
        filelog_handler = logging.FileHandler(logfile_path, encoding='utf-8')  # 使用utf-8
        filelog_handler.setLevel(max(level, logging.DEBUG))  # 设置日志等级
        filelog_handler.setFormatter(formatter)  # 设置输出样式
        return filelog_handler

import time, os
from pattern.singleton import BaseSingleton
name_levels_mapping = logging.getLevelNamesMapping()

class SimpleLoggerFacade(BaseSingleton):
    """ 简单日志门户 """
    _instance = None
    console_handler: logging.StreamHandler  # 控制台日志输出
    logfile_handler: logging.FileHandler  # 文件日志输出
    logfile_path: str  # 日志路径
    logger: logging.Logger  # 日志实例

    def __init__(self):
        self.__init_logfile()  # 初始化日志文件
        self.__init_logger()  # 初始化日志

    def __init_logfile(self):
        """ 初始化日志文件 """
        current_file_path = os.path.abspath(__file__)  # 当前模块所在路径
        current_dir = os.path.dirname(current_file_path)  # 获取当前文件所在目录
        root_dir = os.path.dirname(os.path.dirname(current_dir))
        logs_dir = os.path.join(root_dir, 'logs')

        if not os.path.exists(logs_dir):  # 创建日志目录
            os.mkdir(logs_dir)

        self.logfile_path = SimpleLoggerFacade.__generate_logfile_name(logs_dir)

    def __init_logger(self):
        """ 使用默认配置初始化日志 """
        # 默认配置
        self.console_handler = LoggerFactory.create_console_handler(level=logging.DEBUG, formatter=FLASK_STYLE_CONSOLE_FORMATTER)
        self.logfile_handler = LoggerFactory.create_logfile_handler(self.logfile_path, level=logging.DEBUG, formatter=FLASK_STYLE_FILELOG_FORMATTER)

        self.logger = LoggerFactory.create_basic_logger(__name__, propagate=True, level=logging.DEBUG)
        self.logger.addHandler(self.console_handler)
        self.logger.addHandler(self.logfile_handler)

    # 主要用于在完成配置文件加载后再次配置日志
    def set_console_level(self, level="INFO"):
        """ 设置控制台日志等级 """
        level = name_levels_mapping.get(level, logging.INFO)
        self.console_handler.setLevel(level)

    def set_default_level(self, level="DEBUG"):
        """ 设置日志默认等级 """
        level = name_levels_mapping.get(level, logging.INFO)
        self.logger.setLevel(level)

    def set_logfile_level(self, level="DEBUG"):
        """ 设置日志文件日志等级 """
        level = name_levels_mapping.get(level, logging.INFO)
        self.logfile_handler.setLevel(level)

    @staticmethod
    def __generate_logfile_name(logfile_dir_path: str) -> str:
        """
        基于日志目录生成不会重复的日志文件名，外部使用这个方法来书写日志文件
        """
        current_time = int(round(time.time() * 1000))
        logfile_index = 1
        while True:
            logfile_naming_format = f"%Y-%m-%d-{logfile_index}.log"  # 日志文件命名模板
            logfile_name = time.strftime(logfile_naming_format, time.localtime(current_time / 1000))  # 构建日期时间赋值到日志文件名
            to_return = os.path.join(logfile_dir_path, logfile_name)  # 拼接日志路径
            if not os.path.exists(to_return):
                break
            logfile_index += 1  # 若配置文件已经存在那么继续添加索引号

        return to_return

    def get_logger(self):
        return self.logger

facade = SimpleLoggerFacade()  # 提供修改锚点
log = facade.get_logger()