import logging
import os
import secrets
import smtplib
from datetime import date, datetime, timedelta, timezone
from email.message import EmailMessage
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from . import logic
from .auth import (
    APP_ENV, current_store, current_user, get_db, hash_password, make_token, sha256, verify_password,
)
from .db import Category, Payment, ShoppingItem, ShoppingList, Store, Transaction, User, init_db, now

log = logging.getLogger("kas")
app = FastAPI(title="Kas Resto API")
init_db()


@app.middleware("http")
async def timezone_dari_ponsel(request: Request, call_next):
    logic.set_timezone(request.headers.get("x-timezone"))
    return await call_next(request)

Jenis = Literal["masuk", "keluar"]
Rupiah = Field(gt=0, le=999_999_999_999)
KATEGORI_BAWAAN = [
    ("Penjualan", "masuk"), ("Pembayaran QRIS", "masuk"), ("Lain-lain", "masuk"),
    ("Bahan Baku", "keluar"), ("Operasional", "keluar"), ("Transportasi", "keluar"),
    ("Gaji Karyawan", "keluar"), ("Lain-lain", "keluar"),
]
QR_MAX_CHARS = 1_400_000  # kira-kira 1 MB gambar setelah base64


def bersih(v: str | None) -> str | None:
    v = (v or "").strip()
    return v or None


# ---------- Akun ----------

class RegisterIn(BaseModel):
    nama: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=200)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class ForgotIn(BaseModel):
    email: EmailStr


class ResetIn(BaseModel):
    token: str
    password: str = Field(min_length=8, max_length=200)


def user_out(u: User) -> dict:
    return {"id": u.id, "nama": u.nama, "email": u.email}


def store_out(s: Store | None) -> dict | None:
    if not s:
        return None
    ambang, bawaan = logic.ambang_efektif(s)
    return {"id": s.id, "nama_toko": s.nama_toko, "alamat": s.alamat, "telepon": s.telepon,
            "modal_awal": s.modal_awal, "ambang_kas_menipis": s.ambang_kas_menipis,
            "ambang_efektif": ambang, "ambang_bawaan": bawaan, "qr_image": s.qr_image}


@app.post("/api/auth/register")
def register(body: RegisterIn, db: Session = Depends(get_db)):
    email = body.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "Email ini sudah terdaftar. Silakan masuk.")
    user = User(nama=body.nama.strip(), email=email, password_hash=hash_password(body.password))
    db.add(user)
    db.commit()
    return {"token": make_token(user), "user": user_out(user), "store": None}


@app.post("/api/auth/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Email atau kata sandi salah.")
    store = db.scalar(select(Store).where(Store.owner_id == user.id))
    return {"token": make_token(user), "user": user_out(user), "store": store_out(store)}


@app.post("/api/auth/logout")
def logout(user: User = Depends(current_user), db: Session = Depends(get_db)):
    user.token_version += 1
    db.commit()
    return {"ok": True}


def send_reset_email(to: str, link: str) -> bool:
    host = os.getenv("SMTP_HOST")
    if not host:
        return False
    msg = EmailMessage()
    msg["Subject"] = "Atur ulang kata sandi Kas Resto"
    msg["From"] = os.getenv("MAIL_FROM", os.getenv("SMTP_USER", ""))
    msg["To"] = to
    msg.set_content(f"Buka tautan ini untuk membuat kata sandi baru (berlaku 1 jam):\n{link}\n\n"
                    "Abaikan email ini bila Anda tidak meminta.")
    with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587"))) as s:
        s.starttls()
        if os.getenv("SMTP_USER"):
            s.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD", ""))
        s.send_message(msg)
    return True


@app.post("/api/auth/forgot")
def forgot(body: ForgotIn, db: Session = Depends(get_db)):
    # Jawaban selalu sama, supaya orang lain tidak bisa menebak email mana yang terdaftar.
    hasil = {"message": "Bila email terdaftar, tautan untuk membuat kata sandi baru sudah dikirim."}
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    if not user:
        return hasil
    token = secrets.token_urlsafe(32)
    user.reset_token_hash = sha256(token)
    user.reset_expires_at = now() + timedelta(hours=1)
    db.commit()
    link = f"{os.getenv('APP_URL', 'http://localhost:5173')}/atur-ulang-sandi?token={token}"
    try:
        terkirim = send_reset_email(user.email, link)
    except Exception:
        log.exception("Gagal mengirim email atur ulang sandi")
        terkirim = False
    if not terkirim and APP_ENV != "production":
        hasil["dev_reset_url"] = link  # hanya di mode pengembangan, karena belum ada server email
    return hasil


@app.post("/api/auth/reset")
def reset(body: ResetIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.reset_token_hash == sha256(body.token)))
    expires = user.reset_expires_at if user else None
    if expires and expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if not user or not expires or expires < now():
        raise HTTPException(400, "Tautan sudah tidak berlaku. Minta tautan baru.")
    user.password_hash = hash_password(body.password)
    user.reset_token_hash = None
    user.reset_expires_at = None
    user.token_version += 1
    db.commit()
    return {"ok": True}


@app.get("/api/me")
def me(user: User = Depends(current_user), db: Session = Depends(get_db)):
    store = db.scalar(select(Store).where(Store.owner_id == user.id))
    return {"user": user_out(user), "store": store_out(store)}


class ProfileIn(BaseModel):
    nama: str = Field(min_length=1, max_length=100)


@app.put("/api/me")
def update_me(body: ProfileIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    user.nama = body.nama.strip()
    db.commit()
    return user_out(user)


# ---------- Toko ----------

class StoreIn(BaseModel):
    nama_toko: str = Field(min_length=1, max_length=100)
    alamat: str | None = Field(default=None, max_length=200)
    telepon: str | None = Field(default=None, max_length=30)
    modal_awal: int = Field(ge=0, le=999_999_999_999)
    ambang_kas_menipis: int | None = Field(default=None, ge=0, le=999_999_999_999)


class QrIn(BaseModel):
    image: str

    @field_validator("image")
    @classmethod
    def cek_gambar(cls, v: str) -> str:
        if not v.startswith(("data:image/png;base64,", "data:image/jpeg;base64,", "data:image/webp;base64,")):
            raise ValueError("Gunakan gambar PNG, JPG, atau WEBP.")
        if len(v) > QR_MAX_CHARS:
            raise ValueError("Gambar terlalu besar. Maksimal 1 MB.")
        return v


@app.post("/api/store")
def create_store(body: StoreIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if db.scalar(select(Store).where(Store.owner_id == user.id)):
        raise HTTPException(409, "Akun ini sudah punya toko.")
    store = Store(owner_id=user.id, nama_toko=body.nama_toko.strip(), alamat=bersih(body.alamat),
                  telepon=bersih(body.telepon), modal_awal=body.modal_awal,
                  ambang_kas_menipis=body.ambang_kas_menipis)
    db.add(store)
    db.flush()
    db.add_all(Category(store_id=store.id, nama=n, jenis=j, is_default=True) for n, j in KATEGORI_BAWAAN)
    db.commit()
    return store_out(store)


@app.put("/api/store")
def update_store(body: StoreIn, store: Store = Depends(current_store), db: Session = Depends(get_db)):
    store.nama_toko = body.nama_toko.strip()
    store.alamat = bersih(body.alamat)
    store.telepon = bersih(body.telepon)
    store.modal_awal = body.modal_awal
    store.ambang_kas_menipis = body.ambang_kas_menipis
    db.commit()
    return store_out(store)


@app.put("/api/store/qr")
def upload_qr(body: QrIn, store: Store = Depends(current_store), db: Session = Depends(get_db)):
    store.qr_image = body.image
    db.commit()
    return store_out(store)


@app.delete("/api/store/qr")
def delete_qr(store: Store = Depends(current_store), db: Session = Depends(get_db)):
    store.qr_image = None
    db.commit()
    return store_out(store)


# ---------- Kategori ----------

class CategoryIn(BaseModel):
    nama: str = Field(min_length=1, max_length=50)
    jenis: Jenis


class CategoryRename(BaseModel):
    nama: str = Field(min_length=1, max_length=50)


def cat_out(c: Category, dipakai: int = 0) -> dict:
    return {"id": c.id, "nama": c.nama, "jenis": c.jenis, "is_default": c.is_default, "dipakai": dipakai}


def get_category(db: Session, store: Store, category_id: str, jenis: str | None = None) -> Category:
    c = db.get(Category, category_id)
    if not c or c.store_id != store.id:
        raise HTTPException(404, "Kategori tidak ditemukan.")
    if jenis and c.jenis != jenis:
        raise HTTPException(422, "Kategori tidak cocok dengan jenis catatan.")
    return c


def cek_nama_kategori(db: Session, store: Store, nama: str, jenis: str, kecuali: str | None = None):
    q = select(Category).where(Category.store_id == store.id, Category.jenis == jenis,
                               func.lower(Category.nama) == nama.lower())
    if kecuali:
        q = q.where(Category.id != kecuali)
    if db.scalar(q):
        raise HTTPException(409, "Kategori dengan nama ini sudah ada.")


@app.get("/api/categories")
def list_categories(store: Store = Depends(current_store), db: Session = Depends(get_db)):
    pakai = dict(db.execute(
        select(Transaction.category_id, func.count(Transaction.id))
        .where(Transaction.store_id == store.id).group_by(Transaction.category_id)
    ).all())
    cats = db.scalars(select(Category).where(Category.store_id == store.id).order_by(Category.created_at)).all()
    return [cat_out(c, pakai.get(c.id, 0)) for c in cats]


@app.post("/api/categories")
def create_category(body: CategoryIn, store: Store = Depends(current_store), db: Session = Depends(get_db)):
    nama = body.nama.strip()
    cek_nama_kategori(db, store, nama, body.jenis)
    c = Category(store_id=store.id, nama=nama, jenis=body.jenis)
    db.add(c)
    db.commit()
    return cat_out(c)


@app.put("/api/categories/{category_id}")
def rename_category(category_id: str, body: CategoryRename, store: Store = Depends(current_store),
                    db: Session = Depends(get_db)):
    c = get_category(db, store, category_id)
    nama = body.nama.strip()
    cek_nama_kategori(db, store, nama, c.jenis, kecuali=c.id)
    c.nama = nama
    db.commit()
    return cat_out(c)


@app.delete("/api/categories/{category_id}")
def delete_category(category_id: str, store: Store = Depends(current_store), db: Session = Depends(get_db)):
    c = get_category(db, store, category_id)
    if db.scalar(select(func.count(Transaction.id)).where(Transaction.category_id == c.id)):
        raise HTTPException(409, "Kategori ini sudah dipakai di catatan, jadi tidak bisa dihapus. Ubah namanya saja.")
    if db.scalar(select(func.count(Category.id)).where(Category.store_id == store.id, Category.jenis == c.jenis)) <= 1:
        raise HTTPException(409, "Minimal harus ada satu kategori untuk jenis ini.")
    db.delete(c)
    db.commit()
    return {"ok": True}


# ---------- Sisa kas & transaksi ----------

class TransactionIn(BaseModel):
    jenis: Jenis
    nominal: int = Rupiah
    category_id: str
    tanggal: date
    catatan: str | None = Field(default=None, max_length=200)


def tx_out(t: Transaction) -> dict:
    return {"id": t.id, "jenis": t.jenis, "nominal": t.nominal, "category_id": t.category_id,
            "kategori": t.category.nama, "tanggal": t.tanggal.isoformat(), "catatan": t.catatan,
            "sumber": t.sumber, "created_at": t.created_at.isoformat(), "updated_at": t.updated_at.isoformat()}


def cek_tanggal(d: date):
    if d > logic.today():
        raise HTTPException(422, "Tanggal tidak boleh setelah hari ini.")


def get_tx(db: Session, store: Store, tx_id: str) -> Transaction:
    t = db.get(Transaction, tx_id)
    if not t or t.store_id != store.id:
        raise HTTPException(404, "Catatan tidak ditemukan.")
    return t


@app.get("/api/summary")
def get_summary(store: Store = Depends(current_store), db: Session = Depends(get_db)):
    return logic.summary(db, store)


@app.get("/api/transactions")
def list_transactions(
    dari: date | None = None, sampai: date | None = None, jenis: Jenis | None = None,
    category_id: str | None = None, q: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=50, ge=1, le=200), offset: int = Query(default=0, ge=0),
    store: Store = Depends(current_store), db: Session = Depends(get_db),
):
    filt = [Transaction.store_id == store.id]
    if dari:
        filt.append(Transaction.tanggal >= dari)
    if sampai:
        filt.append(Transaction.tanggal <= sampai)
    if jenis:
        filt.append(Transaction.jenis == jenis)
    if category_id:
        filt.append(Transaction.category_id == category_id)
    if q and q.strip():
        pola = f"%{q.strip().lower()}%"
        filt.append(or_(func.lower(Transaction.catatan).like(pola),
                        Transaction.category_id.in_(select(Category.id).where(
                            Category.store_id == store.id, func.lower(Category.nama).like(pola)))))
    total = db.scalar(select(func.count(Transaction.id)).where(*filt))
    rows = db.scalars(select(Transaction).where(*filt)
                      .order_by(Transaction.tanggal.desc(), Transaction.created_at.desc())
                      .limit(limit).offset(offset)).all()
    return {"items": [tx_out(t) for t in rows], "total": total}


@app.post("/api/transactions")
def create_transaction(body: TransactionIn, user: User = Depends(current_user),
                       store: Store = Depends(current_store), db: Session = Depends(get_db)):
    get_category(db, store, body.category_id, body.jenis)
    cek_tanggal(body.tanggal)
    t = Transaction(store_id=store.id, category_id=body.category_id, jenis=body.jenis, nominal=body.nominal,
                    tanggal=body.tanggal, catatan=bersih(body.catatan), created_by=user.id)
    db.add(t)
    db.commit()
    db.refresh(t)
    return {"transaction": tx_out(t), "summary": logic.summary(db, store)}


@app.get("/api/transactions/{tx_id}")
def get_transaction(tx_id: str, store: Store = Depends(current_store), db: Session = Depends(get_db)):
    return tx_out(get_tx(db, store, tx_id))


@app.put("/api/transactions/{tx_id}")
def update_transaction(tx_id: str, body: TransactionIn, store: Store = Depends(current_store),
                       db: Session = Depends(get_db)):
    t = get_tx(db, store, tx_id)
    if t.sumber != "manual":
        asal = "pembayaran QRIS" if t.sumber == "qris" else "catatan belanja"
        raise HTTPException(409, f"Catatan ini dibuat otomatis dari {asal}, jadi tidak bisa diubah. "
                                 "Hapus catatan ini bila salah, lalu perbaiki di sumbernya.")
    get_category(db, store, body.category_id, body.jenis)
    cek_tanggal(body.tanggal)
    t.jenis, t.nominal, t.category_id = body.jenis, body.nominal, body.category_id
    t.tanggal, t.catatan = body.tanggal, bersih(body.catatan)
    db.commit()
    db.refresh(t)
    return {"transaction": tx_out(t), "summary": logic.summary(db, store)}


@app.delete("/api/transactions/{tx_id}")
def delete_transaction(tx_id: str, store: Store = Depends(current_store), db: Session = Depends(get_db)):
    t = get_tx(db, store, tx_id)
    # Catatan otomatis dihapus -> sumbernya dikembalikan agar bisa diproses ulang.
    for p in db.scalars(select(Payment).where(Payment.transaction_id == t.id)):
        p.status, p.transaction_id, p.verified_at = "menunggu", None, None
    for s in db.scalars(select(ShoppingList).where(ShoppingList.transaction_id == t.id)):
        s.status, s.transaction_id = "rencana", None
    db.flush()
    db.delete(t)
    db.commit()
    return {"ok": True, "summary": logic.summary(db, store)}


# ---------- Laporan ----------

@app.get("/api/report")
def get_report(dari: date, sampai: date, store: Store = Depends(current_store), db: Session = Depends(get_db)):
    if sampai < dari:
        raise HTTPException(422, "Tanggal akhir harus sama atau setelah tanggal awal.")
    if (sampai - dari).days > 366:
        raise HTTPException(422, "Rentang laporan maksimal 1 tahun.")
    return logic.report(db, store, dari, sampai)


# ---------- Pembayaran QRIS ----------

class PaymentIn(BaseModel):
    nominal: int = Rupiah
    nama_pelanggan: str | None = Field(default=None, max_length=100)


class VerifyIn(BaseModel):
    category_id: str | None = None


class RejectIn(BaseModel):
    alasan: str = Field(min_length=1, max_length=200)


def payment_out(p: Payment) -> dict:
    return {"id": p.id, "nominal": p.nominal, "nama_pelanggan": p.nama_pelanggan, "status": p.status,
            "alasan_tolak": p.alasan_tolak, "transaction_id": p.transaction_id,
            "created_at": p.created_at.isoformat(),
            "verified_at": p.verified_at.isoformat() if p.verified_at else None}


def get_payment(db: Session, store: Store, pid: str) -> Payment:
    p = db.get(Payment, pid)
    if not p or p.store_id != store.id:
        raise HTTPException(404, "Pembayaran tidak ditemukan.")
    if p.status != "menunggu":
        raise HTTPException(409, "Pembayaran ini sudah diperiksa.")
    return p


@app.get("/api/payments")
def list_payments(status: Literal["menunggu", "terverifikasi", "ditolak"] | None = None,
                  store: Store = Depends(current_store), db: Session = Depends(get_db)):
    q = select(Payment).where(Payment.store_id == store.id)
    if status:
        q = q.where(Payment.status == status)
    return [payment_out(p) for p in db.scalars(q.order_by(Payment.created_at.desc()).limit(200))]


@app.post("/api/payments")
def create_payment(body: PaymentIn, store: Store = Depends(current_store), db: Session = Depends(get_db)):
    p = Payment(store_id=store.id, nominal=body.nominal, nama_pelanggan=bersih(body.nama_pelanggan))
    db.add(p)
    db.commit()
    return payment_out(p)


@app.post("/api/payments/{pid}/verify")
def verify_payment(pid: str, body: VerifyIn, user: User = Depends(current_user),
                   store: Store = Depends(current_store), db: Session = Depends(get_db)):
    p = get_payment(db, store, pid)
    if body.category_id:
        cat = get_category(db, store, body.category_id, "masuk")
    else:
        cat = db.scalar(select(Category).where(Category.store_id == store.id, Category.jenis == "masuk",
                                               Category.nama == "Pembayaran QRIS")) \
            or db.scalar(select(Category).where(Category.store_id == store.id, Category.jenis == "masuk")
                         .order_by(Category.created_at))
    nama = f" dari {p.nama_pelanggan}" if p.nama_pelanggan else ""
    t = Transaction(store_id=store.id, category_id=cat.id, jenis="masuk", nominal=p.nominal,
                    tanggal=logic.today(), catatan=f"Pembayaran QRIS{nama}", sumber="qris", created_by=user.id)
    db.add(t)
    db.flush()
    p.status, p.transaction_id, p.verified_at = "terverifikasi", t.id, now()
    db.commit()
    return {"payment": payment_out(p), "summary": logic.summary(db, store)}


@app.post("/api/payments/{pid}/reject")
def reject_payment(pid: str, body: RejectIn, store: Store = Depends(current_store), db: Session = Depends(get_db)):
    p = get_payment(db, store, pid)
    p.status, p.alasan_tolak, p.verified_at = "ditolak", body.alasan.strip(), now()
    db.commit()
    return {"payment": payment_out(p)}


# ---------- Catatan belanja ----------

class ListIn(BaseModel):
    judul: str = Field(min_length=1, max_length=100)
    rencana_tanggal: date


class ItemIn(BaseModel):
    nama_barang: str = Field(min_length=1, max_length=100)
    jumlah: float = Field(default=1, gt=0, le=100_000)
    satuan: str | None = Field(default=None, max_length=20)
    estimasi_harga: int = Field(default=0, ge=0, le=999_999_999_999)
    harga_aktual: int | None = Field(default=None, ge=0, le=999_999_999_999)
    sudah_dibeli: bool = False


class ConvertIn(BaseModel):
    category_id: str | None = None


def harga_item(i: ShoppingItem) -> int:
    return i.harga_aktual if i.harga_aktual is not None else i.estimasi_harga


def list_out(s: ShoppingList, with_items: bool = False) -> dict:
    dibeli = [i for i in s.items if i.sudah_dibeli]
    out = {"id": s.id, "judul": s.judul, "rencana_tanggal": s.rencana_tanggal.isoformat(), "status": s.status,
           "transaction_id": s.transaction_id, "jumlah_barang": len(s.items), "jumlah_dibeli": len(dibeli),
           "estimasi_total": sum(i.estimasi_harga for i in s.items),
           "total_dibeli": sum(harga_item(i) for i in dibeli)}
    if with_items:
        out["items"] = [{"id": i.id, "nama_barang": i.nama_barang, "jumlah": i.jumlah, "satuan": i.satuan,
                         "estimasi_harga": i.estimasi_harga, "harga_aktual": i.harga_aktual,
                         "sudah_dibeli": i.sudah_dibeli} for i in s.items]
    return out


def get_list(db: Session, store: Store, lid: str, editable: bool = False) -> ShoppingList:
    s = db.get(ShoppingList, lid)
    if not s or s.store_id != store.id:
        raise HTTPException(404, "Daftar belanja tidak ditemukan.")
    if editable and s.status == "selesai":
        raise HTTPException(409, "Daftar ini sudah jadi catatan pengeluaran, jadi tidak bisa diubah lagi.")
    return s


def get_item(db: Session, store: Store, item_id: str) -> tuple[ShoppingItem, ShoppingList]:
    i = db.get(ShoppingItem, item_id)
    if not i:
        raise HTTPException(404, "Barang tidak ditemukan.")
    return i, get_list(db, store, i.shopping_list_id, editable=True)


@app.get("/api/shopping-lists")
def list_shopping(store: Store = Depends(current_store), db: Session = Depends(get_db)):
    rows = db.scalars(select(ShoppingList).where(ShoppingList.store_id == store.id)
                      .order_by(ShoppingList.status, ShoppingList.rencana_tanggal.desc(),
                                ShoppingList.created_at.desc())).all()
    return [list_out(s) for s in rows]


@app.post("/api/shopping-lists")
def create_shopping(body: ListIn, store: Store = Depends(current_store), db: Session = Depends(get_db)):
    s = ShoppingList(store_id=store.id, judul=body.judul.strip(), rencana_tanggal=body.rencana_tanggal)
    db.add(s)
    db.commit()
    return list_out(s, True)


@app.get("/api/shopping-lists/{lid}")
def get_shopping(lid: str, store: Store = Depends(current_store), db: Session = Depends(get_db)):
    return list_out(get_list(db, store, lid), True)


@app.put("/api/shopping-lists/{lid}")
def update_shopping(lid: str, body: ListIn, store: Store = Depends(current_store), db: Session = Depends(get_db)):
    s = get_list(db, store, lid, editable=True)
    s.judul, s.rencana_tanggal = body.judul.strip(), body.rencana_tanggal
    db.commit()
    return list_out(s, True)


@app.delete("/api/shopping-lists/{lid}")
def delete_shopping(lid: str, store: Store = Depends(current_store), db: Session = Depends(get_db)):
    s = get_list(db, store, lid)
    # Catatan pengeluaran yang sudah dibuat tetap ada; daftar belanja hanya rencana.
    db.delete(s)
    db.commit()
    return {"ok": True}


@app.post("/api/shopping-lists/{lid}/items")
def add_item(lid: str, body: ItemIn, store: Store = Depends(current_store), db: Session = Depends(get_db)):
    s = get_list(db, store, lid, editable=True)
    s.items.append(ShoppingItem(nama_barang=body.nama_barang.strip(), jumlah=body.jumlah,
                                satuan=bersih(body.satuan), estimasi_harga=body.estimasi_harga,
                                harga_aktual=body.harga_aktual, sudah_dibeli=body.sudah_dibeli))
    db.commit()
    db.refresh(s)
    return list_out(s, True)


@app.put("/api/shopping-items/{item_id}")
def update_item(item_id: str, body: ItemIn, store: Store = Depends(current_store), db: Session = Depends(get_db)):
    i, s = get_item(db, store, item_id)
    i.nama_barang, i.jumlah, i.satuan = body.nama_barang.strip(), body.jumlah, bersih(body.satuan)
    i.estimasi_harga, i.harga_aktual, i.sudah_dibeli = body.estimasi_harga, body.harga_aktual, body.sudah_dibeli
    db.commit()
    db.refresh(s)
    return list_out(s, True)


@app.delete("/api/shopping-items/{item_id}")
def delete_item(item_id: str, store: Store = Depends(current_store), db: Session = Depends(get_db)):
    i, s = get_item(db, store, item_id)
    s.items.remove(i)
    db.commit()
    db.refresh(s)
    return list_out(s, True)


@app.post("/api/shopping-lists/{lid}/convert")
def convert_shopping(lid: str, body: ConvertIn, user: User = Depends(current_user),
                     store: Store = Depends(current_store), db: Session = Depends(get_db)):
    s = get_list(db, store, lid, editable=True)
    dibeli = [i for i in s.items if i.sudah_dibeli]
    total = sum(harga_item(i) for i in dibeli)
    if not dibeli:
        raise HTTPException(422, "Centang dulu barang yang sudah dibeli.")
    if total <= 0:
        raise HTTPException(422, "Isi harga barang yang sudah dibeli dulu.")
    if body.category_id:
        cat = get_category(db, store, body.category_id, "keluar")
    else:
        cat = db.scalar(select(Category).where(Category.store_id == store.id, Category.jenis == "keluar",
                                               Category.nama == "Bahan Baku")) \
            or db.scalar(select(Category).where(Category.store_id == store.id, Category.jenis == "keluar")
                         .order_by(Category.created_at))
    tanggal = min(s.rencana_tanggal, logic.today())
    t = Transaction(store_id=store.id, category_id=cat.id, jenis="keluar", nominal=total, tanggal=tanggal,
                    catatan=f"Belanja: {s.judul} ({len(dibeli)} barang)"[:200], sumber="belanja",
                    created_by=user.id)
    db.add(t)
    db.flush()
    s.status, s.transaction_id = "selesai", t.id
    db.commit()
    return {"list": list_out(s, True), "summary": logic.summary(db, store)}
