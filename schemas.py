from pydantic import BaseModel, validator
from typing import Optional

class SchoolCreate(BaseModel):
    school_name: str
    admin_name: str
    admin_surname: str
    admin_tc: str
    admin_phone: str

    @validator("admin_tc")
    def validate_tc(cls, v):
        if not v.isdigit() or len(v) != 11:
            raise ValueError("TC kimlik numarası 11 haneli ve sadece rakamlardan oluşmalı")
        return v

    @validator("admin_phone")
    def validate_phone(cls, v):
        if not v.startswith("0") or len(v) != 11 or not v.isdigit():
            raise ValueError("Telefon numarası 0 ile başlamalı ve 11 haneli olmalı")
        return v
    
class StudentCreate(BaseModel):
    tc: str
    ogrenci_no: str
    ad: str
    soyad: str
    cinsiyet: str
    program_tipi: str
    sube_seviye: str
    sube_sinif: str
    okul_adi: str
    bgkull: str
    bgsif: str
    klbkull: str
    klbsif: str
    sınavzakull: str
    sınavzasif: str
    morpakull: str
    morpasif: str
    parent_phone: str
    school_id: int  # hangi okula ait

class StudentUpdate(BaseModel):
    tc: Optional[str]
    ogrenci_no: Optional[str]
    ad: Optional[str]
    soyad: Optional[str]
    cinsiyet: Optional[str]
    program_tipi: Optional[str]
    sube_seviye: Optional[str]
    sube_sinif: Optional[str]
    okul_adi: Optional[str]
    bgkull: Optional[str]
    bgsif: Optional[str]
    klbkull: Optional[str]
    klbsif: Optional[str]
    sınavzakull: Optional[str]
    sınavzasif: Optional[str]
    morpakull: Optional[str]
    morpasif: Optional[str]
    cambridgekull: Optional[str]
    cambridgesif: Optional[str]
    parent_phone: Optional[str]
    school_id: Optional[int]

class PasswordUpdate(BaseModel):
    new_password: str
