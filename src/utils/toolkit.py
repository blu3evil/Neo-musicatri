"""
工具包，最纯粹的工具包，保证不与其他包产生循环依赖
"""
import os
from enum import Enum
from typing import Type, Callable, Any, Dict
from cerberus import Validator

from pattern.singleton import BaseSingleton
from utils.logger import log
from utils.locale import ResourceUtils


class BaseConfigTag(Enum):
    def sensitive(self) -> bool:
        """ 配置项参数是否敏感 """
        return self.value.get('sensitive')

    def required(self) -> bool:
        """ 配置项是否必须 """
        return self.value.get('required')

    def default_val(self) -> any:
        """ 获取配置项默认值 """
        return self.value.get('default')

    def deprecated(self) -> bool:
        """ 获取配置是否已经被丢弃 """
        return self.value.get('deprecated')

    def type(self):
        """ 获取配置类型 """
        return self.value.get('type')

    @classmethod
    def get_schema(cls):
        schema = {}
        for tag in cls:
            # 规则定义
            rules = schema.copy()        # 浅克隆规则
            rules.pop('required', None)     # 删除自定义标签required
            rules.pop('sensitive', None)    # 删除自定义标签sensitive
            rules.pop('default', None)      # 删除自定义标签default
            rules.pop('deprecated', None)   # 删除自定义标签default
            schema[tag.name] = rules
        return schema  # 返回验证结构

# 默认日志策略实现
default_configuration_logging_strategy = {
    'on_missing': lambda config_type, config_tag: log.warning(
    "['%(config_type)s' configuration] : '%(config_tag)s' is missing."
    % {'config_tag': config_tag, 'config_type': config_type}),

    'on_deprecated': lambda config_type, config_tag: log.warning(
    "['%(config_type)s' configuration] : '%(config_tag)s' is deprecated."
    % {'config_tag': config_tag, 'config_type': config_type}),

    'on_invalid' : lambda config_type, config_tag, validator: log.warning(
    "['%(config_type)s' configuration] : '%(config_tag)s' is invalid, cause: %(error)s"
    % {'config_tag': config_tag, 'config_type': config_type, 'error': validator.errors}),

    'on_type_err' : lambda config_type, config_tag, target_type: log.warning(
    "['%(config_type)s' configuration] : '%(config_tag)s' got type error, target type is: %(target_type)s"
    % {'config_tag': config_tag, 'config_type': config_type, 'target_type': target_type})
}

class BaseConfig(BaseSingleton):
    """
    配置基类，可以通过继承这个类来为项目创建一份配置，配置的加载依赖于项目根目录同级的.env, config.json以及
    默认配置，它们的优先级由前到后依次降低

    每一个配置类绑定一个BaseConfigTag类存在，通过继承并定义BaseConfigTag的枚举实例，可以非常轻松的定义具有
    很强健壮性的配置属性
    """
    def __init__(self,
                 config_tag: Type[BaseConfigTag],
                 on_missing: Callable[[str, BaseConfigTag], None] = default_configuration_logging_strategy['on_missing'],
                 on_deprecated: Callable[[str, BaseConfigTag], None] = default_configuration_logging_strategy['on_deprecated'],
                 on_invalid: Callable[[str, BaseConfigTag, Validator], None] = default_configuration_logging_strategy['on_invalid'],
                 on_type_err: Callable[[str, BaseConfigTag, str], None] = default_configuration_logging_strategy['on_type_err']):

        # 加载.env环境变量，这一句仅仅在非docker环境生效
        import os
        from dotenv import load_dotenv
        if not os.path.exists('/.dockerenv') and not os.getenv('DEV_MODE'):
            # 在非docker环境下加载.env文件，加载/musicatri/.env
            dotenv_file = ResourceUtils.get_root_resource('.env')
            if os.path.exists(dotenv_file):  load_dotenv(dotenv_file)

        """ 初始化配置集合 """
        self.configurations = {}  # 配置项集合
        self.config_tag = config_tag
        self.validator = Validator(config_tag.get_schema())  # 配置校验器

        # 回调函数配置
        self.on_missing = on_missing
        self.on_deprecated = on_deprecated
        self.on_invalid = on_invalid
        self.on_type_err = on_type_err

    def load_default(self):
        """ 加载一份默认配置 """
        for tag in self.config_tag:
            def_val = tag.default_val()
            if self.validator.validate({tag.name: def_val}):
                self.configurations[tag] = def_val  # 参数合法
            else: self.on_invalid('default', tag, self.validator)

    def load_jsonfile(self, jsonfile_path: str):
        """
        加载config.json配置项
        @param jsonfile_path: config.json配置文件路径
        """
        # 尝试加载config.json配置文件
        with open(jsonfile_path, 'r', encoding="utf-8") as config_file:
            import json
            config_json = json.load(config_file)
            for tag in self.config_tag:
                if tag.required():  # 参数为必要参数
                    if tag.deprecated():  # 参数已经停用
                        self.on_deprecated('config.json', tag)

                    if tag.name in config_json:  # 遍历config.json
                        jsonf_val = config_json[tag.name]  # 读取参数
                        if self.validator.validate({tag.name: jsonf_val}):  # 参数校验
                            self.configurations[tag] = jsonf_val  # 参数合法
                            continue
                        self.on_invalid('config.json', tag, self.validator)  # 参数非法

                    else:  # 标签不存在于config文件中，并且为必要，添加进入确实标签列表
                        if tag.required():
                            self.on_missing('config.json', tag)


    def load_env(self):
        """ 加载环境变量 """
        for tag in self.config_tag:
            env_val = os.getenv(tag.name)
            if tag.required():  # 参数为必要参数
                if tag.deprecated():  # 参数已经停用
                    self.on_deprecated('.env', tag)

                # 检查参数是否存在
                if env_val is None or env_val == "":
                    self.on_missing('.env', tag)
                    continue

                # 参数存在，执行校验，对于环境加载需要类型转换，定义类型转换函数映射:
                type_mapping = {
                    'integer': int,
                    'float': float,
                    'boolean': lambda v: v.lower() in ['true', 'enable', 'yes'],
                }

                if tag.type() != 'string' and tag.type() in type_mapping:  # 对于非string类型需要执行转换
                    target_type = type_mapping[tag.type()]
                    try: env_val = target_type(env_val)  # 执行类型转换
                    except (TypeError, ValueError):
                        self.on_type_err('.env', tag, target_type)
                        continue

                if self.validator.validate({tag.name: env_val}):
                    self.configurations[tag] = env_val  # 参数合法
                    continue
                self.on_invalid('.env', tag, self.validator)  # 参数非法



    def get(self, tag: BaseConfigTag) -> Any:
        """ 通过配置文件获取参数 """
        return self.configurations.get(tag)

    def get_all(self) -> Dict[BaseConfigTag, Any]:
        """ 获取全部配置 """
        return self.configurations


