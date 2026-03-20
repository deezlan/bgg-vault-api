from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from app.database import engine, Base
from app.routers import games, collection, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BGG Vault API",
    description="A board game collection tracker and analytics API powered by BoardGameGeek data.",
    version="1.0.0"
)

# --- Exception Handlers ---

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return 422 with a clean message when request validation fails."""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append(f"{field}: {error['msg']}")
    return JSONResponse(
        status_code=422,
        content={"detail": errors}
    )

@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    """Return 400 with a clean message on database integrity errors."""
    return JSONResponse(
        status_code=400,
        content={"detail": "A database integrity error occurred. This record may already exist."}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all handler — return 500 as clean JSON instead of a raw traceback."""
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )

# --- Routers ---

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(games.router, prefix="/games", tags=["Games"])
app.include_router(collection.router, prefix="/collection", tags=["Collection"])

@app.get("/")
def root():
    return {"message": "Welcome to BGG Vault API"}