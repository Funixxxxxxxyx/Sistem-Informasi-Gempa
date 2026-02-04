import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import io

# ===========================
# PAGE CONFIG
# ===========================
st.set_page_config(
    page_title="Sistem Pencarian Data Gempa Indonesia",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk design BMKG style
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .header-title {
        text-align: center;
        color: #1e3a5f;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .header-subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1em;
        margin-bottom: 1.5rem;
    }
    .status-badge {
        text-align: center;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: 600;
        font-size: 0.9em;
        margin-bottom: 1rem;
    }
    .status-live {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .status-backup {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeeba;
    }
    .status-combined {
        background-color: #cfe2ff;
        color: #084298;
        border: 1px solid #b6d4fe;
    }
    .metric-card {
        background-color: #f0f4f8;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1e3a5f;
    }
    .metric-value {
        font-size: 1.8em;
        font-weight: bold;
        color: #1e3a5f;
    }
    .metric-label {
        color: #666;
        font-size: 0.95em;
        margin-top: 0.5rem;
    }
    .result-title {
        color: #1e3a5f;
        font-size: 1.5em;
        font-weight: bold;
        margin-bottom: 1rem;
        border-bottom: 2px solid #1e3a5f;
        padding-bottom: 0.5rem;
    }
    .info-box {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ===========================
# LOAD DATA - EXCEL + BMKG COMBINED
# ===========================

@st.cache_data
def load_data_excel():
    """Load data dari 6 file Excel (Aug-Dec 2025)"""
    try:
        print("Loading data dari Excel (Aug-Dec 2025)...")
        
        files = [
            "data/DataGempaAgustus2025.xlsx",
            "data/DataGempaDesember2025.xlsx",
            "data/DataGempaJuni2025.xlsx",
            "data/DataGempaNovember2025.xlsx",
            "data/DataGempaOktober2025.xlsx",
            "data/DataGempaSeptember2025.xlsx"
        ]
        
        dfs = []
        for file in files:
            try:
                df_temp = pd.read_excel(file, header=1)
                dfs.append(df_temp)
            except FileNotFoundError:
                continue
        
        if not dfs:
            return None
        
        df = pd.concat(dfs, ignore_index=True)
        
        # Clean & format
        df = df[["Date time", "Latitude", "Longitude", "Magnitude", "Depth (km)", "Location"]]
        df.columns = ["waktu", "latitude", "longitude", "magnitudo", "kedalaman_km", "lokasi"]
        
        df["waktu"] = pd.to_datetime(df["waktu"])
        df["source"] = "Excel (Historical)"
        
        return df
    except Exception as e:
        print(f"Error loading Excel: {e}")
        return None


@st.cache_data(ttl=3600)
def load_data_bmkg():
    """Load data dari BMKG API (1 Jan 2026 - hari ini)"""
    gempa_list = []
    processed_gempa = set()
    
    try:
        # Multiple endpoints untuk data lebih lengkap
        endpoints = [
            "https://data.bmkg.go.id/DataMKG/TEWS/gempaterkini.json",
            "https://data.bmkg.go.id/DataMKG/TEWS/gempadirasakan.json",
            "https://data.bmkg.go.id/DataMKG/TEWS/gemparekomendasi.json"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                if 'Infogempa' not in data or 'gempa' not in data['Infogempa']:
                    continue
                
                for gempa in data['Infogempa']['gempa']:
                    try:
                        waktu = pd.to_datetime(gempa.get('Jam', ''), utc=True)
                        
                        # Parse kedalaman
                        kedalaman_str = gempa.get('Kedalaman', '0').replace(' km', '').replace(' LS', '').replace(',', '.').strip()
                        kedalaman_km = float(kedalaman_str) if kedalaman_str else 0
                        
                        # Parse magnitudo
                        magnitudo = float(gempa.get('Magnitude', 0))
                        
                        # Parse lokasi
                        lokasi = gempa.get('Wilayah', 'Unknown').strip()
                        
                        # Parse Lintang
                        lintang_raw = str(gempa.get('Lintang', '0')).replace(' LS', '').replace(' LU', '').replace(',', '.').strip()
                        latitude = float(lintang_raw) if lintang_raw else 0
                        if 'LS' in str(gempa.get('Lintang', '')):
                            latitude = -latitude
                        
                        # Parse Bujur
                        bujur_raw = str(gempa.get('Bujur', '0')).replace(' BT', '').replace(' BB', '').replace(',', '.').strip()
                        longitude = float(bujur_raw) if bujur_raw else 0
                        if 'BB' in str(gempa.get('Bujur', '')):
                            longitude = -longitude
                        
                        # Validasi
                        if not (waktu and latitude and longitude and magnitudo):
                            continue
                        
                        # Avoid duplicate
                        gempa_key = (waktu.timestamp(), latitude, longitude, magnitudo)
                        if gempa_key in processed_gempa:
                            continue
                        processed_gempa.add(gempa_key)
                        
                        gempa_list.append({
                            'waktu': waktu,
                            'latitude': latitude,
                            'longitude': longitude,
                            'magnitudo': magnitudo,
                            'kedalaman_km': kedalaman_km,
                            'lokasi': lokasi,
                            'source': 'BMKG Real-time'
                        })
                    except (ValueError, TypeError, KeyError):
                        continue
            
            except requests.exceptions.RequestException:
                continue
        
        if not gempa_list:
            return None
        
        df = pd.DataFrame(gempa_list)
        df = df.dropna(subset=['latitude', 'longitude', 'magnitudo'])
        
        if df.empty:
            return None
        
        return df
    
    except Exception as e:
        print(f"BMKG API Error: {e}")
        return None


def process_data(df):
    """Process dan format data gempa"""
    if df is None or df.empty:
        return None
    
    # Clean
    df = df.dropna(subset=['latitude', 'longitude', 'magnitudo'])
    
    # Standardisasi
    df["latitude"] = pd.to_numeric(df["latitude"], errors='coerce').round(4)
    df["longitude"] = pd.to_numeric(df["longitude"], errors='coerce').round(4)
    df["magnitudo"] = pd.to_numeric(df["magnitudo"], errors='coerce').round(2)
    df["kedalaman_km"] = pd.to_numeric(df["kedalaman_km"], errors='coerce').round(2)
    df['lokasi'] = df['lokasi'].fillna('Unknown').astype(str).str.strip()
    
    # Format waktu
    df["waktu"] = pd.to_datetime(df["waktu"], utc=True)
    df["tanggal"] = df["waktu"].dt.strftime("%d-%m-%Y")
    df["waktu_display"] = df["waktu"].dt.strftime("%Y-%m-%d %H:%M")
    
    # Sort by waktu (terbaru dulu)
    df = df.sort_values("waktu", ascending=False).reset_index(drop=True)
    
    # Kategorisasi Magnitudo
    def kat_mag(m):
        if m < 3.0: return "Kecil (< 3)"
        elif m < 4.0: return "Ringan (3 - 4)"
        elif m < 5.0: return "Sedang (4 - 5)"
        elif m < 6.0: return "Kuat (5 - 6)"
        else: return "Besar (> 6)"
    
    # Kategorisasi Kedalaman
    def kat_depth(d):
        if d <= 70: return "Dangkal (< 70 km)"
        elif d <= 300: return "Menengah (70 - 300 km)"
        else: return "Dalam (> 300 km)"
    
    df["kategori_magnitudo"] = df["magnitudo"].apply(kat_mag)
    df["kategori_kedalaman"] = df["kedalaman_km"].apply(kat_depth)
    
    return df


def load_data():
    """Load data combined: Excel (Aug-Dec 2025) + BMKG (1 Jan - hari ini)"""
    
    # Load Excel
    df_excel = load_data_excel()
    
    # Load BMKG (dengan cache 1 jam)
    df_bmkg = load_data_bmkg()
    
    # Combine
    if df_excel is not None and df_bmkg is not None:
        df = pd.concat([df_excel, df_bmkg], ignore_index=True)
        data_source = "Excel + BMKG Real-time"
        is_combined = True
    elif df_excel is not None:
        df = df_excel
        data_source = "Excel Only (BMKG unavailable)"
        is_combined = False
    elif df_bmkg is not None:
        df = df_bmkg
        data_source = "BMKG Real-time (Excel data before Jan 1)"
        is_combined = False
    else:
        st.error("❌ Tidak dapat memuat data dari Excel atau BMKG")
        return None, "", False
    
    # Process
    df = process_data(df)
    
    if df is None or df.empty:
        st.error("❌ Data kosong setelah processing")
        return None, "", False
    
    return df, data_source, is_combined


# Load data
df, data_source, is_combined = load_data()

if df is None or df.empty:
    st.error("❌ Gagal memuat data gempa")
    st.stop()

# ===========================
# HEADER
# ===========================
st.markdown('<p class="header-title">📍 SISTEM PENCARIAN DATA GEMPA INDONESIA</p>', unsafe_allow_html=True)

# Calculate data range
min_date = df['waktu'].min()
max_date = df['waktu'].max()
days_span = (max_date - min_date).days

# Status Badge
if is_combined:
    st.markdown(f'<div class="status-badge status-combined">🔵 {data_source} | Range: {min_date.strftime("%d-%m-%Y")} s/d {max_date.strftime("%d-%m-%Y")} ({days_span} hari)</div>', unsafe_allow_html=True)
elif "Real-time" in data_source:
    st.markdown(f'<div class="status-badge status-live">🟢 {data_source} | Update: {max_date.strftime("%d-%m-%Y %H:%M")} WIB</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="status-badge status-backup">🟡 {data_source}</div>', unsafe_allow_html=True)

st.markdown('<p class="header-subtitle">Data dari Badan Meteorologi, Klimatologi, dan Geofisika (BMKG) + Historical Excel</p>', unsafe_allow_html=True)

# ===========================
# SIDEBAR
# ===========================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Logo_BMKG.png/200px-Logo_BMKG.png", width=200)
    st.title("Menu Pencarian")
    
    menu = st.radio(
        "Pilih menu pencarian:",
        ["🏘️ Cari Wilayah", "📊 Cari Magnitudo", "📅 Cari Tanggal", "🔧 Kombinasi Filter"],
        index=0
    )
    
    st.markdown("---")
    st.markdown(f"**📊 Total Data:** {len(df):,} gempa")
    st.markdown(f"**🗺️ Total Wilayah:** {df['lokasi'].nunique()}")
    st.markdown(f"**📅 Range Data:** {min_date.strftime('%d-%m-%Y')} s/d {max_date.strftime('%d-%m-%Y')}")
    st.markdown(f"**⏰ Update:** Real-time (auto 1 jam)")
    
    st.markdown("---")
    st.markdown("📡 **Data Source:**")
    if is_combined:
        st.info("✅ Excel (Aug-Dec) + BMKG (1 Jan-sekarang)")
    elif "Real-time" in data_source:
        st.success("🟢 Real-time BMKG")
    else:
        st.warning("🟡 Excel Backup")
    
    # Data distribution
    with st.expander("📊 Distribusi Data", expanded=False):
        if 'source' in df.columns:
            source_count = df['source'].value_counts()
            for source, count in source_count.items():
                st.metric(source, f"{count:,}")

# ===========================
# MENU 1: CARI WILAYAH
# ===========================
if menu == "🏘️ Cari Wilayah":
    st.markdown('<p class="result-title">Pencarian Berdasarkan Wilayah/Lokasi</p>', unsafe_allow_html=True)
    
    if df.empty:
        st.error("❌ Data tidak tersedia")
    else:
        st.info("💡 **Data tersedia dari:** Agustus 2025 - hari ini (seamless combine Excel + Real-time BMKG)")
        
        wilayah_list = sorted(df['lokasi'].dropna().unique())
        
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_wilayah = st.selectbox(
                "Pilih Wilayah/Lokasi:",
                wilayah_list,
                key="wilayah_select"
            )
        with col2:
            search_button = st.button("🔍 Cari", key="wilayah_button", use_container_width=True)
        
        if search_button:
            df_filtered = df[df['lokasi'].str.contains(selected_wilayah, case=False, na=False)]
            
            if len(df_filtered) == 0:
                st.error(f"❌ Tidak ada data untuk '{selected_wilayah}'")
            else:
                st.success(f"✅ Ditemukan {len(df_filtered)} gempa di {selected_wilayah}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{len(df_filtered)}</div>
                        <div class="metric-label">Total Gempa</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{df_filtered['magnitudo'].max():.2f}</div>
                        <div class="metric-label">Magnitudo Maksimal</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{df_filtered['magnitudo'].mean():.2f}</div>
                        <div class="metric-label">Magnitudo Rata-rata</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{df_filtered['kedalaman_km'].mean():.1f} km</div>
                        <div class="metric-label">Kedalaman Rata-rata</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Data Source breakdown
                if 'source' in df_filtered.columns:
                    source_breakdown = df_filtered['source'].value_counts()
                    st.subheader("📊 Breakdown Data:")
                    for source, count in source_breakdown.items():
                        st.write(f"- {source}: {count} gempa")
                
                st.markdown("---")
                
                st.subheader("📋 Data Gempa")
                display_df = df_filtered[["waktu_display", "magnitudo", "kategori_magnitudo", "kedalaman_km", "kategori_kedalaman", "latitude", "longitude"]].copy()
                display_df.columns = ["Waktu", "Magnitudo", "Kategori Mag", "Kedalaman (km)", "Kategori Depth", "Latitude", "Longitude"]
                
                st.dataframe(display_df, use_container_width=True, height=400)
                
                csv = display_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"gempa_{selected_wilayah.replace(' ', '_').replace(',', '')}.csv",
                    mime="text/csv"
                )

# ===========================
# MENU 2: CARI MAGNITUDO
# ===========================
elif menu == "📊 Cari Magnitudo":
    st.markdown('<p class="result-title">Pencarian Berdasarkan Magnitudo</p>', unsafe_allow_html=True)
    
    if df.empty:
        st.error("❌ Data tidak tersedia")
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            mag_type = st.radio("Tipe Pencarian:", ["Single", "Range"], horizontal=True)
        
        with col2:
            if mag_type == "Single":
                mag_input = st.number_input("Magnitudo:", min_value=1.0, max_value=10.0, value=3.0, step=0.1)
                mag_min = mag_input
                mag_max = mag_input + 0.99
                mag_display = f"{mag_min:.2f}-{mag_max:.2f}"
            else:
                col_min, col_max = st.columns(2)
                with col_min:
                    mag_min = st.number_input("Dari:", min_value=1.0, max_value=10.0, value=3.0, step=0.1)
                with col_max:
                    mag_max = st.number_input("Sampai:", min_value=1.0, max_value=10.0, value=5.0, step=0.1)
                mag_display = f"{mag_min:.2f}-{mag_max:.2f}"
        
        with col3:
            search_button = st.button("🔍 Cari", key="mag_button", use_container_width=True)
        
        if search_button:
            df_filtered = df[(df['magnitudo'] >= mag_min) & (df['magnitudo'] <= mag_max)]
            
            if len(df_filtered) == 0:
                st.error(f"❌ Tidak ada gempa dengan magnitudo {mag_display}")
            else:
                st.success(f"✅ Ditemukan {len(df_filtered)} gempa dengan magnitudo {mag_display}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{len(df_filtered)}</div>
                        <div class="metric-label">Total Gempa</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    wilayah_count = df_filtered['lokasi'].nunique()
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{wilayah_count}</div>
                        <div class="metric-label">Wilayah Terkena</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{df_filtered['kedalaman_km'].min():.1f} km</div>
                        <div class="metric-label">Kedalaman Minimum</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{df_filtered['kedalaman_km'].max():.1f} km</div>
                        <div class="metric-label">Kedalaman Maksimal</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Data breakdown
                if 'source' in df_filtered.columns:
                    source_breakdown = df_filtered['source'].value_counts()
                    st.subheader("📊 Breakdown Data:")
                    for source, count in source_breakdown.items():
                        st.write(f"- {source}: {count} gempa")
                
                st.markdown("---")
                
                st.subheader("🗺️ Wilayah yang Terkena (Klik untuk melihat detail)")
                wilayah_list = df_filtered['lokasi'].value_counts().sort_values(ascending=False)
                
                for idx, (wilayah, count) in enumerate(wilayah_list.items(), 1):
                    with st.expander(f"**{idx}. {wilayah}** - {count} gempa", expanded=False):
                        df_wilayah = df_filtered[df_filtered['lokasi'] == wilayah]
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-value">{len(df_wilayah)}</div>
                                <div class="metric-label">Total Gempa</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-value">{df_wilayah['magnitudo'].max():.2f}</div>
                                <div class="metric-label">Magnitudo Max</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col3:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-value">{df_wilayah['magnitudo'].mean():.2f}</div>
                                <div class="metric-label">Magnitudo Rata-rata</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col4:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-value">{df_wilayah['kedalaman_km'].mean():.1f} km</div>
                                <div class="metric-label">Kedalaman Rata-rata</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        display_df_wilayah = df_wilayah[["waktu_display", "magnitudo", "kategori_magnitudo", "kedalaman_km", "kategori_kedalaman", "latitude", "longitude"]].copy()
                        display_df_wilayah.columns = ["Waktu", "Magnitudo", "Kategori Mag", "Kedalaman (km)", "Kategori Depth", "Latitude", "Longitude"]
                        
                        st.dataframe(display_df_wilayah, use_container_width=True, height=300)
                        
                        csv_wilayah = display_df_wilayah.to_csv(index=False)
                        st.download_button(
                            label=f"📥 Download {wilayah}",
                            data=csv_wilayah,
                            file_name=f"gempa_mag{mag_display}_{wilayah.replace(' ', '_').replace(',', '')}.csv",
                            mime="text/csv",
                            key=f"download_{idx}"
                        )
                
                st.markdown("---")
                
                st.subheader("📋 Semua Data Gempa")
                display_df = df_filtered[["waktu_display", "magnitudo", "kategori_magnitudo", "kedalaman_km", "kategori_kedalaman", "latitude", "longitude", "lokasi"]].copy()
                display_df.columns = ["Waktu", "Magnitudo", "Kategori Mag", "Kedalaman (km)", "Kategori Depth", "Latitude", "Longitude", "Wilayah"]
                
                st.dataframe(display_df, use_container_width=True, height=400)
                
                csv = display_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Semua Data CSV",
                    data=csv,
                    file_name=f"gempa_magnitudo_{mag_display}_semua.csv",
                    mime="text/csv",
                    key="download_all_mag"
                )

# ===========================
# MENU 3: CARI TANGGAL
# ===========================
elif menu == "📅 Cari Tanggal":
    st.markdown('<p class="result-title">Pencarian Berdasarkan Tanggal</p>', unsafe_allow_html=True)
    
    if df.empty:
        st.error("❌ Data tidak tersedia")
    else:
        min_date_picker = df['waktu'].min().date()
        max_date_picker = df['waktu'].max().date()
        st.info(f"📅 **Data tersedia:** {min_date_picker} hingga {max_date_picker}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date_type = st.radio("Tipe Pencarian:", ["Satu Hari", "Range Tanggal"], horizontal=True)
        
        if date_type == "Satu Hari":
            with col2:
                selected_date = st.date_input("Pilih Tanggal:", key="date_single", min_value=min_date_picker, max_value=max_date_picker)
            
            with col3:
                search_button = st.button("🔍 Cari", key="date_button", use_container_width=True)
            
            if search_button:
                date_str = selected_date.strftime("%d-%m-%Y")
                df_filtered = df[df['tanggal'] == date_str]
                
                if len(df_filtered) == 0:
                    st.error(f"❌ Tidak ada gempa pada tanggal {date_str}")
                else:
                    st.success(f"✅ Ditemukan {len(df_filtered)} gempa pada tanggal {date_str}")
                    
                    st.markdown("---")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{len(df_filtered)}</div>
                            <div class="metric-label">Total Gempa</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{df_filtered['magnitudo'].max():.2f}</div>
                            <div class="metric-label">Magnitudo Maksimal</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{df_filtered['lokasi'].nunique()}</div>
                            <div class="metric-label">Jumlah Wilayah</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{df_filtered['kedalaman_km'].mean():.1f} km</div>
                            <div class="metric-label">Kedalaman Rata-rata</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Data breakdown
                    if 'source' in df_filtered.columns:
                        source_breakdown = df_filtered['source'].value_counts()
                        st.subheader("📊 Breakdown Data:")
                        for source, count in source_breakdown.items():
                            st.write(f"- {source}: {count} gempa")
                    
                    st.markdown("---")
                    
                    st.subheader("📋 Data Gempa")
                    display_df = df_filtered[["waktu_display", "magnitudo", "kategori_magnitudo", "kedalaman_km", "kategori_kedalaman", "latitude", "longitude", "lokasi"]].copy()
                    display_df.columns = ["Waktu", "Magnitudo", "Kategori Mag", "Kedalaman (km)", "Kategori Depth", "Latitude", "Longitude", "Lokasi"]
                    
                    st.dataframe(display_df, use_container_width=True, height=400)
                    
                    csv = display_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Semua Data CSV",
                        data=csv,
                        file_name=f"gempa_{date_str}_semua.csv",
                        mime="text/csv",
                        key="download_all_date"
                    )
        
        else:
            col_dari, col_sampai, col_btn = st.columns(3)
            
            with col_dari:
                date_from = st.date_input("Dari Tanggal:", key="date_from", min_value=min_date_picker, max_value=max_date_picker)
            
            with col_sampai:
                date_to = st.date_input("Sampai Tanggal:", key="date_to", min_value=min_date_picker, max_value=max_date_picker)
            
            with col_btn:
                search_button = st.button("🔍 Cari", key="daterange_button", use_container_width=True)
            
            if search_button:
                date_from_ts = pd.Timestamp(date_from, tz='UTC')
                date_to_ts = pd.Timestamp(date_to, tz='UTC') + pd.Timedelta(days=1)
                
                df_filtered = df[(df['waktu'] >= date_from_ts) & (df['waktu'] < date_to_ts)]
                
                if len(df_filtered) == 0:
                    st.error(f"❌ Tidak ada gempa dalam range {date_from.strftime('%d-%m-%Y')} - {date_to.strftime('%d-%m-%Y')}")
                else:
                    st.success(f"✅ Ditemukan {len(df_filtered)} gempa")
                    
                    st.markdown("---")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{len(df_filtered)}</div>
                            <div class="metric-label">Total Gempa</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{df_filtered['magnitudo'].max():.2f}</div>
                            <div class="metric-label">Magnitudo Maksimal</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{df_filtered['lokasi'].nunique()}</div>
                            <div class="metric-label">Jumlah Wilayah</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{df_filtered['kedalaman_km'].mean():.1f} km</div>
                            <div class="metric-label">Kedalaman Rata-rata</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Data breakdown
                    if 'source' in df_filtered.columns:
                        source_breakdown = df_filtered['source'].value_counts()
                        st.subheader("📊 Breakdown Data:")
                        for source, count in source_breakdown.items():
                            st.write(f"- {source}: {count} gempa")
                    
                    st.markdown("---")
                    
                    st.subheader("📋 Data Gempa")
                    display_df = df_filtered[["waktu_display", "magnitudo", "kategori_magnitudo", "kedalaman_km", "kategori_kedalaman", "latitude", "longitude", "lokasi"]].copy()
                    display_df.columns = ["Waktu", "Magnitudo", "Kategori Mag", "Kedalaman (km)", "Kategori Depth", "Latitude", "Longitude", "Lokasi"]
                    
                    st.dataframe(display_df, use_container_width=True, height=400)
                    
                    csv = display_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Semua Data CSV",
                        data=csv,
                        file_name=f"gempa_{date_from.strftime('%d%m%Y')}_{date_to.strftime('%d%m%Y')}_semua.csv",
                        mime="text/csv",
                        key="download_all_range"
                    )

# ===========================
# MENU 4: KOMBINASI FILTER
# ===========================
elif menu == "🔧 Kombinasi Filter":
    st.markdown('<p class="result-title">Pencarian dengan Kombinasi Filter</p>', unsafe_allow_html=True)
    
    if df.empty:
        st.error("❌ Data tidak tersedia")
    else:
        min_date_picker = df['waktu'].min().date()
        max_date_picker = df['waktu'].max().date()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**WILAYAH**")
            wilayah_list = sorted(df['lokasi'].dropna().unique())
            selected_wilayah = st.selectbox("Pilih Wilayah:", wilayah_list, key="kombi_wilayah", label_visibility="collapsed")
        
        with col2:
            st.markdown("**MAGNITUDO**")
            mag_type = st.radio("Tipe:", ["Single", "Range"], horizontal=True, key="kombi_mag_type", label_visibility="collapsed")
            
            if mag_type == "Single":
                mag_val = st.number_input("Nilai:", min_value=1.0, max_value=10.0, value=3.0, step=0.1, key="kombi_mag_single", label_visibility="collapsed")
                mag_min, mag_max = mag_val, mag_val + 0.99
            else:
                col_min, col_max = st.columns(2)
                with col_min:
                    mag_min = st.number_input("Dari:", min_value=1.0, max_value=10.0, value=3.0, step=0.1, key="kombi_mag_min", label_visibility="collapsed")
                with col_max:
                    mag_max = st.number_input("Sampai:", min_value=1.0, max_value=10.0, value=5.0, step=0.1, key="kombi_mag_max", label_visibility="collapsed")
        
        with col3:
            st.markdown("**TANGGAL**")
            date_choice = st.radio("Tipe:", ["Satu Hari", "Range"], horizontal=True, key="kombi_date_type", label_visibility="collapsed")
            
            if date_choice == "Satu Hari":
                selected_date = st.date_input("Pilih:", key="kombi_date_single", label_visibility="collapsed", min_value=min_date_picker, max_value=max_date_picker)
            else:
                col_dari, col_sampai = st.columns(2)
                with col_dari:
                    selected_date_from = st.date_input("Dari:", key="kombi_date_from", label_visibility="collapsed", min_value=min_date_picker, max_value=max_date_picker)
                with col_sampai:
                    selected_date_to = st.date_input("Sampai:", key="kombi_date_to", label_visibility="collapsed", min_value=min_date_picker, max_value=max_date_picker)
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            search_button = st.button("🔍 Cari", key="kombi_button", use_container_width=True)
        
        if search_button:
            df_filtered = df.copy()
            filter_info = []
            
            df_filtered = df_filtered[df_filtered['lokasi'].str.contains(selected_wilayah, case=False, na=False)]
            filter_info.append(f"Wilayah: {selected_wilayah}")
            
            df_filtered = df_filtered[(df_filtered['magnitudo'] >= mag_min) & (df_filtered['magnitudo'] <= mag_max)]
            filter_info.append(f"Magnitudo: {mag_min:.2f}-{mag_max:.2f}")
            
            if date_choice == "Satu Hari":
                date_str = selected_date.strftime("%d-%m-%Y")
                df_filtered = df_filtered[df_filtered['tanggal'] == date_str]
                filter_info.append(f"Tanggal: {date_str}")
            else:
                date_from_ts = pd.Timestamp(selected_date_from, tz='UTC')
                date_to_ts = pd.Timestamp(selected_date_to, tz='UTC') + pd.Timedelta(days=1)
                df_filtered = df_filtered[(df_filtered['waktu'] >= date_from_ts) & (df_filtered['waktu'] < date_to_ts)]
                filter_info.append(f"Tanggal: {selected_date_from.strftime('%d-%m-%Y')} - {selected_date_to.strftime('%d-%m-%Y')}")
            
            if len(df_filtered) == 0:
                st.error("❌ Tidak ada data yang sesuai dengan filter tersebut")
            else:
                st.success(f"✅ Ditemukan {len(df_filtered)} gempa")
                
                st.markdown("---")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{len(df_filtered)}</div>
                        <div class="metric-label">Total Gempa</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{df_filtered['magnitudo'].max():.2f}</div>
                        <div class="metric-label">Magnitudo Maksimal</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{df_filtered['magnitudo'].mean():.2f}</div>
                        <div class="metric-label">Magnitudo Rata-rata</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{df_filtered['kedalaman_km'].mean():.1f} km</div>
                        <div class="metric-label">Kedalaman Rata-rata</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Data breakdown
                if 'source' in df_filtered.columns:
                    source_breakdown = df_filtered['source'].value_counts()
                    st.subheader("📊 Breakdown Data:")
                    for source, count in source_breakdown.items():
                        st.write(f"- {source}: {count} gempa")
                
                st.markdown("---")
                
                st.subheader("📋 Data Gempa")
                display_df = df_filtered[["waktu_display", "magnitudo", "kategori_magnitudo", "kedalaman_km", "kategori_kedalaman", "latitude", "longitude", "lokasi"]].copy()
                display_df.columns = ["Waktu", "Magnitudo", "Kategori Mag", "Kedalaman (km)", "Kategori Depth", "Latitude", "Longitude", "Lokasi"]
                
                st.dataframe(display_df, use_container_width=True, height=400)
                
                csv = display_df.to_csv(index=False)
                filter_str = "_".join([f.split(": ")[1].replace(" ", "").replace(",", "") for f in filter_info])
                st.download_button(
                    label="📥 Download Semua Data CSV",
                    data=csv,
                    file_name=f"gempa_kombinasi_{filter_str}.csv",
                    mime="text/csv",
                    key="download_all_kombi"
                )

# ===========================
# FOOTER
# ===========================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em; margin-top: 2rem;">
    <p>📊 <strong>Sistem Pencarian Data Gempa Indonesia</strong></p>
    <p>Data Seamless: Excel (Aug-Dec 2025) + BMKG Real-time (1 Jan - sekarang)</p>
    <p>Auto-update setiap 1 jam | Sumber: BMKG (Badan Meteorologi, Klimatologi, dan Geofisika)</p>
</div>

""", unsafe_allow_html=True)
