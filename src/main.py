"""
Author: Yoosuf
Email: mayoosuf@gmail.com
Company: Crew Digital
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.config import settings
from src.core.logging_config import setup_logging
from src.modules.admin import router as admin_router
from src.modules.auth import router as auth_router
from src.modules.prompts import router as prompts_router
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    setup_logging()
    logger.info("Starting up...")
    yield
    # Shutdown logic
    logger.info("Shutting down...")


app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION, lifespan=lifespan)

# Include Routers
app.include_router(auth_router.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(admin_router.router, prefix=f"{settings.API_V1_STR}/admin", tags=["admin"])
app.include_router(prompts_router.router, prefix=f"{settings.API_V1_STR}", tags=["prompts"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
