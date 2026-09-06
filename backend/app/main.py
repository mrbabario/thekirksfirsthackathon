from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.db.database import Base, engine
from backend.app.routes.auth import router as auth_router

from backend.app.routes.fact_check import router as fact_check_router

# Import models so SQLAlchemy knows about them
from backend.app.models import user


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Dr.Kirk API",
    version="1.0.0",
)


# Allow Angular development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API routes
app.include_router(
    auth_router,
    prefix="/api",
)

app.include_router(
    fact_check_router,
    prefix="/api",
)

@app.get("/")
def root():
    return {
        "message": "Dr.Kirk API is running"
    }
