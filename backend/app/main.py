# import os

# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse
# from sqlalchemy.exc import IntegrityError
# from fastapi.middleware.cors import CORSMiddleware

# from .routers import equipments, field_jobs, auth, farms
# from app.config import settings

# # FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")
# FRONTEND_ORIGIN = settings.frontend_origin


# app = FastAPI(
#     title = "Agricore Clinical Equipment Command Center",
#     description = "-",
#     version = "0.1.0"
# )

# # CORS Configuration
# app.add_middleware(
#     CORSMiddleware,
#     #The endpoint for our frontent, currently provided by the vite dev server
#     allow_origins=[FRONTEND_ORIGIN],
#     #This allows us to pass an Authorization header (JWT)
#     allow_credentials=True,
#     #This allows all methods and headers through
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

# # Include routers in API
# app.include_router(equipments.router)
# app.include_router(field_jobs.router)
# app.include_router(auth.router)
# app.include_router(farms.router)

# # Sample health endpoint to validate the application is running correctly.
# @app.get("/health", tags=["health"])
# async def health_check() -> dict[str, str]:
#     return {"status": "ok"}

# @app.exception_handler(IntegrityError)
# async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
#     return JSONResponse(
#         status_code=409,
#         content={"detail": "A database constraint was violated (e.g. a duplicate value)"},
#     )

# # ANY unexpected failure
# @app.exception_handler(Exception)
# async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
#     return JSONResponse(
#         status_code=500,
#         content={"detail": "An unexpected error has occured."},
#     )



import os

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

# from app.config import settings # UNCOMMENT/COMMENT AT SAME TIME

from .routers import equipments, field_jobs, auth, farms, service_reports, users

from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, require_role
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from app.models import FieldJob, FieldJobPriority, Operator, ServiceReport, FieldJobStatus, User, UserRole

FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")
# FRONTEND_ORIGIN = settings.frontend_origin # UNCOMMENT/COMMENT AT SAME TIME

app = FastAPI(
    title = "Agricore Equipment Command Center",
    description = "Management API for Prairie Crest Agricultural Cooperative",
    version = "0.1.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    #The endpoint for our frontent, currently provided by the vite dev server
    allow_origins=[FRONTEND_ORIGIN],
    #This allows us to pass an Authorization header (JWT)
    allow_credentials=True,
    #This allows all methods and headers through
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers in API
app.include_router(equipments.router)
app.include_router(field_jobs.router)
app.include_router(farms.router)
app.include_router(auth.router)
app.include_router(service_reports.router)
app.include_router(users.router)

# Sample health endpoint to validate the application is running correctly.
@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/version", tags=["health"])
async def version() -> dict[str, str]:
    return {"version": app.version}

# Stretch goal: Health Checks
@app.get("/health/ready", tags=["health"])
async def health_ready(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail={"status": "fail"})

@app.get("/health/detail", tags=["health"])
async def health_detail(db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.FARM_OPERATIONS_ADMIN))
                        ) -> dict[str, str]:
    db_status = "fail"
    s3_status = "fail"
    BUCKET_NAME = "robopulse-diagnostics-nd2478"
    s3_client = boto3.client("s3")

    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        pass

    try:
        s3_client.head_bucket(Bucket=BUCKET_NAME) # Apparently a sync problem, could block other user access if slow.
        s3_status = "ok"
    except (ClientError, BotoCoreError):
        pass

    return {"db_status": f"{db_status}", "s3_status": f"{s3_status}"}

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": "A database constraint was violated (e.g. a duplicate value)"},
    )

# ANY unexpected failure
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error has occured."},
    )