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
    
import requests
import xml.etree.ElementTree as ET
from typing import Dict

def get_morpa_authcode(uyeip: str, tckimlik: str) -> Dict:
    """
    Morpa'dan AuthCode alır (at=ac).
    Returns: {'ok': 1 or 0, 'authcode': str, 'domain': str, 'message': str}
    """
    url = "https://www.morpakampus.com/api.asp"
    params = {
        'at': 'ac',
        'uyeip': uyeip,
        'tckimlik': tckimlik
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        xml_content = response.text
        
        # XML parse et
        root = ET.fromstring(xml_content)
        ok_elem = root.find('.//OK')
        if ok_elem is None or ok_elem.text != '1':
            message = root.find('.//text()')  # Hata mesajı için
            return {'ok': 0, 'message': message.text if message is not None else 'Bilinmeyen hata'}
        
        r_elem = root.find('.//R')
        if r_elem is None:
            return {'ok': 0, 'message': 'AuthCode XML\'i eksik'}
        
        authcode = r_elem.get('authcode', '')
        domain = r_elem.get('domain', '')
        
        return {
            'ok': 1,
            'authcode': authcode,
            'domain': domain,
            'siniflar': r_elem.get('siniflar', ''),
            'dersler': r_elem.get('dersler', '')
        }
    except requests.RequestException as e:
        return {'ok': 0, 'message': f'HTTP hatası: {str(e)}'}
    except ET.ParseError as e:
        return {'ok': 0, 'message': f'XML parse hatası: {str(e)}'}
