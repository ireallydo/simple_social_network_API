from db.models.LikeModel import LikeModel
from db.dto import LikesReqDTO
from .base_dao import BaseDAO


class LikeDAO(BaseDAO[LikeModel, LikesReqDTO, None, None]):
    pass


like_dao = LikeDAO(LikeModel)
