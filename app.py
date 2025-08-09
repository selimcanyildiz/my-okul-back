from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from models import authenticate_user
from jwt_utils import create_access_token, generate_bilisimgaraji_jwt, generate_bookr_jwt
from auth import get_current_user
from config import BOOKR_SSO_ID

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin'i buraya yaz
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

    elif platform == "bookr":
        jwt_token = generate_bookr_jwt(user)
        deeplink_url = f"bookrclass://app?clientToken={jwt_token}&ssoId={BOOKR_SSO_ID}"
        return {"redirect_url": deeplink_url}

    else:
        raise HTTPException(status_code=404, detail="Bu platform şu anda desteklenmiyor")
