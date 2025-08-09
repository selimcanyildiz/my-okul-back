from fastapi import Depends, HTTPException, Header
from jwt_utils import decode_token
from models import fake_users_db

def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Geçersiz token formatı")
    token = authorization[7:]
    decoded = decode_token(token)
    if not decoded:
        raise HTTPException(status_code=401, detail="Token doğrulanamadı")

    username = decoded.get("sub")
    user = fake_users_db.get(username)
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    return user
