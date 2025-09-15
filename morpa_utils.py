import requests
import xml.etree.ElementTree as ET
from fastapi import HTTPException
from config import MORPA_ENTEGRASYON_KODU

def get_morpa_auth_code(tc_kimlik: str, client_ip: str):
    """
    Morpa sunucusundan AuthCode alır.
    """
    url = "https://www.morpakampus.com/api.asp"
    params = {
        "at": "ac",
        "uyeip": client_ip,
        "tckimlik": tc_kimlik,
        "entkod": MORPA_ENTEGRASYON_KODU
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        root = ET.fromstring(response.text)
        ok = root.find("OK").text
        if ok != "1":
            raise HTTPException(status_code=400, detail="Morpa AuthCode alınamadı")
        
        auth_data = root.find("R").attrib
        return {
            "authcode": auth_data["authcode"],
            "domain": auth_data["domain"],
            "siniflar": auth_data["siniflar"],
            "dersler": auth_data["dersler"]
        }
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Morpa API isteği başarısız: {str(e)}")
    except ET.ParseError:
        raise HTTPException(status_code=500, detail="Morpa API cevabı geçersiz XML formatında")

def check_morpa_auth_code(authcode: str):
    """
    Morpa AuthCode'un aktifliğini kontrol eder.
    """
    url = "https://www.morpakampus.com/api.asp"
    params = {
        "at": "cac",
        "ac": authcode,
        "entkod": MORPA_ENTEGRASYON_KODU
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        root = ET.fromstring(response.text)
        ok = root.find("OK").text
        return ok == "1"
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Morpa AuthCode kontrolü başarısız: {str(e)}")
    except ET.ParseError:
        raise HTTPException(status_code=500, detail="Morpa API cevabı geçersiz XML formatında")

def morpa_login(authcode: str, domain: str):
    """
    Morpa platformuna giriş yapar ve yönlendirme URL'sini döndürür.
    """
    url = f"https://{domain}/api.asp"
    params = {
        "at": "giris",
        "ac": authcode
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.url  # Yönlendirme URL'si
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Morpa giriş isteği başarısız: {str(e)}")