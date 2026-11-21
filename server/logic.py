"""Aturan hitung kas. Sisa kas dan laporan selalu dihitung dari tabel transaksi, tidak pernah disimpan."""
from calendar import monthrange
from contextvars import ContextVar
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from .db import Category, Payment, Store, Transaction

TZ = ZoneInfo("Asia/Jakarta")
# Zona waktu ponsel pemilik (WIB/WITA/WIT), diisi per permintaan dari header X-Timezone.
request_tz: ContextVar[ZoneInfo] = ContextVar("request_tz", default=TZ)
AMBANG_BAWAAN_PERSEN = 20  # bila ambang belum diatur: 20% dari modal awal
AMBANG_BAWAAN_MINIMUM = 500_000  # dipakai bila modal awal 0 atau 20% modal lebih kecil dari ini
JENDELA_PREDIKSI_HARI = 14
MIN_HARI_PREDIKSI = 3


def set_timezone(name: str | None) -> None:
    try:
        request_tz.set(ZoneInfo(name) if name else TZ)
    except (ZoneInfoNotFoundError, ValueError):
        request_tz.set(TZ)


def today() -> date:
    return datetime.now(request_tz.get()).date()


def ambang_efektif(store: Store) -> tuple[int, bool]:
    """Kembalikan (ambang, apakah_bawaan)."""
    if store.ambang_kas_menipis is not None:
        return store.ambang_kas_menipis, False
    return max(store.modal_awal * AMBANG_BAWAAN_PERSEN // 100, AMBANG_BAWAAN_MINIMUM), True


def _sum(jenis: str):
    return func.coalesce(func.sum(case((Transaction.jenis == jenis, Transaction.nominal), else_=0)), 0)


def totals(db: Session, store_id: str, dari: date | None = None, sampai: date | None = None) -> tuple[int, int, int]:
    """(total masuk, total keluar, jumlah transaksi) untuk rentang tanggal, inklusif."""
    q = select(_sum("masuk"), _sum("keluar"), func.count(Transaction.id)).where(Transaction.store_id == store_id)
    if dari:
        q = q.where(Transaction.tanggal >= dari)
    if sampai:
        q = q.where(Transaction.tanggal <= sampai)
    masuk, keluar, n = db.execute(q).one()
    return int(masuk), int(keluar), int(n)


def summary(db: Session, store: Store) -> dict:
    masuk, keluar, n = totals(db, store.id)
    hari = today()
    masuk_hari, keluar_hari, _ = totals(db, store.id, hari, hari)
    sisa = store.modal_awal + masuk - keluar
    ambang, bawaan = ambang_efektif(store)
    menunggu = db.scalar(
        select(func.count(Payment.id)).where(Payment.store_id == store.id, Payment.status == "menunggu")
    )
    return {
        "sisa_kas": sisa,
        "modal_awal": store.modal_awal,
        "total_masuk": masuk,
        "terpakai_operasional": keluar,
        "jumlah_transaksi": n,
        "hari_ini": {"tanggal": hari.isoformat(), "masuk": masuk_hari, "keluar": keluar_hari},
        "ambang_kas_menipis": ambang,
        "ambang_bawaan": bawaan,
        "kas_menipis": sisa < ambang,
        "pembayaran_menunggu": int(menunggu or 0),
    }


def daily_nets(db: Session, store_id: str, dari: date, sampai: date) -> dict[date, tuple[int, int]]:
    rows = db.execute(
        select(Transaction.tanggal, _sum("masuk"), _sum("keluar"))
        .where(Transaction.store_id == store_id, Transaction.tanggal >= dari, Transaction.tanggal <= sampai)
        .group_by(Transaction.tanggal)
    ).all()
    return {r[0]: (int(r[1]), int(r[2])) for r in rows}


def predict(nets: dict[date, int], first_date: date | None, hari: date, modal_awal: int,
            laba_total: int, laba_bulan_ini: int) -> dict:
    """Perkiraan laba dari rata-rata laba harian beberapa hari terakhir.

    nets: laba bersih (masuk - keluar) per tanggal dalam jendela. Hari tanpa catatan dihitung 0,
    karena resto yang tidak mencatat dianggap tidak ada uang bergerak.
    """
    if first_date is None:
        return {"cukup_data": False, "hari_data": 0, "min_hari": MIN_HARI_PREDIKSI}
    mulai = max(first_date, hari - timedelta(days=JENDELA_PREDIKSI_HARI - 1))
    hari_data = (hari - mulai).days + 1
    hari_tercatat = sum(1 for d in nets if mulai <= d <= hari)
    if hari_tercatat < MIN_HARI_PREDIKSI:
        return {"cukup_data": False, "hari_data": hari_tercatat, "min_hari": MIN_HARI_PREDIKSI}
    total = sum(v for d, v in nets.items() if mulai <= d <= hari)
    rata = round(total / hari_data)
    sisa_hari_bulan = monthrange(hari.year, hari.month)[1] - hari.day
    hasil = {
        "cukup_data": True,
        "dasar_hari": hari_data,
        "dasar_dari": mulai.isoformat(),
        "rata_rata_laba_harian": rata,
        "perkiraan_7_hari": rata * 7,
        "perkiraan_akhir_bulan": laba_bulan_ini + rata * sisa_hari_bulan,
        "laba_sejak_awal": laba_total,
        "persen_balik_modal": None,
        "perkiraan_hari_balik_modal": None,
    }
    if modal_awal > 0:
        hasil["persen_balik_modal"] = max(0, min(100, round(laba_total * 100 / modal_awal)))
        kurang = modal_awal - laba_total
        if kurang <= 0:
            hasil["perkiraan_hari_balik_modal"] = 0
        elif rata > 0:
            hasil["perkiraan_hari_balik_modal"] = -(-kurang // rata)
    return hasil


def report(db: Session, store: Store, dari: date, sampai: date) -> dict:
    hari = today()
    masuk_sebelum, keluar_sebelum, _ = totals(db, store.id, sampai=dari - timedelta(days=1))
    sisa_awal = store.modal_awal + masuk_sebelum - keluar_sebelum
    masuk, keluar, n = totals(db, store.id, dari, sampai)

    per_hari = daily_nets(db, store.id, dari, sampai)
    harian, berjalan, d = [], sisa_awal, dari
    while d <= sampai:
        m, k = per_hari.get(d, (0, 0))
        berjalan += m - k
        harian.append({"tanggal": d.isoformat(), "masuk": m, "keluar": k, "sisa_kas": berjalan})
        d += timedelta(days=1)

    def per_kategori(jenis: str, total: int) -> list[dict]:
        rows = db.execute(
            select(Category.nama, func.sum(Transaction.nominal), func.count(Transaction.id))
            .join(Category, Category.id == Transaction.category_id)
            .where(Transaction.store_id == store.id, Transaction.jenis == jenis,
                   Transaction.tanggal >= dari, Transaction.tanggal <= sampai)
            .group_by(Category.nama)
            .order_by(func.sum(Transaction.nominal).desc())
        ).all()
        return [{"nama": r[0], "total": int(r[1]), "jumlah": int(r[2]),
                 "persen": round(int(r[1]) * 100 / total) if total else 0} for r in rows]

    first_date = db.scalar(select(func.min(Transaction.tanggal)).where(Transaction.store_id == store.id))
    jendela = daily_nets(db, store.id, hari - timedelta(days=JENDELA_PREDIKSI_HARI - 1), hari)
    m_total, k_total, _ = totals(db, store.id, sampai=hari)
    m_bulan, k_bulan, _ = totals(db, store.id, hari.replace(day=1), hari)
    prediksi = predict({d: m - k for d, (m, k) in jendela.items()}, first_date, hari,
                       store.modal_awal, m_total - k_total, m_bulan - k_bulan)

    return {
        "dari": dari.isoformat(),
        "sampai": sampai.isoformat(),
        "masuk": masuk,
        "keluar": keluar,
        "laba": masuk - keluar,
        "jumlah_transaksi": n,
        "sisa_kas_awal": sisa_awal,
        "sisa_kas_akhir": sisa_awal + masuk - keluar,
        "harian": harian,
        "kategori_keluar": per_kategori("keluar", keluar),
        "kategori_masuk": per_kategori("masuk", masuk),
        "prediksi": prediksi,
    }
