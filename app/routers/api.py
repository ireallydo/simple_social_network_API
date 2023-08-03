from fastapi import APIRouter
from . import authentication, registration, users, posts


api_router = APIRouter()

endpoints = [authentication, registration, users, posts]

for endpoint in endpoints:
    api_router.include_router(endpoint.router)
