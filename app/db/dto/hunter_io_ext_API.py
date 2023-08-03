from pydantic import BaseModel


class HunterIOReqDTO(BaseModel):
    email: str
    api_key: str
