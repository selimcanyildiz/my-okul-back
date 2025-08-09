# Sahte kullanıcı verisi
fake_users_db = {
    "ogrenci1": {
        "username": "ogrenci1",
        "password": "1234",
        "id": "1",
        "ogrenci_no": "675",
        "ad": "Ahmet",
        "soyad": "Can",
        "cinsiyet": "1",
        "okul_id": "1",
        "okul_adi": "Demo Okul",
        "program_tipi": "1",
        "sube_seviye": "11",
        "sube_sinif": "A"
    }
}

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or user["password"] != password:
        return None
    return user
