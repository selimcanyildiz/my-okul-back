from datetime import datetime, timedelta
from jose import jwt, JWTError
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, BILISIMGARAJI_API_KODU

def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded
    except JWTError:
        return None

def generate_bilisimgaraji_jwt(user):
    try:
        payload = {
            "api_kodu": BILISIMGARAJI_API_KODU,
            "kullanici_tekil_id": str(user.get("id", "")),
            "kullanici_tipi": "ogrenci",
            "ogrenci_no": str(user.get("ogrenci_no", "")),
            "ad": user.get("ad", ""),
            "soyad": user.get("soyad", ""),
            "cinsiyet": str(user.get("cinsiyet", "")),
            "okul_detay": [
                {
                    "okul_id": str(user.get("okul_id", "")),
                    "okul_adi": user.get("okul_adi", ""),
                    "program_tipi": str(user.get("program_tipi", "")),
                    "sube_seviye": str(user.get("sube_seviye", "")),
                    "sube_sinif": user.get("sube_sinif", "")
                }
            ],
            "kullanici_durum": 1,
            "zaman": int(datetime.utcnow().timestamp())
        }
        return create_access_token(payload)
    except Exception as e:
        raise Exception(f"Bilişim Garajı JWT oluşturma hatası: {str(e)}")

def generate_kolibri_jwt(user):
    try:
        payload = {
            "nameid": str(user.get("id", "")),  # Kolibri expects userId in 'nameid' claim
            "nbf": int(datetime.utcnow().timestamp()),
            "iat": int(datetime.utcnow().timestamp()),
            "exp": int((datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp())
        }
        return create_access_token(payload)
    except Exception as e:
        raise Exception(f"Kolibri JWT oluşturma hatası: {str(e)}")