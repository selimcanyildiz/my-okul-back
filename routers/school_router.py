from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth import get_current_user
from database import get_db
from models import User, School, Student
from schemas import SchoolCreate
import random
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/schools", tags=["schools"])

@router.post("/add")
def add_school(
    data: SchoolCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    logger.debug(f"Received data: {data}")

    if current_user.role != "sysadmin":
        raise HTTPException(status_code=403, detail="Yetkiniz yok")

    # TC veya username zaten var mı kontrol et
    existing_user = db.query(User).filter(
        (User.username == data.admin_tc) | (User.tc == data.admin_tc)
    ).first()
    if existing_user:
        raise HTTPException(status_code=422, detail="Bu TC kimlik numarası veya kullanıcı adı zaten kayıtlı")

    # Yetkili kullanıcı için username ve password oluştur
    username = data.admin_tc
    initials = (data.admin_name[0] + data.admin_surname[0]).lower()
    password = f"{initials}{random.randint(1000, 9999)}"
    logger.debug(f"Generated username: {username}, password: {password}")

    # Kullanıcı ekle
    new_user = User(
        username=username,
        password=password,
        role="yetkili",
        full_name=f"{data.admin_name} {data.admin_surname}",
        tc=data.admin_tc,
        phone=data.admin_phone
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.debug(f"User created: {new_user.id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Kullanıcı eklenirken hata: {str(e)}")

    # Okul ekle
    new_school = School(name=data.school_name, admin_id=new_user.id)
    try:
        db.add(new_school)
        db.commit()
        db.refresh(new_school)
        logger.debug(f"School created: {new_school.id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating school: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Okul eklenirken hata: {str(e)}")

    # Response JSON
    return {
        "school": {
            "id": new_school.id,
            "name": new_school.name,
            "admin_id": new_user.id
        },
        "admin_user": {
            "username": username,
            "password": password,
            "full_name": new_user.full_name,
            "tc": new_user.tc,
            "phone": new_user.phone
        }
    }


@router.get("/{school_id}")
def get_school(
    school_id: int,
    db: Session = Depends(get_db),
):
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="Okul bulunamadı")

    return {
        "id": school.id,
        "name": school.name
        # Eğer Schools tablosunda başka alanlar varsa onları da ekleyebilirsin
    }

@router.get("/")
def get_all_schools(db: Session = Depends(get_db)):
    schools = db.query(School).all()
    if not schools:
        return []

    result = []
    for s in schools:
        # Admin bilgilerini çek
        admin = db.query(User).filter(User.id == s.admin_id).first()
        admin_info = {
            "id": admin.id,
            "full_name": admin.full_name,
            "tc": admin.tc,
            "username": admin.username,
            "password": admin.password,
            "phone": admin.phone
        } if admin else {}

        result.append({
            "id": s.id,
            "name": s.name,
            "address": getattr(s, "address", ""),
            "city": getattr(s, "city", ""),
            "district": getattr(s, "district", ""),
            "admin": admin_info
        })

    return result

@router.get("/by_admin/{admin_id}")
def get_school_by_admin(
    admin_id: int,
    db: Session = Depends(get_db)
):
    # Yetkili kullanıcı var mı kontrol et
    admin_user = db.query(User).filter(User.id == admin_id, User.role == "yetkili").first()
    if not admin_user:
        raise HTTPException(status_code=404, detail="Yetkili kullanıcı bulunamadı")

    # Admin_id ile okulu bul
    school = db.query(School).filter(School.admin_id == admin_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="Bu yetkiliye ait okul bulunamadı")

    return {
        "school": {
            "id": school.id,
            "name": school.name,
            "created_at": school.created_at
        },
        "admin": {
            "id": admin_user.id,
            "full_name": admin_user.full_name,
            "tc": admin_user.tc,
            "username": admin_user.username,
            "phone": admin_user.phone
        }
    }

@router.delete("/delete/{school_id}")
def delete_school(school_id: int, db: Session = Depends(get_db)):
    # Okulu bul
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="Okul bulunamadı")

    # Okula ait tüm öğrencileri sil
    students = db.query(Student).filter(Student.school_id == school_id).all()
    deleted_student_ids = []
    for student in students:
        deleted_student_ids.append(student.id)
        db.delete(student)

    db.commit()  # Öğrencileri commit et

    # Okulu sil
    school_name = school.name
    db.delete(school)
    db.commit()  # Okulu commit et

    # Okul yetkilisini sil (User tablosundan)
    admin_user = db.query(User).filter(User.id == school.admin_id).first()
    deleted_admin_id = None
    if admin_user:
        deleted_admin_id = admin_user.id
        db.delete(admin_user)
        db.commit()  # Admini commit et

    return {
        "message": f"{school_name} okulu, {len(deleted_student_ids)} öğrencisi ve yetkili kullanıcı başarıyla silindi",
        "deleted_school_id": school_id,
        "deleted_student_ids": deleted_student_ids,
        "deleted_admin_id": deleted_admin_id
    }
