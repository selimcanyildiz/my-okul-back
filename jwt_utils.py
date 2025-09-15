from datetime import datetime, timedelta
from jose import jwt, JWTError
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, BILISIMGARAJI_API_KODU
from models import Student, User

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
        # Eğer SQLAlchemy objesi geldiyse dict'e dönüştürelim
        if isinstance(user, Student) or isinstance(user, User):
            user_dict = {
                "id": getattr(user, "id", ""),
                "ogrenci_no": getattr(user, "ogrenci_no", ""),
                "ad": getattr(user, "ad", ""),
                "soyad": getattr(user, "soyad", ""),
                "cinsiyet": getattr(user, "cinsiyet", ""),
                "okul_id": getattr(user, "school_id", ""),
                "okul_adi": getattr(user, "okul_adi", ""),  # varsa
                "program_tipi": getattr(user, "program_tipi", ""),
                "sube_seviye": getattr(user, "sube_seviye", ""),
                "sube_sinif": getattr(user, "sube_sinif", ""),
            }
        else:
            # dict verilmişse olduğu gibi kullan
            user_dict = user

        payload = {
            "api_kodu": BILISIMGARAJI_API_KODU,
            "kullanici_tekil_id": str(user_dict.get("id", "")),
            "kullanici_tipi": "ogrenci",
            "ogrenci_no": str(user_dict.get("ogrenci_no", "")),
            "ad": user_dict.get("ad", ""),
            "soyad": user_dict.get("soyad", ""),
            "cinsiyet": str(user_dict.get("cinsiyet", "")),
            "okul_detay": [
                {
                    "okul_id": str(user_dict.get("okul_id", "")),
                    "okul_adi": user_dict.get("okul_adi", ""),
                    "program_tipi": str(user_dict.get("program_tipi", "")),
                    "sube_seviye": str(user_dict.get("sube_seviye", "")),
                    "sube_sinif": user_dict.get("sube_sinif", "")
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
        if isinstance(user, Student) or isinstance(user, User):
            user_dict = {
                "id": getattr(user, "id", ""),
                "username": getattr(user, "username", ""),
            }
        else:
            user_dict = user

        payload = {
            "sub": user_dict.get("username", ""),
            "nameid": str(user_dict.get("id", "")),
            "nbf": int(datetime.utcnow().timestamp()),
            "iat": int(datetime.utcnow().timestamp()),
            "exp": int((datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp())
        }
        return create_access_token(payload)
    except Exception as e:
        raise Exception(f"Kolibri JWT oluşturma hatası: {str(e)}")
