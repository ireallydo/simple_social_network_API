from http import HTTPStatus
from fastapi import APIRouter, HTTPException, Response
from fastapi_utils.cbv import cbv
from services.user_service import user_service
from db.dto import UserCreateDTO
from .api_spec import ApiSpec


router = APIRouter(tags=["registration"])


@cbv(router)
class RegistrationView:
    @router.post(ApiSpec.REGISTRATION, status_code=HTTPStatus.CREATED)
    async def create_user(self, input_data: UserCreateDTO):
        user, profile = await user_service.create_user(input_data)
        if user is None or profile is None:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                detail="INTERNAL_SERVER_ERROR")
        else:
            return Response(status_code=HTTPStatus.CREATED)
