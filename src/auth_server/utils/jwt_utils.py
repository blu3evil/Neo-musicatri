import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"  # 建议从配置中加载
ALGORITHM = "HS256"
EXPIRES_IN_MINUTES = 60 * 24  # 1天

def create_jwt_token(user_id: str, roles: list[str]) -> str:
    payload = {
        "sub": user_id,
        "roles": roles,
        "exp": datetime.utcnow() + timedelta(minutes=EXPIRES_IN_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
