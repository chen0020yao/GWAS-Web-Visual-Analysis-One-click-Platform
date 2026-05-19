from jose import jwt
from datetime import datetime, timedelta

SECRET = "gwas_secret"

def create_token(data: dict):
    return jwt.encode(
        {**data, "exp": datetime.utcnow() + timedelta(hours=12)},
        SECRET,
        algorithm="HS256"
    )