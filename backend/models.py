# backend/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)
    full_name = Column(String)

    # Keep user simple for now. Optional: add relationships if needed later.

class StudentResult(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    student_class = Column(String, index=True)
    subject = Column(String, index=True)
    percentage = Column(Float)

    # Allow nullable True so bulk upload can store rows before link to user ids.
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # relationships linking back to User (teacher and student)
    teacher = relationship("User", foreign_keys=[teacher_id], backref="uploaded_results")
    student = relationship("User", foreign_keys=[student_id], backref="received_results")
    
    term = Column(String, nullable=False)
    session = Column(String, nullable=False)

