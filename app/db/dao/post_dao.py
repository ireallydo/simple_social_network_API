from db.models.PostModel import PostModel
from .base_dao import BaseDAO
from loguru import logger


class PostDAO(BaseDAO[PostModel, None, None, None]):
    pass
    # async def patch_post(self, item: dict, post_id: str) -> PostModel:
    #     logger.info(f"Post DAO: update db entry")



post_dao = PostDAO(PostModel)
