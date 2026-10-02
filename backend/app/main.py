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
#     title = "Medflow Clinical Equipment Command Center",
#     description = "Clinical Management API for Halcyon Health Systems",
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






from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import equipments, field_jobs, auth

app = FastAPI(
    title = "Agricore Equipment Command Center",
    description = "Management API for Prairie Crest Agricultural Cooperative",
    version = "0.1.0"
)

# # CORS Configuration
# app.add_middleware(
#     CORSMiddleware,
#     #The endpoint for our frontent, currently provided by the vite dev server
#     allow_origins=["http://localhost:5173"],
#     #This allows us to pass an Authorization header (JWT)
#     allow_credentials=True,
#     #This allows all methods and headers through
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

# Include routers in API
app.include_router(equipments.router)
app.include_router(field_jobs.router)
app.include_router(auth.router)

# Sample health endpoint to validate the application is running correctly.
@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}