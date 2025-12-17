from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
import bcrypt
import csv

router = APIRouter(prefix="/auth", tags=["Authentication"])


# password hashing
def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


# password verification
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# get current user using header
def get_current_user(
    x_user_id: int = Header(None, alias="X-User-Id"),
    db: Session = Depends(get_db)
):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header")

    user = db.query(models.User).filter(models.User.id == x_user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# admin register single user
@router.post("/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = models.User(
        username=user.username,
        full_name=user.full_name,
        password=get_password_hash(user.password),
        role=user.role,
        must_change_password=True,
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id
    }


# bulk register students from csv
@router.post("/bulk-register-csv")
def bulk_register_from_csv(db: Session = Depends(get_db)):
    created_users = []

    try:
        with open("./students.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                username = row["username"].strip()

                exists = db.query(models.User).filter(
                    models.User.username == username
                ).first()

                if exists:
                    continue

                new_user = models.User(
                    username=username,
                    full_name=row["full_name"].strip(),
                    password=get_password_hash(row["password"]),
                    role=row.get("role", "student"),
                    must_change_password=True,
                    is_active=True
                )

                db.add(new_user)
                created_users.append(username)

        db.commit()

    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="students.csv file not found"
        )

    return {
        "created": len(created_users),
        "usernames": created_users
    }


# login
@router.post("/login")
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        models.User.username == user.username,
        models.User.is_active == True
    ).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "message": "Login successful",
        "user_id": db_user.id,
        "username": db_user.username,
        "role": db_user.role,
        "must_change_password": db_user.must_change_password
    }


# change password (student)
@router.post("/change-password")
def change_password(
    old_password: str,
    new_password: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    current_user.password = get_password_hash(new_password)
    current_user.must_change_password = False

    db.commit()

    return {
        "message": "Password changed successfully"
    }
