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
        "sube_sinif": "A",
        "role": "Student",  # Added for Kolibri
        "level": 9  # Added for Kolibri
    },
    "ali": {
        "username": "ali",
        "password": "12345",
        "id": "2",
        "ogrenci_no": "701",
        "ad": "Ali",
        "soyad": "Yılmaz",
        "cinsiyet": "1",
        "okul_id": "1",
        "okul_adi": "Demo Okul",
        "program_tipi": "1",
        "sube_seviye": "11",
        "sube_sinif": "A",
        "role": "Student",  # Added for Kolibri
        "level": 9  # Added for Kolibri
    },
    "Celal": {
        "username": "Celal",
        "password": "12",
        "id": "3",
        "ogrenci_no": "789",
        "ad": "Ahmet",
        "soyad": "Can",
        "cinsiyet": "1",
        "okul_id": "1",
        "okul_adi": "My Okul İstanbul",
        "program_tipi": "1",
        "sube_seviye": "12",
        "sube_sinif": "A",
        "role": "Student",  # Added for Kolibri
        "level": 9  # Added for Kolibri
    },
    "Recep": {
        "username": "Recep",
        "password": "13",
        "id": "4",
        "ogrenci_no": "942",
        "ad": "Recep",
        "soyad": "Öztürk",
        "cinsiyet": "1",
        "okul_id": "1",
        "okul_adi": "My Okul Ankara",
        "program_tipi": "1",
        "sube_seviye": "9",
        "sube_sinif": "B",
        "role": "Student",  # Added for Kolibri
        "level": 9  # Added for Kolibri
    }
}

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or user["password"] != password:
        return None
    return user