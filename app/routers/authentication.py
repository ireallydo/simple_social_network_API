from http import HTTPStatus
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_utils.cbv import cbv
from services.auth_service import auth_service
from db.models import *
from db.dto import LoginRespDTO, RefreshTokenRespDTO, RefreshTokenReqDTO
from .api_spec import ApiSpec

# TODO: reuse if resp is None to common exception
router = APIRouter(tags=["authentication"])


@cbv(router)
class AuthView:

    @router.post(ApiSpec.AUTH, status_code=HTTPStatus.OK, response_model=LoginRespDTO)
    async def login(self, form_data: OAuth2PasswordRequestForm = Depends()):
        resp = await auth_service.login_user(form_data)
        if resp is None:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                detail="INTERNAL_SERVER_ERROR")
        return resp

    @router.post(ApiSpec.TOKEN, status_code=HTTPStatus.OK, response_model=RefreshTokenRespDTO)
    async def refresh_token(self, input_data: RefreshTokenReqDTO):
        resp = await auth_service.refresh_token(input_data)
        if resp is None:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                detail="INTERNAL_SERVER_ERROR")
        return resp
