from http import HTTPStatus
from fastapi import HTTPException
from typing import Union
import asyncio
from db.dao.http_request import make_request
from settings import Settings
from db.dto import HunterIOReqDTO
from db.enums import EmailStatusesEnum
from loguru import logger


settings = Settings()


class ExternalAPIService:

    def __init__(self):
        self._http_client = make_request

    async def verify_email_hunter(self, email: str) -> Union[EmailStatusesEnum, str]:
        """Verifies email using hunter.io API;
        returns EmailStatusEnum"""
        logger.info("VerifyEmailHunter: Verify email with hunter IO")
        logger.trace(f"VerifyEmailHunter: Verify email: {email}")
        url = f"{settings.HUNTER_IO_API_HOST}{settings.HUNTER_IO_API_VERIFIER}"
        method = 'GET'
        query_params = HunterIOReqDTO(email=email, api_key=settings.HUNTER_IO_API_KEY).dict()

        response = await self.make_hunt_io_request(method, url, query_params)
        if response is None:
            return EmailStatusesEnum.FAILED
        else:
            logger.trace(f"VerifyEmailHunter: Response data from hunter io: {response}")
            verification_status = response["data"]["status"]
            logger.trace(f"VerifyEmailHunter: Email verification status: {verification_status}")
            if verification_status in EmailStatusesEnum._member_map_.values():
                return verification_status
            else:
                logger.warning(f"External API service: HUNTER IO:\
                 server verified email with unknown status: {verification_status};\
                 please update external API service in accordance with new API documentation")
                return EmailStatusesEnum.UNSTATED

    async def make_hunt_io_request(self, method: str, url: str, query_params: dict):
        """Makes request to Hunter.io API;
        API documentation: https://hunter.io/api-documentation/v2#email-verifier
        if request fails due to hunter IO subscription issues,
        returns None
        if request succeeds - returns response from Hunter io server
        if request fails due to external servers troubles after retries,
        or if request fails due to wrong email parameter provided by the user
        - raises HttpException
        """
        logger.info("MakeHuntRequest: Make request to hunter io")
        for _ in range(settings.HUNTER_IO_API_RETRY):
            resp_status, response = await self._http_client(method, url, query_params=query_params)
            logger.debug(f"MakeHuntRequest: response from hunt io server: {response}")
            if resp_status in (HTTPStatus.OK, HTTPStatus.UNAVAILABLE_FOR_LEGAL_REASONS):
                return response
            elif resp_status in (HTTPStatus.ACCEPTED, 222):
                await asyncio.sleep(settings.HUNTER_IO_API_SLEEP)
                continue
            else:
                break
        if resp_status in (HTTPStatus.ACCEPTED, 222):
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail="BAD REQUEST: the email cannot be verified, please try again later")
        elif resp_status == 400:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail="BAD_REQUEST: provided email is invalid")
        elif resp_status == HTTPStatus.TOO_MANY_REQUESTS:
            logger.warning(f"HUNTER IO: server response status {resp_status}: response: {response}")
            return None


external_api_service = ExternalAPIService()
