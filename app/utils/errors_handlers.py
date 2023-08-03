from loguru import logger
from http import HTTPStatus
from fastapi import HTTPException
import sqlalchemy.exc

def Error_Handler(func):
    def inner_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlalchemy.exc.DBAPIError as e:
            logger.exception(e)
            err = HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='INTERNAL SERVER ERROR')
            logger.exception(err)
            raise err
    return inner_func
