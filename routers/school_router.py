from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth import get_current_user
from database import get_db
from models import User, School
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
