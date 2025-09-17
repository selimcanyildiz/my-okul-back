from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Student, School
from schemas import StudentCreate, StudentUpdate, PasswordUpdate
import random
from datetime import timedelta

router = APIRouter(prefix="/students", tags=["students"])

@router.post("/add")
def add_student(student: StudentCreate, db: Session = Depends(get_db)):
    password = "123456"  # default şifre

    school = db.query(School).filter(School.id == student.school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail=f"Okul bulunamadı (id={student.school_id})")

    new_student = Student(
        tc=student.tc,
        ogrenci_no=student.ogrenci_no,
        ad=student.ad,
        soyad=student.soyad,
        cinsiyet=student.cinsiyet,
        program_tipi=student.program_tipi,
        sube_seviye=student.sube_seviye,
        sube_sinif=student.sube_sinif,
        okul_adi=student.okul_adi,
        bgkull=student.bgkull,
        bgsif=student.bgsif,
        klbkull=student.klbkull,
        klbsif=student.klbsif,
        sınavzakull=student.sınavzakull,
        sınavzasif=student.sınavzasif,
        morpakull=student.morpakull,
        morpasif=student.morpasif,
        parent_phone=student.parent_phone,
        username=student.tc,
        password=password,
        school_id=student.school_id
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return {
        "id": new_student.id,
        "full_name": f"{new_student.ad} {new_student.soyad}",
        "username": new_student.username,
        "password": new_student.password,
        "tc": new_student.tc,
        "school_id": new_student.school_id,
        "okul_adi": new_student.okul_adi,
        "parent_phone": new_student.parent_phone
    }


@router.post("/add_bulk")
def add_students_bulk(students: list[StudentCreate], db: Session = Depends(get_db)):
    if not students:
        raise HTTPException(status_code=400, detail="Hiç öğrenci gönderilmedi")

    added_students = []

    for s in students:
        password = "123456"  # tüm öğrencilere sabit şifre

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
            okul_adi=s.okul_adi,
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
            "username": new_student.username,
            "password": password,
            "tc": s.tc,
            "school_id": s.school_id,
            "okul_adi": s.okul_adi,
            "parent_phone": s.parent_phone
        })

    db.commit()
    return {"added_students": added_students}

@router.delete("/delete/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")

    db.delete(student)
    db.commit()
    return {"message": f"{student.ad} {student.soyad} başarıyla silindi", "deleted_id": student_id}

@router.put("/update/{student_id}")
def update_student(student_id: int, updated_student: StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")

    # Alanları güncelle
    for key, value in updated_student.dict(exclude_unset=True).items():
        setattr(student, key, value)

    db.commit()
    db.refresh(student)
    return student


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
            "password": s.password,
            "last_login": (s.last_login + timedelta(hours=3)).strftime("%d.%m.%Y %H:%M") if s.last_login else None,
            "school": {
                "id": school.id,
                "name": school.name,
                "address": school.address if hasattr(school, "address") else None,
            }
        })
    return result

@router.get("/all")
def get_all_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    result = []

    for s in students:
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
            "password": s.password,
            "branch": f"{s.sube_seviye} / {s.sube_sinif}",
            "last_login": (s.last_login + timedelta(hours=3)).strftime("%d.%m.%Y %H:%M") if s.last_login else None,
            "school": school_data,
            "parent_phone": s.parent_phone,
            "username": s.username
        })

    return {"students": result}

@router.get("/{student_id}")
def get_student_by_id(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")

    school = db.query(School).filter(School.id == student.school_id).first()
    school_data = None
    if school:
        school_data = {
            "id": school.id,
            "name": school.name,
            "address": getattr(school, "address", None)
        }

    return {
        "id": student.id,
        "tc": student.tc,
        "ogrenci_no": student.ogrenci_no,
        "ad": student.ad,
        "soyad": student.soyad,
        "cinsiyet": student.cinsiyet,
        "program_tipi": student.program_tipi,
        "sube_seviye": student.sube_seviye,
        "sube_sinif": student.sube_sinif,
        "okul_adi": student.okul_adi,
        "bgkull": student.bgkull,
        "bgsif": student.bgsif,
        "klbkull": student.klbkull,
        "klbsif": student.klbsif,
        "sınavzakull": student.sınavzakull,
        "sınavzasif": student.sınavzasif,
        "morpakull": student.morpakull,
        "morpasif": student.morpasif,
        "parent_phone": student.parent_phone,
        "school_id": student.school_id,
        "school": school_data,
        "username": student.username,
        "password": student.password,
        "last_login": (student.last_login + timedelta(hours=3)).strftime("%d.%m.%Y %H:%M") if student.last_login else None
    }

@router.put("/update_password/{student_id}")
def update_student_password(student_id: int, password_update: PasswordUpdate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")
    
    student.password = password_update.new_password
    db.commit()
    db.refresh(student)
    
    return {"message": "Şifre başarıyla değiştirildi", "id": student.id}


