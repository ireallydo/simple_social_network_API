from typing import Union
from pydantic import BaseModel
from uuid import UUID
from db.enums import UserRolesSignupEnum


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None


class AuthHeadersDTO(BaseModel):
    user_id: Union[str, UUID]
    role: Union[str, UserRolesSignupEnum]
    login: str


class RefreshTokenReqDTO(BaseModel):
    refresh_token: str


class RefreshTokenRespDTO(RefreshTokenReqDTO):
    access_token: str


class LoginRespDTO(RefreshTokenRespDTO):
    user_id: Union[str, UUID]
    login: str
