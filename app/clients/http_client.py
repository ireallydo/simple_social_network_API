from typing import Optional
import aiohttp
import asyncio


async def request(method: str, url: str, payload: Optional[dict], headers: Optional[dict]) -> aiohttp.ClientResponse:
    session = aiohttp.ClientSession()
    try:
        async with session:
            response = await session.request(method, url, json=payload, headers=headers)
            # await session.close()
            resp = await response.json()
            return response.status, resp
    except TypeError:
        try:
            async with session:
                response = await session.request(method, url, data=payload, headers=headers)
                # await session.close()
                resp = await response.json()
                return response.status, resp
        except asyncio.TimeoutError as e:
            return e
    except asyncio.TimeoutError as e:
        return e
# TODO: change the exceptions system
