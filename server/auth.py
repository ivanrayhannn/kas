import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .db import SessionLocal, Store, User

APP_ENV = os.getenv("APP_ENV", "development")
SECRET_KEY = os.getenv("SECRET_KEY") or ("dev-secret-hanya-untuk-lokal-ganti-di-produksi" if APP_ENV != "production" else "")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY wajib diisi saat APP_ENV=production")
TOKEN_DAYS = 30
PBKDF2_ROUNDS = 310_000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), PBKDF2_ROUNDS).hex()
    return f"pbkdf2${PBKDF2_ROUNDS}${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, rounds, salt, digest = stored.split("$")
    except ValueError:
        return False
    test = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(rounds)).hex()
    return hmac.compare_digest(test, digest)


def make_token(user: User) -> str:
    exp = datetime.now(timezone.utc) + timedelta(days=TOKEN_DAYS)
    return jwt.encode({"sub": user.id, "v": user.token_version, "exp": exp}, SECRET_KEY, algorithm="HS256")


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def current_user(request: Request, db: Session = Depends(get_db)) -> User:
    header = request.headers.get("authorization", "")
    if not header.lower().startswith("bearer "):
        raise HTTPException(401, "Silakan masuk dulu.")
    try:
        data = jwt.decode(header[7:], SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(401, "Sesi sudah berakhir. Silakan masuk lagi.")
    user = db.get(User, data.get("sub"))
    if not user or user.token_version != data.get("v"):
        raise HTTPException(401, "Sesi sudah berakhir. Silakan masuk lagi.")
    return user


def current_store(user: User = Depends(current_user), db: Session = Depends(get_db)) -> Store:
    store = db.query(Store).filter(Store.owner_id == user.id).one_or_none()
    if not store:
        raise HTTPException(409, "Profil toko belum diisi.")
    return store
