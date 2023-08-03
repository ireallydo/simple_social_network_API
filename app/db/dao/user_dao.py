from db.models.UserModel import UserModel
from db.dto import UserCreateLineDTO, UserChangeProfileDTO
from .base_dao import BaseDAO


class UserDAO(BaseDAO[UserModel, UserCreateLineDTO, UserChangeProfileDTO, None]):
    pass


user_dao = UserDAO(UserModel)
