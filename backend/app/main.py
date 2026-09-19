from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.core.config import settings
from app.db.database import Base, engine
from app.schools.router import router as schools_router
from app.documents.router import router as documents_router
from app.normative.router import router as normative_router

app = FastAPI(
    title="SchoolNorm API",
    description="Платформа нормативного сопровождения образовательных организаций",
    version="0.1.0",
)
app.include_router(normative_router)
# Явно добавляем оба адреса для локальной разработки
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

# Добавляем origins из настроек, если они есть
if settings.cors_origins:
    for origin in settings.cors_origins.split(","):
        clean_origin = origin.strip()
        if clean_origin and clean_origin not in origins:
            origins.append(clean_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(schools_router)
app.include_router(documents_router)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "schoolnorm-api",
    }