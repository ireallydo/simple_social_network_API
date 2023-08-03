from aiohttp import ClientResponse
from clients import http_client
from pydantic import BaseModel
from typing import Type, Tuple
from loguru import logger


async def make_request(method: str, url: str, payload: Type[BaseModel] = None,
                       headers: dict = None, query_params: dict = None) -> Tuple[int, str]:
    logger.info("MakeHTTPRequest: Make HTTP request to external server")
    logger.trace(f"MakeHTTPRequest: Make {method} request to: {url} with payload: {payload},\
    query params: {query_params} and headers: {headers}")
    if query_params is not None:
        url = url.format(**query_params)
    payload = dict(payload) if payload is not None else {}
    headers = headers if not None else {}
    status, response_body = await http_client.request(method, url, payload, headers)
    return status, response_body
