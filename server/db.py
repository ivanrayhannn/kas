import os
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import (
    BigInteger, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from sqlalchemy.pool import NullPool

# Lokal: SQLite. Produksi: isi DATABASE_URL dengan connection string Supabase Postgres.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./kas.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql://" + DATABASE_URL[len("postgres://"):]
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL[len("postgresql://"):]

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Supabase Transaction pooler (port 6543) sudah mengelola pool dan tidak mendukung prepared statement,
    # jadi fungsi serverless tidak menahan koneksi dan psycopg tidak membuat prepared statement.
    engine = create_engine(DATABASE_URL, poolclass=NullPool, connect_args={"prepare_threshold": None})
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def new_id() -> str:
    return str(uuid.uuid4())


def now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    nama: Mapped[str] = mapped_column(String(100))
    password_hash: Mapped[str] = mapped_column(String(200))
    # Naik setiap kali keluar akun, sehingga semua token lama tidak berlaku lagi.
    token_version: Mapped[int] = mapped_column(Integer, default=0)
    reset_token_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reset_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Store(Base):
    __tablename__ = "stores"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True)
    nama_toko: Mapped[str] = mapped_column(String(100))
    alamat: Mapped[str | None] = mapped_column(String(200), nullable=True)
    telepon: Mapped[str | None] = mapped_column(String(30), nullable=True)
    # shortcut: gambar QR disimpan sebagai data URL di database (maks ~1 MB), pindah ke Supabase Storage bila butuh gambar lebih besar.
    qr_image: Mapped[str | None] = mapped_column(Text, nullable=True)
    modal_awal: Mapped[int] = mapped_column(BigInteger, default=0)
    ambang_kas_menipis: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id"), index=True)
    nama: Mapped[str] = mapped_column(String(50))
    jenis: Mapped[str] = mapped_column(String(6))  # masuk / keluar
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id"), index=True)
    category_id: Mapped[str] = mapped_column(ForeignKey("categories.id"))
    jenis: Mapped[str] = mapped_column(String(6))
    nominal: Mapped[int] = mapped_column(BigInteger)
    catatan: Mapped[str | None] = mapped_column(String(200), nullable=True)
    sumber: Mapped[str] = mapped_column(String(10), default="manual")  # manual / qris / belanja
    tanggal: Mapped[date] = mapped_column(Date, index=True)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    category: Mapped[Category] = relationship(lazy="joined")


class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id"), index=True)
    nominal: Mapped[int] = mapped_column(BigInteger)
    nama_pelanggan: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(14), default="menunggu")  # menunggu / terverifikasi / ditolak
    alasan_tolak: Mapped[str | None] = mapped_column(String(200), nullable=True)
    transaction_id: Mapped[str | None] = mapped_column(ForeignKey("transactions.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ShoppingList(Base):
    __tablename__ = "shopping_lists"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id"), index=True)
    judul: Mapped[str] = mapped_column(String(100))
    rencana_tanggal: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(10), default="rencana")  # rencana / selesai
    transaction_id: Mapped[str | None] = mapped_column(ForeignKey("transactions.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    items: Mapped[list["ShoppingItem"]] = relationship(
        cascade="all, delete-orphan", order_by="ShoppingItem.urutan", lazy="selectin"
    )


class ShoppingItem(Base):
    __tablename__ = "shopping_items"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    shopping_list_id: Mapped[str] = mapped_column(ForeignKey("shopping_lists.id"), index=True)
    nama_barang: Mapped[str] = mapped_column(String(100))
    jumlah: Mapped[float] = mapped_column(Float, default=1)
    satuan: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # Perkiraan dan harga aktual sama-sama total untuk barang itu (bukan harga satuan).
    estimasi_harga: Mapped[int] = mapped_column(BigInteger, default=0)
    harga_aktual: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    sudah_dibeli: Mapped[bool] = mapped_column(Boolean, default=False)
    urutan: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


def init_db() -> None:
    Base.metadata.create_all(engine)
