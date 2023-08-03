from fastapi import Depends, Request
from http import HTTPStatus
from fastapi import HTTPException
from loguru import logger
from db.dto import AuthHeadersDTO
from utils.auth_utils import decode_token
from services.user_service import user_service
from settings import Settings


settings = Settings()


async def get_auth_headers(request: Request) -> AuthHeadersDTO:
    logger.info("AuthMixin: get auth headers from request")
    headers_check = request.headers.items()
    for item in headers_check:
        if item[0] == 'authorization':
            token = item[1].strip().split(" ")[-1]
            break
        elif item == headers_check[-1]:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Did not get credentials.')
    token_data = await decode_token(token)
    print(f"Token: {token}")
    print(f"Token Data: {token_data}")
    user = await user_service.get_by_login(token_data.sub)
    if not user.is_active:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail="The user does not exist anymore")
    resp = AuthHeadersDTO(
        user_id=user.id,
        login=user.login,
        role=user.role
    )
    return resp


class AuthMixin:
    auth_headers: AuthHeadersDTO = Depends(get_auth_headers)
