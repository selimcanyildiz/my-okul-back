from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    full_name = Column(String)
    tc = Column(String(11))
    phone = Column(String(15))

class School(Base):
    __tablename__ = "schools"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # Uzunluk kısıtlamasını açıkça belirttik
    admin_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=False), server_default=func.now())  # timezone=False
    students = relationship("Student", back_populates="school")

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    tc = Column(String(11), unique=True, nullable=False)
    ogrenci_no = Column(String(20), nullable=False)
    ad = Column(String(50), nullable=False)
    soyad = Column(String(50), nullable=False)
    cinsiyet = Column(String(1))
    program_tipi = Column(String(10))
    sube_seviye = Column(String(10))
    sube_sinif = Column(String(10))
    
    # şifreli sistemler
    bgkull = Column(String(50), nullable=True)
    bgsif = Column(String(50), nullable=True)
    klbkull = Column(String(50), nullable=True)
    klbsif = Column(String(50), nullable=True)
    sınavzakull = Column(String(50), nullable=True)
    sınavzasif = Column(String(50), nullable=True)
    morpakull = Column(String(50), nullable=True)
    morpasif = Column(String(50), nullable=True)
    parent_phone = Column(String(15), nullable=True)


    # login için username ve password
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)

    parent_phone = Column(String(15), nullable=False)  # <-- Yeni alan

    # ilişki
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    school = relationship("School", back_populates="students")

