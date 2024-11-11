from utils import cache
from domains import db, copy, DiscordUser, to_dict


user_info_prefix = 'user_info'

def save_user(data: dict):
    """ 写入或者更新用户 """
    user = db.session.get(data['id'])
    if not user:
        # 用户不存在，创建新的用户数据
        user = DiscordUser()
        copy(data, user)
        db.session.add(user)
        db.session.commit()
    else:
        # 用户已经存在，更新数据
        copy(data, user)
        db.session.commit()
    cache.set(f'{user_info_prefix}:{user.id}', to_dict(user))  # 将用户数据写入缓存

def get_user(user_id):
    """ 获取用户数据 """
    data = cache.get(f'{user_info_prefix}:{user_id}')
    if data: return data  # 缓存存在用户数据直接返回

    # 缓存不存在，从数据库查询
    user = db.session.query(DiscordUser).get(user_id)
    if user:  # 用户存在，缓存数据
        data = to_dict(user)
        cache.set(f'{user_info_prefix}:{user_id}', data)
        return data
    return {}  # 用户不存在

def exist_user(user_id):
    """ 判断用户是否存在于数据库当中，不查询缓存 """
    user = db.session.query(DiscordUser).get(user_id)
    return user is not None






