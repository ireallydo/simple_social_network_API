from typing import Union, Optional, List
from pydantic import BaseModel, AnyUrl
from datetime import datetime
from uuid import UUID


class PostBaseDTO(BaseModel):
    class Config:
        orm_mode = True


class PostDTO(PostBaseDTO):
    id: Union[str, UUID]
    user_id: Optional[Union[str, UUID]]
    likes: int
    liked_by: Optional[List]
    created_at: Union[str, datetime]
    updated_at: Union[str, datetime]
    text: Optional[str]


class PostRespDTO(PostDTO):
    image: Optional[AnyUrl]


class LikesPostReqDTO(PostBaseDTO):
    likes: int


class LikesReqDTO(PostBaseDTO):
    user_id: Union[str, UUID]
    post_id: Union[str, UUID]


class LikesRespDTO(PostBaseDTO):
    id: Union[str, UUID]
    likes: int
    liked_by: Optional[List]
