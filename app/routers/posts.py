from http import HTTPStatus
from typing import List
from typing_extensions import Annotated
from fastapi import APIRouter, Response, Form, UploadFile
from fastapi.responses import StreamingResponse
from fastapi_utils.cbv import cbv
from mixins import AuthMixin
from services.post_service import post_service
from db.dto import PostRespDTO, LikesRespDTO
from .api_spec import ApiSpec
from utils.rights_restrictions import available_roles
from db.enums import UserRolesEnum as Roles
from io import BytesIO


router = APIRouter(tags=["posts"])


@cbv(router)
class PostsView(AuthMixin):

    @router.post(ApiSpec.POSTS, status_code=HTTPStatus.OK, response_model=PostRespDTO)
    @available_roles(role=Roles.USER)
    async def make_post(self, text: Annotated[str, Form()] = None, image: UploadFile = None):
        img = await image.read()
        return await post_service.create_post(self.auth_headers, text=text, image=img)

    @router.get(ApiSpec.POSTS, status_code=HTTPStatus.OK, response_model=List[PostRespDTO])
    @available_roles(role=Roles.USER)
    async def get_all_posts(self, limit: str = 100, offset: str = 0):
        return await post_service.get_all_posts(limit, offset)

    @router.get(ApiSpec.POSTS_DETAILS, status_code=HTTPStatus.OK, response_model=PostRespDTO)
    @available_roles(role=Roles.USER)
    async def get_post(self, post_id: str):
        return await post_service.get_post(post_id)

    @router.get(ApiSpec.POSTS_IMAGES, status_code=HTTPStatus.OK)
    @available_roles(role=Roles.USER)
    async def get_post_image(self, post_id: str):
        image = await post_service.get_post_image(post_id)
        return Response(content=image, media_type="image/jpeg")

    @router.patch(ApiSpec.POSTS_DETAILS, status_code=HTTPStatus.OK, response_model=PostRespDTO)
    @available_roles(role=Roles.USER)
    async def update_post(self, post_id: str, text: Annotated[str, Form()] = None, image: UploadFile = None):
        if image is not None:
            img = await image.read()
        else:
            img = image
        return await post_service.update_post(self.auth_headers, post_id, text, img)

    @router.delete(ApiSpec.POSTS_DETAILS, status_code=HTTPStatus.NO_CONTENT)
    @available_roles(role=Roles.USER)
    async def delete_post(self, post_id: str):
        await post_service.delete_post(self.auth_headers, post_id)
        return Response(status_code=HTTPStatus.NO_CONTENT)

    @router.get(ApiSpec.POSTS_USERS, status_code=HTTPStatus.OK, response_model=List[PostRespDTO])
    @available_roles(role=Roles.USER)
    async def get_user_posts(self, user_id: str, limit: str = 100, offset: str = 0):
        return await post_service.get_all_posts(limit, offset, user_id=user_id)

    @router.post(ApiSpec.POSTS_LIKES, status_code=HTTPStatus.OK, response_model=LikesRespDTO)
    @available_roles(role=Roles.USER)
    async def like_post(self, post_id: str):
        return await post_service.like_post(self.auth_headers, post_id)
