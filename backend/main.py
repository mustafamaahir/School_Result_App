# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import auth, results  # use actual module names
from backend.database import Base, engine
from dotenv import load_dotenv

load_dotenv()


# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="School Result Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def home():
    return {"message": "Welcome to School Result API"}

# routers already define their own prefixes inside their files,
# so include them without an extra prefix here.
app.include_router(auth.router)
app.include_router(results.router)
