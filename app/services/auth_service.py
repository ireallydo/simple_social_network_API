from fastapi import HTTPException
from http import HTTPStatus
from db.dto import LoginRespDTO, RefreshTokenReqDTO, RefreshTokenRespDTO
from utils import auth_utils
from services.user_service import user_service
from loguru import logger


class AuthService:

    async def login_user(self, form_data) -> LoginRespDTO:
        logger.info("AuthService: Login user")
        logger.trace(f"AuthService: Login user: {form_data.username}")
        user = await user_service.get_by_login(form_data.username)
        if user is None:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail='Incorrect login or password')
        elif user.blocked:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail='User is blocked')
        elif not user.is_active:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail='User does not exist')
        if not auth_utils.verify_password(form_data.password, user.password):
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail='Incorrect login or password')
        access_token = await auth_utils.create_access_token(user.login)
        refresh_token = await auth_utils.create_refresh_token(user.login)
        resp = LoginRespDTO(access_token=access_token,
                            refresh_token=refresh_token,
                            user_id=user.id,
                            login=user.login,
                            role=user.role)
        return resp

    async def refresh_token(self, item: RefreshTokenReqDTO) -> RefreshTokenRespDTO:
        logger.info("AuthService: Refresh token")
        current_token = await auth_utils.verify_refresh_token(item.refresh_token)
        user = await user_service.get_by_login(current_token.sub)
        logger.trace(f"AuthService: Refresh token for user: {user.id}")
        if not user.is_active:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail="The user does not exist anymore")
        if user.blocked:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail="The user is blocked")
        access_token = await auth_utils.create_access_token(user.login)
        resp = RefreshTokenRespDTO(
            access_token=access_token,
            refresh_token=item.refresh_token
        )
        return resp


auth_service = AuthService()
