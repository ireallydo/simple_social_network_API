from typing import Union, Optional
from pydantic import BaseModel
from datetime import datetime, date
from db.enums import EmailStatusesEnum, UserRolesSignupEnum
from uuid import UUID


class UserBaseDTO(BaseModel):
    class Config:
        orm_mode = True


class UserDTO(UserBaseDTO):
    first_name: str
    second_name: Optional[str]
    last_name: str
    birth_date: Union[str, date]
    about: Optional[str]


class UserProfileDTO(UserDTO):
    id: Optional[Union[UUID, str]]


class UserCreateDTO(UserDTO):
    login: str
    email: str
    password: str
    role: str


class UserRespDTO(UserBaseDTO):
    id: Union[UUID, str]
    login: str
    email: str
    email_status: EmailStatusesEnum
    role: UserRolesSignupEnum
    blocked: bool
    is_active: bool
    created_at: Union[str, datetime]
    updated_at: Union[str, datetime]
    deleted_at: Union[str, datetime, None]


class UserCreateLineDTO(BaseModel):
    login: str
    email: str
    password: str
    role: UserRolesSignupEnum
    email_status: Optional[EmailStatusesEnum]


class UserChangeProfileDTO(BaseModel):
    first_name: Optional[str]
    second_name: Optional[str]
    last_name: Optional[str]
    birth_date: Optional[Union[str, date]]
    about: Optional[str]


class UserBlockDTO(UserBaseDTO):
    blocked: bool


class UserDeleteDTO(UserBaseDTO):
    is_active: bool
    deleted_at: Union[str, datetime]
