import streamlit as st
import pandas as pd
from datetime import datetime
import io  # <-- TAMBAHAN: Wajib di-import untuk membuat file Excel di memori

# ==========================================
# 1. KONFIGURASI HALAMAN UTAMA
# ==========================================
st.set_page_config(page_title="Dashboard Tracking", page_icon="📊", layout="wide")

# ==========================================
# 2. INISIALISASI VARIABEL GLOBAL
# ==========================================
# Mengambil tanggal hari ini sesuai format yang kamu mau
tanggal_sekarang_str = datetime.now().strftime("%A, %d %B %Y")

# ==========================================
# 3. SETUP SIDEBAR & MENU NAVIGASI
# ==========================================
st.sidebar.title("Main Menu")
st.sidebar.caption("Pilih Dashboard:")
menu_pilihan = st.sidebar.radio("", ["Home", "Tracking Vendor"])

# ==========================================
# 4. LOGIKA KONTEN BERDASARKAN MENU
# ==========================================

# --- MENU 1: HOME ---
if menu_pilihan == "Home":
    st.title("🏠 Halaman Utama")
    
    # Tambahan teks khusus
    st.subheader("✨ Khusus buat Ramadhan Sahdian ✨")
    
    st.write("Selamat datang di Dashboard. Silakan pilih menu di samping untuk mulai memonitor pekerjaan.")

# --- MENU 7 (atau 2 di contoh ini): TRACKING VENDOR ---
elif menu_pilihan == "Tracking Vendor":
    st.header("🏢 Tracking Vendor")
    st.caption(f"📅 {tanggal_sekarang_str} | Sumber: data_po_sbm.xlsx")
    
    # 1. Membaca Database (Ditambah Cache agar lebih cepat saat difilter)
    @st.cache_data
    def load_data():
        df = pd.read_excel("data_po_sbm.xlsx")
        df.columns = df.columns.str.strip() 
        
        if "Tanggal" in df.columns:
            df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce").dt.strftime('%Y-%m-%d')
        return df

    try:
        df_vendor = load_data()
    except Exception as e:
        st.error(f"Gagal membaca file 'data_po_sbm.xlsx'. Pastikan file ada di folder yang sama dengan script. Error detail: {e}")
        st.stop()

    # 2. Pengecekan Kolom
    kolom_wajib = ["No Transaksi", "Tanggal", "Supplier", "Nama Barang"]
    kolom_ada = [col for col in kolom_wajib if col in df_vendor.columns]
    
    if len(kolom_ada) < len(kolom_wajib):
        st.warning(f"⚠️ Beberapa kolom tidak ditemukan di database. Kolom yang ada: {', '.join(df_vendor.columns)}")

    st.subheader("🔍 Pencarian Riwayat Vendor")
    
    # 3. Filter & Pencarian
    if "Supplier" in df_vendor.columns:
        col_v1, col_v2 = st.columns(2)
        
        with col_v1:
            list_supplier = ["Semua"] + sorted(df_vendor["Supplier"].dropna().astype(str).unique().tolist())
            pilih_supplier = st.selectbox("Pilih Supplier:", list_supplier, key="filter_supplier")
        
        with col_v2:
            cari_barang_vendor = st.text_input("Cari Nama Barang (Opsional):", placeholder="Ketik nama barang...")
        
        df_filter = df_vendor.copy()
        
        if pilih_supplier != "Semua":
            df_filter = df_filter[df_filter["Supplier"].astype(str) == pilih_supplier]
            
        if cari_barang_vendor and "Nama Barang" in df_filter.columns:
            df_filter = df_filter[df_filter["Nama Barang"].astype(str).str.contains(cari_barang_vendor, case=False, na=False)]
            
        st.divider()
        
        # 4. Tampilkan Hasil
        if not df_filter.empty:
            st.success(f"✅ Ditemukan {len(df_filter)} riwayat transaksi.")
            
            # Tampilkan dataframe di layar
            st.dataframe(df_filter[kolom_ada], use_container_width=True)
            
            # --- TAMBAHAN KODE UNTUK DOWNLOAD EXCEL ---
            # Menyiapkan buffer memori
            buffer = io.BytesIO()
            
            # Menyimpan dataframe hasil filter ke dalam buffer memori sebagai file Excel
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                # Disini kita export semua kolom dari df_filter (bukan cuma kolom_ada)
                df_filter.to_excel(writer, index=False, sheet_name='Data_Tracking')
            
            # Membuat tombol download
            st.download_button(
                label="📥 Download Data Excel",
                data=buffer.getvalue(),
                file_name=f"Data_Tracking_Vendor_{tanggal_sekarang_str}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            # -----------------------------------------
            
        else:
            st.info("Tidak ada data transaksi yang sesuai dengan pencarian Anda.")
            
    else:
        st.error("Kolom 'Supplier' tidak ditemukan di dalam file Excel.")