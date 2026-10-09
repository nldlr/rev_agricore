import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

# Security Constants and helper functions for password hashing and JWTW token management
SECRET_KEY = os.environ.get("SECRET_KEY", "<replace-with-real-secret-key>")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = .1
REFRESH_TOKEN_EXPIRE_MINUTES = 360

# With bcrypt, deterministically irreversibly hashes a password.
def hash_password(plain_password: str) -> str:
    # .encode = convert to raw bytes for bcrypt, .gensalt = unique salt so identical passwords masked
    # .hashpw = hashes salted password, .decode = convert raw bytes back to utf-8 string format.
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")

# With bcrypt, will compare the test hashpassword against the target hashpassword.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

# JWT (JSON Web Tokens) Generation
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    # Example data: data={"sub": user.username, "role": user.role.value}
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # to_encode["exp"] = expire
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + (
        timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    )
    
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    response = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    if response.get("type") != "access":
        raise jwt.PyJWTError("Invalid token type: Expected Access Token")
    return response


def decode_refresh_token(token: str) -> dict:
    response = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    if response.get("type") != "refresh":
        raise jwt.PyJWTError("Invalid token type: Expected Refresh Token")
    return response


# JWT (Header, Payload, Signature)
# Header: type of token (JWT), signing algorithm (HS256)
# Payload: Claims (in this case, sub/exp, role?), Note: Never put secret info here, is public readable
# Signature: Header + Payload + Secret + Algo = Signature