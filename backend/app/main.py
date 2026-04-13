from fastapi import FastAPI
from sqlmodel import SQLModel
from app.db.session import engine
from contextlib import asynccontextmanager

from app.models.admin import Admin
from app.models.gpsping import GPSPing
from app.models.report import Report

from app.api import auth
from app.api import excel
from app.api import progress
from app.api import export
from app.api import report
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    print("Starting server")
    SQLModel.metadata.create_all(engine)
    yield
    print("Shutting down server")

app = FastAPI(title="Field Worker Tracking API",lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/admin", tags=["Admin Auth"])
app.include_router(excel.router, prefix="/admin", tags=["Excel"])
app.include_router(progress.router, prefix="/admin", tags=["Progress"])
app.include_router(export.router, prefix="/admin", tags=["Export"])
app.include_router(report.router, prefix="/admin", tags=["Report"])