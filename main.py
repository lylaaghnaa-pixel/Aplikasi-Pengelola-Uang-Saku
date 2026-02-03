from datetime import datetime

saldo = 0.0
transactions = []  # each entry: (type, amount, desc, category, date)
budgets = {}       # category -> monthly_limit (float)


def _now():
    return datetime.now()


def tambah_pemasukan():
    """Menambah pemasukan ke saldo dengan kategori dan deskripsi"""
    global saldo
    try:
        jumlah = float(input("Masukkan jumlah pemasukan: "))
    except ValueError:
        print("Input tidak valid. Masukkan angka.")
        return

    if jumlah <= 0:
        print("Jumlah harus lebih dari 0.")
        return

    kategori = input("Kategori (misal: Gaji, Hadiah) [Umum]: ").strip() or "Umum"
    deskripsi = input("Deskripsi (opsional): ")
    tanggal = _now()

    saldo += jumlah
    transactions.append(("Pemasukan", jumlah, deskripsi, kategori, tanggal))
    print(f"✅ Pemasukan Rp {jumlah:,.2f} ({kategori}) berhasil ditambahkan.")


def tambah_pengeluaran():
    """Menambah pengeluaran, memeriksa saldo, dan notifikasi budget"""
    global saldo
    try:
        jumlah = float(input("Masukkan jumlah pengeluaran: "))
    except ValueError:
        print("Input tidak valid. Masukkan angka.")
        return

    if jumlah <= 0:
        print("Jumlah harus lebih dari 0.")
        return

    if jumlah > saldo:
        print("⚠️ Saldo tidak cukup untuk pengeluaran ini.")
        return

    kategori = input("Kategori (misal: Makan, Transport, Hiburan) [Umum]: ").strip() or "Umum"
    deskripsi = input("Deskripsi (opsional): ")
    tanggal = _now()

    saldo -= jumlah
    transactions.append(("Pengeluaran", jumlah, deskripsi, kategori, tanggal))
    print(f"✅ Pengeluaran Rp {jumlah:,.2f} ({kategori}) berhasil dicatat.")

    # Cek budget untuk kategori ini (per bulan)
    limit = budgets.get(kategori)
    if limit is not None:
        spent = _spent_this_month(kategori)
        if spent > limit:
            print(f"⚠️ WARNING: Anda telah melebihi budget untuk kategori '{kategori}'.")
            print(f"   Terpakai: Rp {spent:,.2f} / Limit: Rp {limit:,.2f}")


def _spent_this_month(category):
    """Jumlah pengeluaran di category untuk bulan berjalan"""
    now = _now()
    total = 0.0
    for t_type, amount, desc, cat, tanggal in transactions:
        if t_type == "Pengeluaran" and cat.lower() == category.lower():
            if tanggal.year == now.year and tanggal.month == now.month:
                total += amount
    return total


def set_budget():
    """Menetapkan atau memperbarui budget per kategori (per bulan)"""
    kategori = input("Masukkan nama kategori untuk di-budget-kan: ").strip()
    if not kategori:
        print("Nama kategori tidak boleh kosong.")
        return
    try:
        limit = float(input("Masukkan limit per bulan (contoh 1000000): "))
    except ValueError:
        print("Input tidak valid. Masukkan angka untuk limit.")
        return
    if limit <= 0:
        print("Limit harus lebih dari 0.")
        return
    budgets[kategori] = limit
    print(f"✅ Budget untuk kategori '{kategori}' diatur: Rp {limit:,.2f}")


def lihat_budgets():
    """Menampilkan semua budget dan status pemakaian bulan ini"""
    if not budgets:
        print("Belum ada budget yang ditetapkan.")
        return
    print("--- Daftar Budget (per bulan) ---")
    for cat, limit in budgets.items():
        spent = _spent_this_month(cat)
        status = "OK" if spent <= limit else "OVER"
        print(f"{cat}: Rp {spent:,.2f} terpakai / Rp {limit:,.2f} ({status})")
    print("---")


def total_summary():
    """Menampilkan total pemasukan, pengeluaran, dan breakdown per kategori"""
    total_in = sum(a for t, a, d, c, dt in transactions if t == "Pemasukan")
    total_out = sum(a for t, a, d, c, dt in transactions if t == "Pengeluaran")

    print("--- Ringkasan Total ---")
    print(f"Total pemasukan: Rp {total_in:,.2f}")
    print(f"Total pengeluaran: Rp {total_out:,.2f}")
    print(f"Saldo sekarang: Rp {saldo:,.2f}")

    # Breakdown per kategori
    by_cat = {}
    for t, a, d, c, dt in transactions:
        key = (t, c)
        by_cat[key] = by_cat.get(key, 0.0) + a

    if by_cat:
        print("\nBreakdown per kategori:")
        for (t, c), amt in by_cat.items():
            print(f"- {t} | {c}: Rp {amt:,.2f}")
    print("---")


def _get_month_transactions(year, month, t_type=None):
    """Kembalikan transaksi untuk bulan tertentu. t_type: 'Pemasukan' | 'Pengeluaran' | None"""
    result = []
    for t, a, d, c, dt in transactions:
        if dt.year == year and dt.month == month:
            if t_type is None or t == t_type:
                result.append((t, a, d, c, dt))
    return result


def laporan_bulanan():
    """Buat laporan untuk bulan tertentu (default: bulan sekarang)"""
    now = _now()
    inp = input(f"Masukkan bulan dan tahun (MM/YYYY) [default {now.month:02d}/{now.year}]: ").strip()
    if inp:
        try:
            month_str, year_str = inp.split("/")
            month = int(month_str)
            year = int(year_str)
        except Exception:
            print("Format tidak valid. Gunakan MM/YYYY.")
            return
    else:
        month = now.month
        year = now.year

    items = _get_month_transactions(year, month)
    if not items:
        print("Tidak ada transaksi untuk bulan tersebut.")
        return

    total_in = sum(a for t, a, d, c, dt in items if t == "Pemasukan")
    total_out = sum(a for t, a, d, c, dt in items if t == "Pengeluaran")

    by_cat = {}
    for t, a, d, c, dt in items:
        if t == "Pengeluaran":
            by_cat[c] = by_cat.get(c, 0.0) + a

    print(f"--- Laporan {month:02d}/{year} ---")
    print(f"Total pemasukan: Rp {total_in:,.2f}")
    print(f"Total pengeluaran: Rp {total_out:,.2f}")
    print("\nPengeluaran per kategori:")
    for cat, amt in sorted(by_cat.items(), key=lambda x: x[1], reverse=True):
        pct = amt / total_out * 100 if total_out else 0
        print(f"- {cat}: Rp {amt:,.2f} ({pct:.1f}%)")
    print("---")


def grafik_pengeluaran():
    """Buat grafik pengeluaran per kategori untuk bulan tertentu. Jika matplotlib tersedia, simpan gambar; jika tidak, tampilkan grafik ASCII."""
    now = _now()
    inp = input(f"Masukkan bulan dan tahun untuk grafik (MM/YYYY) [default {now.month:02d}/{now.year}]: ").strip()
    if inp:
        try:
            month_str, year_str = inp.split("/")
            month = int(month_str)
            year = int(year_str)
        except Exception:
            print("Format tidak valid. Gunakan MM/YYYY.")
            return
    else:
        month = now.month
        year = now.year

    items = _get_month_transactions(year, month, t_type="Pengeluaran")
    if not items:
        print("Tidak ada pengeluaran untuk bulan tersebut.")
        return

    by_cat = {}
    for t, a, d, c, dt in items:
        by_cat[c] = by_cat.get(c, 0.0) + a

    labels = list(by_cat.keys())
    values = [by_cat[k] for k in labels]

    # Coba matplotlib
    try:
        import matplotlib.pyplot as plt  # type: ignore
        fig, ax = plt.subplots(figsize=(8, max(4, len(labels) * 0.5)))
        ax.barh(labels, values, color='tab:blue')
        ax.set_xlabel('Jumlah (Rp)')
        ax.set_title(f'Pengeluaran per kategori {month:02d}/{year}')
        plt.tight_layout()
        filename = f"grafik_pengeluaran_{year}_{month:02d}.png"
        plt.savefig(filename)
        plt.close(fig)
        print(f"Grafik disimpan ke '{filename}'.")
    except Exception:
        # ASCII fallback
        max_width = 40
        max_val = max(values)
        print(f"--- Grafik (ASCII) Pengeluaran {month:02d}/{year} ---")
        for lab, val in zip(labels, values):
            bar_len = int(val / max_val * max_width) if max_val else 0
            bar = '#' * bar_len
            print(f"{lab[:15]:15} | {bar} {val:,.2f}")
        print("---")


def lihat_saldo():
    """Menampilkan saldo saat ini dan riwayat singkat transaksi"""
    print("---")
    print(f"Saldo saat ini: Rp {saldo:,.2f}")
    if transactions:
        print("\nRiwayat transaksi (terbaru 10):")
        for idx, (t_type, amount, desc, cat, tanggal) in enumerate(transactions[-10:], start=1):
            desc_text = f" - {desc}" if desc.strip() else ""
            print(f"{idx}. [{tanggal.strftime('%Y-%m-%d')}] {t_type} ({cat}): Rp {amount:,.2f}{desc_text}")
    else:
        print("Belum ada transaksi.")
    print("---")


def menu():
    print("=== Aplikasi Pengelola Uang Saku ===")
    print("1. Tambah pemasukan")
    print("2. Tambah pengeluaran")
    print("3. Lihat saldo")
    print("4. Ringkasan total")
    print("5. Atur / Lihat budget per kategori")
    print("6. Laporan & Grafik bulanan")
    print("7. Keluar")


if __name__ == '__main__':
    while True:
        menu()
        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            tambah_pemasukan()
        elif pilihan == "2":
            tambah_pengeluaran()
        elif pilihan == "3":
            lihat_saldo()
        elif pilihan == "4":
            total_summary()
        elif pilihan == "5":
            print("1. Atur budget\n2. Lihat budget\n3. Kembali")
            sub = input("Pilih: ").strip()
            if sub == "1":
                set_budget()
            elif sub == "2":
                lihat_budgets()
            else:
                pass
        elif pilihan == "6":
            print("1. Laporan bulanan\n2. Grafik pengeluaran\n3. Kembali")
            sub = input("Pilih: ").strip()
            if sub == "1":
                laporan_bulanan()
            elif sub == "2":
                grafik_pengeluaran()
            else:
                pass
        elif pilihan == "7":
            print("Terima kasih!")
            break
        else:
            print("Pilihan tidak valid")
            print()
