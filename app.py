from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from models import authenticate_user, fake_users_db
from jwt_utils import create_access_token, generate_bilisimgaraji_jwt, generate_kolibri_jwt, decode_token
from auth import get_current_user

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://api.v2.bookrclass.com", "https://web.bookrclass.com","https://my-okul-front.vercel.app"],
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
def login(data: LoginRequest):
    user = authenticate_user(data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Kullanıcı adı veya şifre hatalı")

    token = create_access_token({"sub": data.username})
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
async def validate_token(token: str = Query(...)):
    decoded = decode_token(token)
    if not decoded:
        raise HTTPException(status_code=401, detail="Geçersiz veya süresi dolmuş token")

    username = decoded.get("sub")
    user = fake_users_db.get(username)
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    # BookR Class'ın beklediği SsoUserDto formatında yanıt
    sso_user_dto = {
        "id": str(user.get("id", "")),
        "appGeneratedId": str(user.get("id", "")),
        "username": user.get("username", ""),
        "firstName": user.get("ad", ""),
        "lastName": user.get("soyad", ""),
        "name": f"{user.get('ad', '')} {user.get('soyad', '')}",
        "role": user.get("role", "Student"),
        "school_class": [
            {
                "schoolcode": str(user.get("okul_id", "")),
                "classname": f"{user.get('sube_seviye', '')}/{user.get('sube_sinif', '')}",
                "schoolname": user.get("okul_adi", "")
            }
        ],
        "level": user.get("level", 1),
        "hidden_levels": []
    }
    return sso_user_dto