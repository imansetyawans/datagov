from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import identity, catalogue, connectors, scans

app = FastAPI(
    title="DataGov API",
    description="Data Governance Platform API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(identity.router, prefix="/api/v1")
app.include_router(catalogue.router, prefix="/api/v1")
app.include_router(connectors.router, prefix="/api/v1")
app.include_router(scans.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "DataGov API", "version": "1.0.0"}