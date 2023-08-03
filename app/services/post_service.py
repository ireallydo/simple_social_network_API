from http import HTTPStatus
from fastapi import HTTPException
import sqlalchemy.exc
from typing import NoReturn, List
from db.models.PostModel import PostModel
from db.dao import post_dao, PostDAO, like_dao, LikeDAO
from db.dto import AuthHeadersDTO, PostRespDTO,\
    PostDTO, LikesPostReqDTO, LikesReqDTO, LikesRespDTO
from settings import Settings
from routers.api_spec import ApiSpec
from utils.errors_handlers import Error_Handler
from loguru import logger


class PostService:

    def __init__(self, post_dao: PostDAO, like_dao: LikeDAO):
        self._post_dao = post_dao
        self._like_dao = like_dao
        self._settings = Settings()
        self._image_basic_url = f"{self._settings.HOST}:{self._settings.PORT}{ApiSpec.POSTS_IMAGES}"

    async def create_post(self, auth_headers: AuthHeadersDTO, text: str = None, image: bytes = None) -> PostModel:
        logger.info("PostService: Create post")
        logger.trace(f"PostService: Create post from user with id: {auth_headers.user_id}")
        # pydantic has issues with bytes objects encoding, so here Pydantic model isn't used as DTO
        # the python dictionary is used instead
        post_db = await self._post_dao.create({"user_id": auth_headers.user_id,
                                                "text": text,
                                                "image": image})
        # post is returned without an image, image can be requested separately
        post = PostDTO(**post_db.dict())
        post = PostRespDTO(**post.dict())
        post.image = self._image_basic_url.format(post_id=post.id)
        post.liked_by = post_db.liked_by
        return post

    @Error_Handler
    async def get_all_posts(self, *args, **kwargs) -> List[PostModel]:
        logger.info("PostService: Get all posts with limit and offset")
        posts = await self._post_dao.get_all_by(*args, **kwargs)
        response = []
        if posts:
            for post_db in posts:
                post = PostDTO(**post_db.dict())
                post = PostRespDTO(**post.dict())
                post.image = self._image_basic_url.format(post_id=post.id)
                post.liked_by = post_db.liked_by
                response.append(post)
        return response

    @Error_Handler
    async def get_post(self, post_id: str) -> PostRespDTO:
        logger.info("PostService: Get post by post_id")
        logger.trace(f"PostService: Get post by post_id: {post_id}")
        try:
            post_db = await self._post_dao.get_by_id(post_id)
        except sqlalchemy.exc.DBAPIError as e:
            logger.exception(e)
            err = HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='BAD REQUEST: no post with provided id')
            logger.exception(err)
            raise err
        post = PostDTO(**post_db.dict())
        post = PostRespDTO(**post.dict())
        post.image = self._image_basic_url.format(post_id=post.id)
        post.liked_by = [like.user_id for like in post_db.liked_by]
        return post

    @Error_Handler
    async def get_post_image(self, post_id: str) -> bytes:
        logger.info("PostService: Get post image by post_id")
        logger.trace(f"PostService: Get post image by post_id: {post_id}")
        post = await self._post_dao.get_by_id(post_id)
        return post.image

    @Error_Handler
    async def update_post(self, auth_headers: AuthHeadersDTO, post_id: str,
                          text: str = None, image: bytes = None) -> PostRespDTO:
        logger.info("PostService: Update post")
        logger.trace(f"PostService: Update post with post_id: {post_id}")
        # check if requesting ia authorized to update post
        await self.check_owner_rights(post_id, auth_headers.user_id)
        # we cannot use exclude_unset in base_dao as we don't use Pydantic model here
        # (bc Pydantic has issues with bytes object of image)
        # so we make a special method in post_dao and need to exclude unset vars manually
        if text is None and image is None:
            item = {}
        elif text is None:
            item = {"image": image}
        elif image is None:
            item = {"text": text}
        else:
            item = {"text": text,
                    "image": image}
        post_db = await self._post_dao.patch(item, post_id)
        post = PostDTO(**post_db.dict())
        post = PostRespDTO(**post.dict())
        post.image = self._image_basic_url.format(post_id=post.id)
        post.liked_by = [like.user_id for like in post_db.liked_by]
        return post

    @Error_Handler
    async def delete_post(self, auth_headers: AuthHeadersDTO, post_id: str) -> NoReturn:
        logger.info("PostService: Delete post")
        logger.trace(f"PostService: Delete post with post_id: {post_id}")
        # check if requesting user is authorized to delete post
        await self.check_owner_rights(post_id, auth_headers.user_id)
        await self._post_dao.delete(post_id)

    @Error_Handler
    async def like_post(self, auth_headers: AuthHeadersDTO, post_id: str) -> LikesRespDTO:
        logger.info("PostService: Like a post")
        logger.trace(f"PostService: Like a post with id: {post_id} by user with id: {auth_headers.user_id}")
        # check if user is authorized to like a post (can like only other users' posts, not its own)
        await self.check_owner_rights(post_id, auth_headers.user_id, False)
        post_is_liked = await self._like_dao.get_by(user_id=auth_headers.user_id, post_id=post_id)
        if post_is_liked is not None:
            err = HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='BAD REQUEST: post is already liked by user')
            logger.exception(err)
            raise err
        # TODO: change to using Redis instead
        post = await self.get_post(post_id)

        item = LikesPostReqDTO(likes=post.likes + 1)
        like_post = await self._post_dao.patch(item, post_id)
        logger.trace(f"PostService: Like a post: post with id: {post_id} - likes counter is updated")

        item = LikesReqDTO(
            user_id=auth_headers.user_id,
            post_id=post_id
        )
        await self._like_dao.create(item)
        logger.trace(f"PostService: Like a post: post with id: {post_id} - like is added")
        # TODO: roll back changes to posts table

        resp = LikesRespDTO(**like_post.dict())
        liked_post = await self._post_dao.get_by_id(post_id)
        likes = [like.user_id for like in liked_post.liked_by]
        resp.liked_by = likes
        return resp

    async def check_owner_rights(self, post_id: str, user_id: str, flag: bool = True) -> bool:
        """Checks if the user_id of the post owner is equal/not equal requesting user id;
        asserts for equality by default or if 'flag' argument is set to 'True';
        asserts for inequality if 'flag' argument is set to 'False'"""
        logger.info("PostService: Check if post owner is requesting to perform an action")
        logger.trace(
            f"PostService: Check if user_id {user_id} is authorized to perform an action on post: {post_id}")
        post = await self.get_post(post_id)
        try:
            if flag:
                assert(post.user_id == user_id)
            else:
                assert(post.user_id != user_id)
            return True
        except AssertionError as e:
            logger.exception(e)
            err = HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='FORBIDDEN')
            logger.exception(err)
            raise err


post_service = PostService(post_dao, like_dao)
