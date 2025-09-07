from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from routers import school_router
from routers import student_router
from auth import get_current_user, authenticate_user
from database import get_db
from models import User
from jwt_utils import create_access_token, generate_bilisimgaraji_jwt, generate_kolibri_jwt, decode_token
from sqlalchemy.orm import Session

app = FastAPI()

app.include_router(school_router.router)
app.include_router(student_router.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
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

@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Kullanıcı adı veya şifre hatalı")

    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/login-to-platform")
def login_to_platform(req: PlatformRequest, user=Depends(get_current_user)):
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
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    sso_user_dto = {
        "id": str(user.id),
        "appGeneratedId": str(user.id),
        "username": user.username,
        "firstName": user.full_name.split(" ")[0] if user.full_name else "",
        "lastName": user.full_name.split(" ")[1] if user.full_name else "",
        "name": user.full_name or "",
        "role": user.role,
        "school_class": [],  # Burayı okul bilgisi ile doldurabilirsiniz
        "level": 1,
        "hidden_levels": []
    }
    return sso_user_dto
