from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, upload, rules, checks, reports

app = FastAPI(title="DataPulse", description="Data Quality Monitoring", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"])

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(upload.router, prefix="/api/datasets", tags=["Datasets"])
app.include_router(rules.router, prefix="/api/rules", tags=["Rules"])
app.include_router(checks.router, prefix="/api/checks", tags=["Checks"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])

@app.on_event("startup")
def on_startup():
    import app.models.user
    import app.models.dataset
    import app.models.rule
    import app.models.check_result
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"name": "DataPulse", "version": "1.0.0", "docs": "/docs"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
