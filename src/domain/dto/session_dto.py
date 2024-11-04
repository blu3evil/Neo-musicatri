from dataclasses import dataclass
from datetime import datetime

from domain.base_domain import BaseDTO

@dataclass
class TokenPayloadDTO(BaseDTO):
    """ 后端使用的认证JWT payload """
    user_id: int = None     # 用户id
    exp: datetime = None    # 过期时间

