""" 更简洁的项目配置文件 """
import yaml
from cerberus import Validator

class Config:
    """ 项目配置类，通过Tag枚举类来更方便地获取项目配置 """
    def __init__(self, config_path, rule_schema: dict):
        self.configurations = {}  # 项目配置
        self.load_config(config_path, rule_schema)

    def _update_dicts(self, base_dict, new_dict):
        """
        更新字典，使用new_dict当中的键值更新old_dict当中的键值，此方法为深度拷贝
        注意此方法不会将仅new_dict中存在的值插入
        """
        base_dict_copy = base_dict.copy()
        for key, value in new_dict.items():

            if key in base_dict_copy:  # 仅key存在的时候执行更新
                if isinstance(value, dict) and isinstance(base_dict_copy[key], dict):
                    # 字典类型，执行递归拷贝
                    base_dict_copy[key] = self._update_dicts(base_dict_copy[key], value)
                elif value is not None:
                    # 一般类型，仅value存在执行更新
                    base_dict_copy[key] = value

        return base_dict_copy

    def build_empty_config_frame_from_schema(self, rule_schema):
        """
        基于cerberus定义的表单验证规则生成一份仅仅具备配置结构的空白骨架，并通过随后的用户配置
        以及默认配置完成配置构建
        """
        config_frame = self._do_build_empty_config_frame_from_schema({}, rule_schema)
        return config_frame

    def _do_build_empty_config_frame_from_schema(self, current_config, rule_schema: dict):
        """ 实际执行构建基础配置 """
        for field, field_schema in rule_schema.items():
            if field not in current_config:

                # 字段类型为dict，直接将字段初始化为字典，同时通过递归来初始化字典
                if field_schema['type'] == 'dict' and 'schema' in field_schema:
                    current_config[field] = {}
                    self._do_build_empty_config_frame_from_schema(current_config[field], field_schema['schema'])

                # 一般类型字段，对环境相关字段填充默认值，其余字段保持为空
                else:
                    if field == 'environment' and not current_config.get(field):
                        current_config[field] = 'global'  # 无名配置环默认境名为global
                    elif field == 'active-environment' and not current_config.get(field):
                        current_config[field] = 'global'  # 无激活环境名配置，默认激活环境为global

                    else: current_config[field] = None  # 默认赋值为空

        return current_config

    def load_config(self, config_path: str, rule_schema: dict):
        if config_path:  # 配置路径存在，加载配置
            with open(config_path, 'r', encoding='utf-8') as file:
                env_configs = list(yaml.safe_load_all(file))
        else:
            env_configs = []  # 配置路径不存在，返回空配置

        self._do_load_config(env_configs, rule_schema)

    def _do_load_config(self, env_configs: list, rule_schema: dict):
        """ 基于路径加载配置文件 """
        envname_config_map = {}  # 环境名到环境配置的映射 name -> env
        # env_configs 为空，使用骨架作为配置（即任何值都没有被定义）
        if not env_configs:
            env_configs = [self.build_empty_config_frame_from_schema(rule_schema)]

        for env_config in env_configs:  # 遍历所有环境
            config_frame = self.build_empty_config_frame_from_schema(rule_schema)  # 为每一份环境配置创建一份配置骨架
            extend_env_config = self._update_dicts(config_frame, env_config)  # 使用环境配置来更新骨架
            envname = extend_env_config['environment']  # 获取当前配置环境名进行存储进入字典

            if not envname_config_map.get(envname):
                envname_config_map[envname] = extend_env_config
            else:
                # 若环境已经存在那么执行覆盖，这能够避免一些同名环境被重复创建
                old_evn_config = envname_config_map[envname]
                new_env_config = self._update_dicts(old_evn_config, extend_env_config)
                envname_config_map[envname] = new_env_config

        try:
            global_config = envname_config_map['global']  # 获取全局环境
        except KeyError:
            raise RuntimeError("'global' config not found")  # global环境未定义

        # 使用校验器补齐缺失参数
        v = Validator(rule_schema, purge_unknown=True)

        active_env_config_name = global_config['active-environment']  # 获取激活环境名

        # 使用全局环境
        if active_env_config_name == 'global':
            configurations = global_config

        # 非全局激活环境，查找对应的环境
        else:
            try:
                active_env_config = envname_config_map[active_env_config_name]
            except KeyError:  # 未找到指定环境
                raise RuntimeError(f"'{active_env_config_name}' config not found")

            configurations = self._update_dicts(global_config, active_env_config)  # 使用环境配置覆盖全局配置

        self.configurations = v.normalized(configurations)  # 补齐默认值

    from typing import Any
    def get(self, tag) -> Any:
        """ 通过Tag标签获取项目配置 """
        keys = tag.split('.')
        value = self.configurations
        for key in keys:
            try:
                value = value[key]
            except KeyError:
                raise RuntimeError(f"{tag.name}({tag}) not found '{key}'")
        return value
