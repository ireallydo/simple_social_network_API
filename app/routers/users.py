from http import HTTPStatus
from fastapi import APIRouter, Response
from fastapi_utils.cbv import cbv
from mixins import AuthMixin
from services.user_service import user_service
from db.dto import UserRespDTO, UserProfileDTO, UserChangeProfileDTO, UserBlockDTO
from .api_spec import ApiSpec
from utils.rights_restrictions import available_roles
from db.enums import UserRolesEnum as Roles


router = APIRouter(tags=["users"])


@cbv(router)
class UsersView(AuthMixin):

    @router.get(ApiSpec.USERS_DETAILS, status_code=HTTPStatus.OK, response_model=UserRespDTO)
    @available_roles(role=Roles.MODERATOR, self_action=True)
    async def get_user(self, user_id: str):
        return await user_service.get_user(user_id)

    @router.patch(ApiSpec.USERS_DETAILS, status_code=HTTPStatus.OK, response_model=UserRespDTO)
    @available_roles(role=Roles.MODERATOR)
    async def block_user(self, user_id: str, item: UserBlockDTO):
        return await user_service.block_user(user_id, item)

    @router.delete(ApiSpec.USERS_DETAILS, status_code=HTTPStatus.NO_CONTENT)
    @available_roles(role=Roles.ADMIN, self_action=True)
    async def delete_user(self, user_id: str):
        await user_service.delete_user(user_id)
        return Response(status_code=HTTPStatus.NO_CONTENT)

    @router.get(ApiSpec.USERS_PROFILES, status_code=HTTPStatus.OK, response_model=UserProfileDTO)
    @available_roles(role=Roles.USER)
    async def get_user_profile(self, user_id: str):
        return await user_service.get_user_profile(user_id)

    @router.patch(ApiSpec.USERS_PROFILES, status_code=HTTPStatus.OK, response_model=UserProfileDTO)
    @available_roles(role=Roles.USER, self_action=True)
    async def update_user_profile(self, user_id: str, input_data: UserChangeProfileDTO):
        return await user_service.update_user_profile(user_id, input_data)
