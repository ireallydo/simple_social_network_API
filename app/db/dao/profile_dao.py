from db.models.ProfileModel import ProfileModel
from db.dto import UserProfileDTO, UserChangeProfileDTO
from .base_dao import BaseDAO


class ProfileDAO(BaseDAO[ProfileModel, UserProfileDTO, UserChangeProfileDTO, None]):
    pass


profile_dao = ProfileDAO(ProfileModel)
