from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import ALLOWED_ORIGINS, setup_logging
from app.database import init_db
from app.api import connectors, policies, suites, testcases, runs, dashboard

setup_logging()

app = FastAPI(
    title="AI Guardrail QA Framework",
    description="QA platform for testing guardrails on AI customer-support chatbots",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(connectors.router, prefix="/api/connectors", tags=["Connectors"])
app.include_router(policies.router, prefix="/api/policies", tags=["Guardrail Policies"])
app.include_router(suites.router, prefix="/api/suites", tags=["Test Suites"])
app.include_router(testcases.router, prefix="/api/testcases", tags=["Test Cases"])
app.include_router(runs.router, prefix="/api/runs", tags=["Test Runs"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}
