from enum import Enum


class ApiSpec(str, Enum):

    REGISTRATION = '/registration'

    AUTH = '/authentication'
    TOKEN = '/authentication/token'

    USERS_DETAILS = '/users/{user_id}'
    USERS_PROFILES = '/users/{user_id}/profile'

    POSTS = '/posts'
    POSTS_DETAILS = '/posts/{post_id}'
    POSTS_IMAGES = '/posts/{post_id}/images'
    POSTS_USERS = '/posts/users/{user_id}'
    # TODO: consider likes system with Redis
    POSTS_LIKES = '/posts/{post_id}/likes'
