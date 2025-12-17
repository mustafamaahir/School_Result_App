from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
import bcrypt

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

def get_password_hash(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


@router.post("/register", status_code=200)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if existing:
        raise HTTPException(400, "Username already exists")
    
    hashed_pw = get_password_hash(user.password)
    
    new_user = models.User(
        username=user.username,
        password=hashed_pw,
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

@router.post("/bulk-register-csv")
def bulk_register_from_csv(clear_existing: bool = False, db: Session = Depends(get_db)):
    """
    Import students from CSV file.
    Set clear_existing=true to delete old users first.
    """
    if clear_existing:
        db.query(models.User).delete()
        db.commit()
    
    # Read CSV (put your CSV file in backend folder)
    import csv
    created = []
    
    with open("students.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            exists = db.query(models.User).filter(
                models.User.username == row["username"]
            ).first()
            
            if exists:
                continue
                
            hashed_pw = get_password_hash(row["password"])
            new_user = models.User(
                username=row["username"],
                password=hashed_pw,
                full_name=row["full_name"],
                role=row.get("role", "student")
            )
            db.add(new_user)
            created.append(row["username"])
    
    db.commit()
    return {"created": len(created), "usernames": created}

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
