from fastapi import FastAPI

from app.api import router


app = FastAPI(
    title="Retail Policy AI System",
    version="3.0 - Multi-Agent Architecture",
)

app.include_router(router)

