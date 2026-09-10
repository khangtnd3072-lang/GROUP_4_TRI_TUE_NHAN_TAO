from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings


app = FastAPI(
    title=settings.APP_NAME,
    version="2.0.0",
    description="Backend FastAPI cho hệ thống lập lịch học thông minh sử dụng Genetic Algorithm.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix=settings.API_PREFIX)


@app.get("/health")
def health():
    return {"status": "ok", "service": settings.APP_NAME}
