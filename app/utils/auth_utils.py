from http import HTTPStatus
from fastapi import HTTPException
from passlib.context import CryptContext
from settings import Settings
from typing import Union, Any
from datetime import datetime, timedelta
from jose import jwt
from db.dto import TokenPayload
from loguru import logger


settings = Settings()


password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_context.verify(password, hashed_password)


async def get_exp_time(expiration_delta: timedelta, expire_minutes: timedelta) -> datetime:
    if expiration_delta is not None:
        expiration_delta = datetime.utcnow() + expiration_delta
    else:
        expiration_delta = datetime.utcnow() + expire_minutes
    return expiration_delta


async def create_access_token(subject: Union[str, Any], expiration_delta: timedelta = None) -> str:
    expiration_delta = await get_exp_time(expiration_delta, settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    encode_info = {"exp": expiration_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(encode_info, settings.JWT_KEY, settings.TOKEN_ALGO)
    return encoded_jwt


async def create_refresh_token(subject: Union[str, Any], expiration_delta: timedelta = None) -> str:
    expiration_delta = await get_exp_time(expiration_delta, settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    encode_info = {"exp": expiration_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(encode_info, settings.JWT_REFRESH_KEY, settings.TOKEN_ALGO)
    return encoded_jwt


async def decode_token(token: str, key: str = settings.JWT_KEY) -> TokenPayload:
    logger.info("AuthUtils: Decode token")
    try:
        payload = jwt.decode(token, key, algorithms=[settings.TOKEN_ALGO])
        token_data = TokenPayload(**payload)
        print(f"Token data from decode token: {token_data}")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="Unauthorized")
    except jwt.JWTError:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                            detail="Could not validate credentials")
    return token_data


async def verify_refresh_token(token: str) -> TokenPayload:
    return await decode_token(token, settings.JWT_REFRESH_KEY)
