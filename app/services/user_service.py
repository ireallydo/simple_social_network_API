from http import HTTPStatus

import asyncpg.exceptions
from fastapi import HTTPException
from typing import Union, NoReturn
from datetime import datetime
import sqlalchemy
import sqlalchemy.exc
from db.models.UserModel import UserModel
from db.models.ProfileModel import ProfileModel
from db.dto import UserCreateDTO, UserCreateLineDTO, UserProfileDTO, \
    UserDeleteDTO, UserBlockDTO, UserChangeProfileDTO
from db.dao import user_dao, UserDAO, profile_dao, ProfileDAO
from db.enums import EmailStatusesEnum
from utils.auth_utils import hash_password
from .external_api_service import external_api_service
from loguru import logger


class UserService:

    def __init__(self, user_dao: UserDAO, profile_dao: ProfileDAO):
        self._user_dao = user_dao
        self._profile_dao = profile_dao
        self._external_api = external_api_service

    async def create_user(self, item: UserCreateDTO) -> tuple:
        logger.info("UserService: Create user")
        logger.trace(f"UserService: Create user with following passed data: {item}")
        # check if user with provided login or email already exists
        login_ex = await self._user_dao.get_by(login=item.login)
        if login_ex is not None:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail="Login is already used. Please choose different login.")
        email_ex = await self._user_dao.get_by(email=item.email)
        if email_ex is not None and email_ex.is_active:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail="User with this email already exists.")
        # check if provided email is a valid email address
        email_status = await external_api_service.verify_email_hunter(item.email)
        if email_status == EmailStatusesEnum.INVALID:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail="Cannot register user with provided email: email is invalid.")
        # change entered birthday format to db format
        item.birth_date = datetime.strptime(item.birth_date, '%d-%m-%Y')
        # hash password
        item.password = hash_password(item.password)
        # create object for user creation
        obj = UserCreateLineDTO(**item.dict())
        obj.email_status = email_status
        # create user
        try:
            user = await self._user_dao.create(obj)
        except sqlalchemy.exc.DBAPIError as e:
            logger.exception(e)
            if "invalid input for query argument" in str(e.orig):
                err = HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='BAD REQUEST (incorrect data provided)')
            else:
                err = HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='INTERNAL SERVER ERROR')
            logger.exception(err)
            raise err
        # create user profile
        profile = UserProfileDTO(**item.dict())
        profile.id = user.id
        try:
            user_profile = await self._profile_dao.create(profile)
        except sqlalchemy.exc.DBAPIError as e:
            logger.exception(e)
            if "invalid input for query argument" in str(e.orig):
                err = HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='BAD REQUEST (incorrect data provided)')
            else:
                err = HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='INTERNAL SERVER ERROR')
            logger.exception(err)
            raise err
        return user, user_profile

    async def get_user(self, user_id: str) -> UserModel:
        logger.info("UserService: Get user by user_id")
        logger.trace(f"UserService: Get user by user_id {user_id}")
        try:
            user = await self._user_dao.get_by_id(user_id)
        except sqlalchemy.exc.DBAPIError as e:
            logger.exception(e)
            if "invalid input for query argument" in str(e.orig):
                err = HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='BAD REQUEST (incorrect data provided)')
            else:
                err = HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='INTERNAL SERVER ERROR')
            logger.exception(err)
            raise err
        return user

    async def block_user(self, user_id: str, item: UserBlockDTO) -> UserModel:
        logger.info("UserService: Block user")
        logger.trace(f"UserService: Set blocked field to {item} for user with id {user_id}")
        patch_data = UserBlockDTO(blocked=item.blocked)
        try:
            return await self._user_dao.patch(patch_data, user_id)
        except sqlalchemy.exc.DBAPIError as e:
            logger.exception(e)
            if "invalid input for query argument" in str(e.orig):
                err = HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='BAD REQUEST (incorrect data provided)')
            else:
                err = HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='INTERNAL SERVER ERROR')
            logger.exception(err)
            raise err

    async def delete_user(self, user_id: str) -> NoReturn:
        logger.info("UserService: Delete user")
        logger.trace(f"UserService: Set is_active field to False for user with id {user_id}")
        patch_data = UserDeleteDTO(is_active=False, deleted_at=datetime.utcnow())
        try:
            await self._user_dao.patch(patch_data, user_id)
        except sqlalchemy.exc.DBAPIError as e:
            logger.exception(e)
            if "invalid input for query argument" in str(e.orig):
                err = HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='BAD REQUEST (incorrect data provided)')
            else:
                err = HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='INTERNAL SERVER ERROR')
            logger.exception(err)
            raise err

    async def get_user_profile(self, user_id: str) -> ProfileModel:
        logger.info("UserService: Get user profile by user_id")
        logger.trace(f"UserService: Get user profile by user_id {user_id}")
        try:
            profile = await self._profile_dao.get_by_id(user_id)
        except sqlalchemy.exc.DBAPIError as e:
            logger.exception(e)
            if "invalid input for query argument" in str(e.orig):
                err = HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='BAD REQUEST (incorrect data provided)')
            else:
                err = HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='INTERNAL SERVER ERROR')
            logger.exception(err)
            raise err
        return profile

    async def update_user_profile(self, user_id, item: UserChangeProfileDTO) -> ProfileModel:
        logger.info("UserService: Update user profile")
        logger.trace(f"UserService: Update profile of user with user_id {user_id} with data: {item}")
        try:
            if item.birth_date is not None:
                item.birth_date = datetime.strptime(item.birth_date, '%d-%m-%Y')
            profile = await self._profile_dao.patch(item, user_id)
        except sqlalchemy.exc.DBAPIError as e:
            logger.exception(e)
            if "invalid input for query argument" in str(e.orig):
                err = HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='BAD REQUEST (incorrect data provided)')
            else:
                err = HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='INTERNAL SERVER ERROR')
            logger.exception(err)
            raise err
        return profile

    async def get_by_login(self, login: str) -> Union[UserModel, None]:
        logger.info("UserService: Get user by login")
        logger.trace(f"UserService: Get user by login {login}")
        try:
            user = await self._user_dao.get_by(login=login)
        except sqlalchemy.exc.DBAPIError as e:
            logger.exception(e)
            err = HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='BAD REQUEST')
            logger.exception(err)
            raise err
        return user


user_service = UserService(user_dao, profile_dao)
