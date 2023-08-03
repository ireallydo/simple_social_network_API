from fastapi import FastAPI
from settings import Settings
from db.database import init_db, session
from routers.api import api_router
from utils.logger import setup_logger


settings = Settings()

app = FastAPI()
app.include_router(api_router)


@app.on_event("startup")
async def startup():
    setup_logger(settings)
    await init_db()


@app.on_event("shutdown")
async def shutdown():
    await session.aclose()


def main():
    run(app, port=settings.PORT)


if __name__ == "__main__":
    main()
