from bson import ObjectId

import domains
from modo.base_domain import BaseDomain
from typing import Type, Dict, TypeVar, Optional
from utils.locale import default_locale as _
from utils import log

T = TypeVar('T', bound='BaseDomain')  # 返回值上界
class MongodbEntityAdaptor:
    """
    Mongodb实体类适配器，支持将实体类转换为Mongodb文档格式，也支持将
    Mongodb文档格式反序列化成为实体类
    """
    @staticmethod
    def serialize(domain: BaseDomain) -> Dict:
        """ 将对象序列化为Mongodb文档的格式 """
        data = domains.copy()  # 获取原始字典
        if 'id' in data and data['id'] is not None and data['id'] != '':
            data['_id'] = data.pop('id')  # 若字典存在id字段，则使用id作为文档id

        return data

    @staticmethod
    def deserialize(document: Dict[str, any], clazz: Type[T]) -> Optional[T]:
        """
        将Mongodb文档反序列化为指定BaseDomain
        * 注: 反序列化采用反射实现，因此对于性能敏感的场景应考虑是否手动构建domain对象
        """
        if not issubclass(clazz, BaseDomain):  # 类型检查
            raise TypeError(_("mongo entity adaptor error: %(clazz)s must be a subclass of BaseEntity")
                            % {'clazz': clazz.__name__})

        if not document: return None  # 未查询到文档时

        # 通过反射设置属性
        instance = clazz()
        for key, value in document.items():
            if key == '_id':
                setattr(instance, 'id', value)  # 将_id设置为id字段
                continue
            setattr(instance, key, value)  # 设置属性

        return instance  # 返回实例
