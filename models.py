# Sahte kullanıcı verisi
fake_users_db = {
    "Can": {
        "username": "Can",
        "password": "1234",
        "id": "1",
        "ogrenci_no": "675",
        "ad": "Can",
        "soyad": "Yıldız",
        "cinsiyet": "1",
        "okul_id": "1",
        "okul_adi": "My Okul Ankara",
        "program_tipi": "1",
        "sube_seviye": "11",
        "sube_sinif": "A",
        "role": "Student",  # Added for Kolibri
        "level": 11  # Added for Kolibri
    },
    "Elif": {
        "username": "Elif",
        "password": "12345",
        "id": "2",
        "ogrenci_no": "701",
        "ad": "Elif",
        "soyad": "Yılmaz",
        "cinsiyet": "2",
        "okul_id": "1",
        "okul_adi": "My Okul İzmir",
        "program_tipi": "1",
        "sube_seviye": "10",
        "sube_sinif": "C",
        "role": "Student",  # Added for Kolibri
        "level": 10  # Added for Kolibri
    }
}

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or user["password"] != password:
        return None
    return user