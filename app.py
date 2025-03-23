from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# CORS için yapılandırma
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Herhangi bir domain'e izin veriyoruz (prod'da domain kısıtlaması yapmalısınız)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Statik platform verileri
platformlar = {
    "egitimparki": {
        "url": "https://akademi.myokullari.com/Login",
        "username": "1535-175",
        "password": "9A01E",
        "usernameInputId": "txtUserName",
        "passwordInputId": "txtPassword",
        "loginButtonId": "btnLogin",
    },
    "rokodemi": {
        "url": "https://www.rokodemi.com/Login",
        "username": "MEHMETAKIFMERMER",
        "password": "1905gs",
        "usernameInputId": "Email",
        "passwordInputId": "Password",
        "loginButtonId": "submit",
    },
    "eyotek": {
        "url": "https://mykolej.eyotek.com/v1/",
        "username": "20337",
        "password": "5T5BR2V",
        "usernameInputId": "txtUsername",
        "passwordInputId": "txtPassword",
        "loginButtonId": "btnLogin",
    },
}

# Tüm istekleri logla
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Gelen istek: {request.method} {request.url}")
    response = await call_next(request)
    return response

# Gelen istekler için model
class PlatformRequest(BaseModel):
    platformName: str

@app.post("/login-to-platform")
async def login_to_platform(request: PlatformRequest):
    platform_name = request.platformName
    print("Gelen platform adı:", platform_name)

    platform_data = platformlar.get(platform_name)

    if platform_data:
        return platform_data
    else:
        raise HTTPException(status_code=404, detail="Platform bulunamadı")


# Statik dosyaların bulunduğu dizini tanımla
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/download-extension")
async def download_extension():
    # extension.zip dosyasının tam yolunu belirt
    file_path = os.path.join("static", "extension.zip")
    
    # Dosyanın mevcut olduğundan emin olun
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/zip', filename="extension.zip")
    else:
        return {"error": "Dosya bulunamadı"}
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)