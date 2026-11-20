from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

SECRET_KEY = "my-secret-key-change-this"
ALGORITHM = "HS256"


def create_access_token(username: str):

    expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    payload = {
        "sub": username,
        "exp": expire
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload.get("sub")

    except JWTError:
        return None
