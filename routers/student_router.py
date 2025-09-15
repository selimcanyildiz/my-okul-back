from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Student, School
from schemas import StudentCreate
import random

router = APIRouter(prefix="/students", tags=["students"])

@router.post("/add_bulk")
def add_students_bulk(students: list[StudentCreate], db: Session = Depends(get_db)):
    if not students:
        raise HTTPException(status_code=400, detail="Hiç öğrenci gönderilmedi")

    added_students = []

    for s in students:
        initials = (s.ad[0] + s.soyad[0]).lower()
        password = f"{initials}{random.randint(1000, 9999)}"
        username = password

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
            okul_adi= s.okul_adi,
            bgkull=s.bgkull,
            bgsif=s.bgsif,
            klbkull=s.klbkull,
            klbsif=s.klbsif,
            sınavzakull=s.sınavzakull,
            sınavzasif=s.sınavzasif,
            morpakull=s.morpakull,
            morpasif=s.morpasif,
            parent_phone=s.parent_phone,
            username=s.tc,
            password=password,
            school_id=s.school_id
        )

        db.add(new_student)
        added_students.append({
            "full_name": f"{s.ad} {s.soyad}",
            "username": username,
            "password": password,
            "tc": s.tc,
            "school_id": s.school_id,
            "okul_adi": s.okul_adi,
            "parent_phone": s.parent_phone
        })

    # tek seferde commit
    db.commit()

    return {"added_students": added_students}

@router.get("/by_school/{school_id}")
def get_students_by_school(school_id: int, db: Session = Depends(get_db)):
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="Okul bulunamadı")

    students = db.query(Student).filter(Student.school_id == school_id).all()
    result = []
    for s in students:
        result.append({
            "id": s.id,
            "ad": s.ad,
            "soyad": s.soyad,
            "tc": s.tc,
            "branch": f"{s.sube_seviye} / {s.sube_sinif}",
            # Okul bilgilerini direkt ekliyoruz
            "school": {
                "id": school.id,
                "name": school.name,
                "address": school.address if hasattr(school, "address") else None,
                # diğer okul alanları eklenebilir
            }
        })
    return result

@router.get("/all")
def get_all_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    result = []

    for s in students:
        # Okul bilgilerini çekiyoruz
        school = db.query(School).filter(School.id == s.school_id).first()
        school_data = None
        if school:
            school_data = {
                "id": school.id,
                "name": school.name,
                "address": getattr(school, "address", None)
            }

        result.append({
            "id": s.id,
            "ad": s.ad,
            "soyad": s.soyad,
            "tc": s.tc,
            "branch": f"{s.sube_seviye} / {s.sube_sinif}",
            "school": school_data,
            "parent_phone": s.parent_phone,
            "username": s.username
        })

    return {"students": result}