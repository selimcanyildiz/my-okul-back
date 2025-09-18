from fastapi import FastAPI, HTTPException, Depends, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from routers import school_router
from routers import student_router
from auth import get_current_user
from database import get_db
from models import User, Student, School
from jwt_utils import create_access_token, generate_bilisimgaraji_jwt, generate_kolibri_jwt, decode_token
from sqlalchemy.orm import Session
from datetime import datetime

app = FastAPI(
    title="MY Okulları API",
    version="1.0.0",
    root_path="/api"
)

app.include_router(school_router.router)
app.include_router(student_router.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://mypanel.myokullari.com",
        "https://mypanel.myokullari.com", 
        "https://api.v2.bookrclass.com", 
        "https://web.bookrclass.com",
        "https://my-okul-front.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str

class PlatformRequest(BaseModel):
    platformName: str

def authenticate_user(db: Session, username: str, password: str):
    # Önce users tablosuna bak
    user = db.query(User).filter(User.username == username, User.password == password).first()
    if user:
        return user

    # Sonra students tablosuna bak
    student = db.query(Student).filter(Student.username == username, Student.password == password).first()
    if student:
        return student

    return None

@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Kullanıcı adı veya şifre hatalı")

    if hasattr(user, "last_login"):
        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)

    token = create_access_token({"sub": user.username})
    return {"user": user, "access_token": token, "token_type": "bearer"}

@app.get("/stats")
def get_stats(
    school_id: int = Query(..., description="Yetkilinin okul ID'si veya 0 = tüm okullar"),
    db: Session = Depends(get_db)
):
    total_schools = db.query(School).count()  # Toplam okul sayısı

    if school_id == 0:
        # Tüm okullar için
        total_students = db.query(Student).count()
        active_students = db.query(Student).filter(Student.last_login.isnot(None)).count()
        passive_students = db.query(Student).filter(Student.last_login.is_(None)).count()

        recent_logins = (
            db.query(Student, School)
            .join(School, Student.school_id == School.id, isouter=True)
            .filter(Student.last_login.isnot(None))
            .order_by(Student.last_login.desc())
            .limit(5)
            .all()
        )

        recent_logins_data = [
            {
                "id": s.id,
                "name": f"{s.ad} {s.soyad}",
                "school": school.name if school else None,
                "branch": f"{s.sube_sinif} / {s.sube_seviye}",
                "lastLogin": s.last_login.strftime("%d.%m.%Y %H:%M") if s.last_login else None
            }
            for s, school in recent_logins
        ]

        return {
            "school_id": 0,
            "school_name": "Tüm Okullar",
            "total_schools": total_schools,
            "total_students": total_students,
            "active_students": active_students,
            "passive_students": passive_students,
            "recent_logins": recent_logins_data
        }

    else:
        # Belirli okul için
        total_students = db.query(Student).filter(Student.school_id == school_id).count()
        active_students = db.query(Student).filter(
            Student.school_id == school_id,
            Student.last_login.isnot(None)
        ).count()
        passive_students = db.query(Student).filter(
            Student.school_id == school_id,
            Student.last_login.is_(None)
        ).count()

        school = db.query(School).filter(School.id == school_id).first()
        if not school:
            raise HTTPException(status_code=404, detail="Okul bulunamadı")

        recent_logins = (
            db.query(Student)
            .filter(Student.school_id == school_id, Student.last_login.isnot(None))
            .order_by(Student.last_login.desc())
            .limit(5)
            .all()
        )

        recent_logins_data = [
            {
                "id": s.id,
                "name": f"{s.ad} {s.soyad}",
                "school": school.name,
                "branch": f"{s.sube_sinif} / {s.sube_seviye}",
                "lastLogin": s.last_login.strftime("%d.%m.%Y %H:%M") if s.last_login else None
            }
            for s in recent_logins
        ]

        return {
            "school_id": school.id,
            "school_name": school.name,
            "total_schools": total_schools,
            "total_students": total_students,
            "active_students": active_students,
            "passive_students": passive_students,
            "recent_logins": recent_logins_data
        }


@app.post("/login-to-platform")
def login_to_platform(
    req: PlatformRequest,
    user=Depends(get_current_user)
):
    platform = req.platformName.lower()

    if platform == "bilisimgaraji":
        jwt_token = generate_bilisimgaraji_jwt(user)
        redirect_url = f"https://lms.bilisimgaraji.com/loginsso?c={jwt_token}"
        return {"redirect_url": redirect_url}
    
    elif platform == "kolibri":
        jwt_token = generate_kolibri_jwt(user)
        from config import KOLIBRI_SSO_ID
        redirect_url = f"https://api.v2.bookrclass.com/api/oauth/sso/app/login/{KOLIBRI_SSO_ID}/?token={jwt_token}&returnUrl=https://www.bookrclass.com/?platform=web"
        return {"redirect_url": redirect_url}

    else:
        raise HTTPException(status_code=404, detail="Bu platform şu anda desteklenmiyor")

@app.get("/auth/validatetoken")
def validate_token(token: str = Query(...), db: Session = Depends(get_db)):
    decoded = decode_token(token)
    if not decoded:
        raise HTTPException(status_code=401, detail="Geçersiz veya süresi dolmuş token")

    username = decoded.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        # users bulunmazsa students tablosuna bak
        user = db.query(Student).filter(Student.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    sso_user_dto = {
        "id": str(getattr(user, "id", "")),
        "appGeneratedId": str(getattr(user, "id", "")),
        "username": getattr(user, "username", ""),
        "firstName": getattr(user, "full_name", "").split(" ")[0] if getattr(user, "full_name", "") else "",
        "lastName": getattr(user, "full_name", "").split(" ")[1] if getattr(user, "full_name", "") else "",
        "name": getattr(user, "full_name", ""),
        "role": getattr(user, "role", "student"),  # students için default role
        "school_class": [],
        "level": 1,
        "hidden_levels": []
    }
    return sso_user_dto