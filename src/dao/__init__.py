from .models import DiscordUser, Role, UserRole
from core import db

def copy_properties(data, instance):
    """ 属性拷贝 """
    if isinstance(data, dict):
        # 如果是字典，则按键值对赋值
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
    elif hasattr(data, '__dict__'):
        # 如果是对象，则按属性名称赋值
        for key, value in data.__dict__.items():
            if hasattr(instance, key) and not key.startswith('_'):
                setattr(instance, key, value)

def to_dict(instance) -> dict:
    if isinstance(instance, db.Model):
        data = {}
        for column in instance.__table__.columns:
            data[column.name] = getattr(instance, column.name)
        return data
    return {}


__all__ = [copy_properties, DiscordUser, to_dict, Role, UserRole]



