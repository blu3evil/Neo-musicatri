from __future__ import annotations

from typing import Union


class BaseDomain:
    """ 域模型基类，拥有序列化方法，可将对象序列化为json插入数据库 """
    def to_dict(self):
        """ 对公开属性进行json序列化，这个方法通常用于打印日志或者将数据插入数据库 """
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_')}

    @staticmethod
    def copy_properties(source: Union[dict, BaseDomain], to: BaseDomain):
        """
        遍历source字典，检查如果字典包含对象某个字段，那么将字段的值拷贝到对象
        参数说明:
          - target: 目标对象，将字典属性拷贝进入其中
          - source: 字典对象，包含需要拷贝的字段信息
        """
        if isinstance(source, dict):
            # 针对字典到domain的拷贝
            for key, value in source.items():
                if hasattr(to, key):
                    setattr(to, key, value)
        elif isinstance(source, BaseDomain):
            # 针对domain到domain的拷贝
            for key, value in source.to_dict().items():
                if hasattr(to, key):
                    setattr(to, key, value)

class BaseEntity(BaseDomain):
    """ 域对象 """
    pass

class BaseVO(BaseDomain):
    """ 视图对象 """
    pass

class BaseDTO(BaseDomain):
    """ 数据传递 """
    pass