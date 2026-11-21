import os
from datetime import date, timedelta

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool

from server import db as dbmod

# Satu koneksi in-memory bersama, supaya semua sesi melihat data yang sama.
dbmod.engine = dbmod.create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
dbmod.SessionLocal.configure(bind=dbmod.engine)

from server import logic  # noqa: E402
from server.main import app  # noqa: E402

TODAY = logic.today().isoformat()


@pytest.fixture(autouse=True)
def fresh_db():
    dbmod.Base.metadata.drop_all(dbmod.engine)
    dbmod.Base.metadata.create_all(dbmod.engine)


@pytest.fixture
def c():
    return TestClient(app)


def owner(c, email="pemilik@resto.example", modal=1_000_000, ambang=None):
    r = c.post("/api/auth/register", json={"nama": "Bu Sari", "email": email, "password": "rahasia123"})
    assert r.status_code == 200, r.text
    h = {"authorization": f"Bearer {r.json()['token']}"}
    r = c.post("/api/store", headers=h, json={"nama_toko": "Warung Sari", "modal_awal": modal,
                                              "ambang_kas_menipis": ambang})
    assert r.status_code == 200, r.text
    cats = c.get("/api/categories", headers=h).json()
    return h, {(x["nama"], x["jenis"]): x["id"] for x in cats}


def tx(c, h, cats, jenis, nominal, cat=None, tanggal=TODAY, catatan=None):
    cat = cat or ("Penjualan" if jenis == "masuk" else "Bahan Baku")
    r = c.post("/api/transactions", headers=h, json={"jenis": jenis, "nominal": nominal,
                                                     "category_id": cats[(cat, jenis)], "tanggal": tanggal,
                                                     "catatan": catatan})
    assert r.status_code == 200, r.text
    return r.json()


def test_sisa_kas_modal_plus_masuk_minus_keluar(c):
    h, cats = owner(c)
    s = c.get("/api/summary", headers=h).json()
    assert s["sisa_kas"] == 1_000_000 and s["jumlah_transaksi"] == 0
    tx(c, h, cats, "masuk", 250_000)
    r = tx(c, h, cats, "keluar", 75_000)
    assert r["summary"]["sisa_kas"] == 1_175_000
    assert r["summary"]["terpakai_operasional"] == 75_000
    assert r["summary"]["hari_ini"] == {"tanggal": TODAY, "masuk": 250_000, "keluar": 75_000}


def test_perbaiki_dan_hapus_mengubah_saldo(c):
    h, cats = owner(c)
    t = tx(c, h, cats, "keluar", 100_000)["transaction"]
    body = {"jenis": "keluar", "nominal": 40_000, "category_id": cats[("Operasional", "keluar")], "tanggal": TODAY}
    r = c.put(f"/api/transactions/{t['id']}", headers=h, json=body).json()
    assert r["summary"]["sisa_kas"] == 960_000 and r["transaction"]["kategori"] == "Operasional"
    r = c.delete(f"/api/transactions/{t['id']}", headers=h).json()
    assert r["summary"]["sisa_kas"] == 1_000_000 and r["summary"]["terpakai_operasional"] == 0


def test_validasi_transaksi(c):
    h, cats = owner(c)
    base = {"jenis": "masuk", "category_id": cats[("Penjualan", "masuk")], "tanggal": TODAY}
    assert c.post("/api/transactions", headers=h, json={**base, "nominal": 0}).status_code == 422
    assert c.post("/api/transactions", headers=h, json={**base, "nominal": -5}).status_code == 422
    besok = (logic.today() + timedelta(days=1)).isoformat()
    assert c.post("/api/transactions", headers=h, json={**base, "nominal": 5, "tanggal": besok}).status_code == 422
    salah_jenis = {**base, "nominal": 5, "category_id": cats[("Bahan Baku", "keluar")]}
    assert c.post("/api/transactions", headers=h, json=salah_jenis).status_code == 422


def test_kas_menipis_dan_ambang_bawaan(c):
    h, cats = owner(c, modal=1_000_000)  # ambang bawaan: maks(20% modal, 500.000) = 500.000
    s = c.get("/api/summary", headers=h).json()
    assert s["ambang_bawaan"] and s["ambang_kas_menipis"] == 500_000 and not s["kas_menipis"]
    t = tx(c, h, cats, "keluar", 600_000)
    assert t["summary"]["kas_menipis"]
    c.delete(f"/api/transactions/{t['transaction']['id']}", headers=h)
    assert not c.get("/api/summary", headers=h).json()["kas_menipis"]


def test_data_toko_terpisah(c):
    h1, cats1 = owner(c, "a@resto.example")
    h2, _ = owner(c, "b@resto.example")
    t = tx(c, h1, cats1, "masuk", 10_000)["transaction"]
    assert c.get(f"/api/transactions/{t['id']}", headers=h2).status_code == 404
    assert c.delete(f"/api/transactions/{t['id']}", headers=h2).status_code == 404
    assert c.get("/api/transactions", headers=h2).json()["total"] == 0
    body = {"jenis": "masuk", "nominal": 1, "category_id": cats1[("Penjualan", "masuk")], "tanggal": TODAY}
    assert c.post("/api/transactions", headers=h2, json=body).status_code == 404


def test_qris_verifikasi_jadi_uang_masuk_dan_tolak_tidak_mengubah_kas(c):
    h, cats = owner(c)
    p1 = c.post("/api/payments", headers=h, json={"nominal": 45_000, "nama_pelanggan": "Meja 3"}).json()
    p2 = c.post("/api/payments", headers=h, json={"nominal": 20_000}).json()
    assert c.get("/api/summary", headers=h).json()["pembayaran_menunggu"] == 2
    r = c.post(f"/api/payments/{p1['id']}/verify", headers=h, json={}).json()
    assert r["payment"]["status"] == "terverifikasi" and r["summary"]["sisa_kas"] == 1_045_000
    t = c.get(f"/api/transactions/{r['payment']['transaction_id']}", headers=h).json()
    assert t["sumber"] == "qris" and t["kategori"] == "Pembayaran QRIS" and t["nominal"] == 45_000
    assert c.post(f"/api/payments/{p2['id']}/reject", headers=h, json={"alasan": ""}).status_code == 422
    r = c.post(f"/api/payments/{p2['id']}/reject", headers=h, json={"alasan": "Tidak ada di mutasi"}).json()
    assert r["payment"]["alasan_tolak"] == "Tidak ada di mutasi"
    assert c.get("/api/summary", headers=h).json()["sisa_kas"] == 1_045_000
    assert c.post(f"/api/payments/{p1['id']}/verify", headers=h, json={}).status_code == 409


def test_catatan_otomatis_terkunci_dan_hapus_mengembalikan_sumber(c):
    h, cats = owner(c)
    p = c.post("/api/payments", headers=h, json={"nominal": 30_000}).json()
    tid = c.post(f"/api/payments/{p['id']}/verify", headers=h, json={}).json()["payment"]["transaction_id"]
    body = {"jenis": "masuk", "nominal": 1, "category_id": cats[("Penjualan", "masuk")], "tanggal": TODAY}
    assert c.put(f"/api/transactions/{tid}", headers=h, json=body).status_code == 409
    c.delete(f"/api/transactions/{tid}", headers=h)
    assert c.get("/api/payments", headers=h).json()[0]["status"] == "menunggu"


def test_belanja_estimasi_dan_jadi_pengeluaran(c):
    h, cats = owner(c)
    s = c.post("/api/shopping-lists", headers=h, json={"judul": "Belanja Besok", "rencana_tanggal": TODAY}).json()
    s = c.post(f"/api/shopping-lists/{s['id']}/items", headers=h,
               json={"nama_barang": "Cabai", "jumlah": 2, "satuan": "kg", "estimasi_harga": 80_000}).json()
    s = c.post(f"/api/shopping-lists/{s['id']}/items", headers=h,
               json={"nama_barang": "Beras", "jumlah": 10, "satuan": "kg", "estimasi_harga": 150_000}).json()
    assert s["estimasi_total"] == 230_000
    assert c.post(f"/api/shopping-lists/{s['id']}/convert", headers=h, json={}).status_code == 422
    cabai = s["items"][0]
    s = c.put(f"/api/shopping-items/{cabai['id']}", headers=h,
              json={**cabai, "harga_aktual": 90_000, "sudah_dibeli": True}).json()
    assert s["jumlah_dibeli"] == 1 and s["total_dibeli"] == 90_000
    r = c.post(f"/api/shopping-lists/{s['id']}/convert", headers=h, json={}).json()
    assert r["list"]["status"] == "selesai" and r["summary"]["sisa_kas"] == 910_000
    t = c.get(f"/api/transactions/{r['list']['transaction_id']}", headers=h).json()
    assert t["sumber"] == "belanja" and t["kategori"] == "Bahan Baku" and t["jenis"] == "keluar"
    assert c.post(f"/api/shopping-lists/{s['id']}/items", headers=h,
                  json={"nama_barang": "Telur"}).status_code == 409


def test_laporan_harian_dan_kategori(c):
    h, cats = owner(c)
    kemarin = (logic.today() - timedelta(days=1)).isoformat()
    tx(c, h, cats, "masuk", 300_000, tanggal=kemarin)
    tx(c, h, cats, "keluar", 100_000, tanggal=kemarin)
    tx(c, h, cats, "keluar", 50_000, cat="Transportasi")
    r = c.get("/api/report", headers=h, params={"dari": TODAY, "sampai": TODAY}).json()
    assert r["sisa_kas_awal"] == 1_200_000 and r["sisa_kas_akhir"] == 1_150_000 and r["laba"] == -50_000
    r = c.get("/api/report", headers=h, params={"dari": kemarin, "sampai": TODAY}).json()
    assert [d["sisa_kas"] for d in r["harian"]] == [1_200_000, 1_150_000]
    assert r["kategori_keluar"][0] == {"nama": "Bahan Baku", "total": 100_000, "jumlah": 1, "persen": 67}
    assert not r["prediksi"]["cukup_data"]


def test_prediksi():
    hari = date(2026, 11, 21)
    nets = {hari - timedelta(days=i): 100_000 for i in range(5)}
    p = logic.predict(nets, hari - timedelta(days=4), hari, 1_000_000, 500_000, 500_000)
    assert p["rata_rata_laba_harian"] == 100_000 and p["perkiraan_7_hari"] == 700_000
    assert p["perkiraan_akhir_bulan"] == 500_000 + 9 * 100_000
    assert p["persen_balik_modal"] == 50 and p["perkiraan_hari_balik_modal"] == 5
    assert not logic.predict({hari: 1}, hari, hari, 0, 1, 1)["cukup_data"]


def test_akun_keluar_dan_lupa_sandi(c):
    h, _ = owner(c)
    assert c.post("/api/auth/login", json={"email": "pemilik@resto.example", "password": "salah"}).status_code == 401
    assert c.post("/api/auth/logout", headers=h).status_code == 200
    assert c.get("/api/me", headers=h).status_code == 401
    r = c.post("/api/auth/forgot", json={"email": "tidak.ada@resto.example"}).json()
    assert "dev_reset_url" not in r
    link = c.post("/api/auth/forgot", json={"email": "pemilik@resto.example"}).json()["dev_reset_url"]
    token = link.split("token=")[1]
    assert c.post("/api/auth/reset", json={"token": token, "password": "sandibaru123"}).status_code == 200
    assert c.post("/api/auth/reset", json={"token": token, "password": "sandibaru123"}).status_code == 400
    r = c.post("/api/auth/login", json={"email": "pemilik@resto.example", "password": "sandibaru123"})
    assert r.status_code == 200 and r.json()["store"]["nama_toko"] == "Warung Sari"


def test_kategori_terpakai_tidak_bisa_dihapus(c):
    h, cats = owner(c)
    tx(c, h, cats, "masuk", 1_000)
    assert c.delete(f"/api/categories/{cats[('Penjualan', 'masuk')]}", headers=h).status_code == 409
    assert c.delete(f"/api/categories/{cats[('Gaji Karyawan', 'keluar')]}", headers=h).status_code == 200
    assert c.post("/api/categories", headers=h, json={"nama": "penjualan", "jenis": "masuk"}).status_code == 409


def test_tanggal_mengikuti_zona_waktu_ponsel(c):
    from datetime import datetime
    from zoneinfo import ZoneInfo
    h, cats = owner(c)
    tz = "Pacific/Kiritimati"  # UTC+14: hampir selalu sudah "besok" dibanding WIB
    lokal = datetime.now(ZoneInfo(tz)).date().isoformat()
    hz = {**h, "x-timezone": tz}
    body = {"jenis": "masuk", "nominal": 1_000, "category_id": cats[("Penjualan", "masuk")], "tanggal": lokal}
    r = c.post("/api/transactions", headers=hz, json=body)
    assert r.status_code == 200 and r.json()["summary"]["hari_ini"]["tanggal"] == lokal
    assert c.get("/api/summary", headers={**h, "x-timezone": "bukan/zona"}).status_code == 200
