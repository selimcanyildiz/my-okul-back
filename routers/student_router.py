from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Student, School
from schemas import StudentCreate
import random

router = APIRouter(prefix="/students", tags=["students"])

@router.post("/add")
def add_students(students: list[StudentCreate], db: Session = Depends(get_db)):
    added_students = []

    for s in students:
        # kullanıcı adı ve şifre üret (ad + soyad başharf + random 4 sayı)
        initials = (s.ad[0] + s.soyad[0]).lower()
        password = f"{initials}{random.randint(1000, 9999)}"
        username = password

        # okul var mı kontrol et
        school = db.query(School).filter(School.id == s.school_id).first()
        if not school:
            raise HTTPException(status_code=404, detail=f"Okul bulunamadı (id={s.school_id})")

        new_student = Student(
            tc=s.tc,
            ogrenci_no=s.ogrenci_no,
            ad=s.ad,
            soyad=s.soyad,
            cinsiyet=s.cinsiyet,
            program_tipi=s.program_tipi,
            sube_seviye=s.sube_seviye,
            sube_sinif=s.sube_sinif,
            username=username,
            password=password,
            school_id=s.school_id
        )
        db.add(new_student)
        db.commit()
        db.refresh(new_student)

        added_students.append({
            "id": new_student.id,
            "username": username,
            "password": password,
            "full_name": f"{s.ad} {s.soyad}",
            "tc": s.tc,
            "school_id": s.school_id
        })

    return {"added_students": added_students}
