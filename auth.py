from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
from models import User, Student
from jwt_utils import decode_token

def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Geçersiz token formatı")

    token = authorization[7:]
    decoded = decode_token(token)
    if not decoded:
        raise HTTPException(status_code=401, detail="Token doğrulanamadı")

    username = decoded.get("sub")

    # Önce User tablosuna bak
    user = db.query(User).filter(User.username == username).first()
    if user:
        return user

    # Eğer bulunmazsa Student tablosuna bak
    student = db.query(Student).filter(Student.username == username).first()
    if student:
        return student

    raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

def authenticate_user(db: Session, username: str, password: str):
    """
    Hash kullanmadan plain password ile kontrol
    """
    user = db.query(User).filter(User.username == username, User.password == password).first()
    if not user:
        return None
    return user
