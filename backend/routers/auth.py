from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
import models, schemas
from database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_current_user(
    x_user_id: int = Header(None, alias="X-User-Id"),
    db: Session = Depends(get_db)
):
    if x_user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Missing X-User-Id header"
        )

    user = db.query(models.User).filter(models.User.id == x_user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


@router.post("/register", status_code=200)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if existing:
        raise HTTPException(400, "Username already exists")

    new_user = models.User(
        username=user.username,
        password=user.password,  # hash in production
        role=user.role,
        full_name=user.full_name,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": f"{user.role.capitalize()} registered successfully",
        "user_id": new_user.id
    }


@router.post("/login")
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if not db_user or db_user.password != user.password:
        raise HTTPException(401, "Invalid credentials")

    return {
        "message": "Login successful",
        "user_id": db_user.id,
        "username": db_user.username,
        "role": db_user.role,
    }
