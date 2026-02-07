import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta

# ===========================
# PAGE CONFIG
# ===========================
st.set_page_config(
    page_title="Peta Gempa Indonesia",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Professional BMKG Style
st.markdown("""
<style>
    .header-title {
        text-align: center;
        color: #1e3a5f;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 0.3rem;
    }
    .header-subtitle {
        text-align: center;
        color: #666;
        font-size: 1em;
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
    .status-combined {
        background-color: #cfe2ff;
        color: #084298;
        border: 1px solid #b6d4fe;
    }
    .metric-card {
        background-color: #f0f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1e3a5f;
        text-align: center;
    }
    .metric-value {
        font-size: 1.6em;
        font-weight: bold;
        color: #1e3a5f;
    }
    .metric-label {
        color: #666;
        font-size: 0.9em;
        margin-top: 0.3rem;
    }
    .filter-header {
        color: #1e3a5f;
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 0.8rem;
        text-align: center;
    }
    .button-container {
        display: flex;
        gap: 10px;
        justify-content: center;
        margin-top: 1rem;
    }
    .info-box {
        background-color: #e8f4f8;
        border-left: 4px solid #1e3a5f;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
    .info-title {
        color: #1e3a5f;
        font-weight: bold;
        font-size: 1em;
        margin-bottom: 0.5rem;
    }
    .info-text {
        color: #333;
        font-size: 0.95em;
        line-height: 1.6;
    }
    .stat-grid {
        background-color: #f9f9f9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
    .stat-item {
        padding: 0.8rem;
        margin-bottom: 0.5rem;
        background-color: white;
        border-left: 3px solid #1e3a5f;
        border-radius: 0.3rem;
    }
    .source-badge {
        display: inline-block;
        padding: 0.3rem 0.6rem;
        border-radius: 0.3rem;
        font-size: 0.85em;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    .source-excel {
        background-color: #fff3cd;
        color: #856404;
    }
    .source-bmkg {
        background-color: #d4edda;
        color: #155724;
    }
</style>
""", unsafe_allow_html=True)

# ===========================
# LOAD DATA - EXCEL + BMKG COMBINED (SAME AS APP.PY)
# ===========================

@st.cache_data
def load_data_excel():
    """Load data dari 6 file Excel (Aug-Dec 2025)"""
    try:
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
                        
                        kedalaman_str = gempa.get('Kedalaman', '0').replace(' km', '').replace(' LS', '').replace(',', '.').strip()
                        kedalaman_km = float(kedalaman_str) if kedalaman_str else 0
                        
                        magnitudo = float(gempa.get('Magnitude', 0))
                        lokasi = gempa.get('Wilayah', 'Unknown').strip()
                        
                        lintang_raw = str(gempa.get('Lintang', '0')).replace(' LS', '').replace(' LU', '').replace(',', '.').strip()
                        latitude = float(lintang_raw) if lintang_raw else 0
                        if 'LS' in str(gempa.get('Lintang', '')):
                            latitude = -latitude
                        
                        bujur_raw = str(gempa.get('Bujur', '0')).replace(' BT', '').replace(' BB', '').replace(',', '.').strip()
                        longitude = float(bujur_raw) if bujur_raw else 0
                        if 'BB' in str(gempa.get('Bujur', '')):
                            longitude = -longitude
                        
                        if not (waktu and latitude and longitude and magnitudo):
                            continue
                        
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
    
    df = df.dropna(subset=['latitude', 'longitude', 'magnitudo'])
    
    df["latitude"] = pd.to_numeric(df["latitude"], errors='coerce').round(4)
    df["longitude"] = pd.to_numeric(df["longitude"], errors='coerce').round(4)
    df["magnitudo"] = pd.to_numeric(df["magnitudo"], errors='coerce').round(2)
    df["kedalaman_km"] = pd.to_numeric(df["kedalaman_km"], errors='coerce').round(2)
    df['lokasi'] = df['lokasi'].fillna('Unknown').astype(str).str.strip()
    
    df["waktu"] = pd.to_datetime(df["waktu"], utc=True)
    df["tanggal"] = df["waktu"].dt.strftime("%d-%m-%Y")
    df["bulan"] = df["waktu"].dt.strftime("%B %Y")
    df["waktu_display"] = df["waktu"].dt.strftime("%Y-%m-%d %H:%M")
    
    df = df.sort_values("waktu", ascending=False).reset_index(drop=True)
    
    return df


def load_data():
    """Load data combined: Excel (Aug-Dec 2025) + BMKG (1 Jan - hari ini)"""
    
    df_excel = load_data_excel()
    df_bmkg = load_data_bmkg()
    
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
        data_source = "BMKG Real-time"
        is_combined = False
    else:
        return None, "", False
    
    df = process_data(df)
    
    if df is None or df.empty:
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
st.markdown('<p class="header-title">🗺️ PETA GEMPA INDONESIA</p>', unsafe_allow_html=True)

# Calculate data range
min_date = df['waktu'].min()
max_date = df['waktu'].max()
days_span = (max_date - min_date).days

# Status Badge
if is_combined:
    st.markdown(f'<div class="status-badge status-combined">🔵 {data_source} | Range: {min_date.strftime("%d-%m-%Y")} s/d {max_date.strftime("%d-%m-%Y")} ({days_span} hari)</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="status-badge status-combined">⚠️ {data_source}</div>', unsafe_allow_html=True)

st.markdown('<p class="header-subtitle">Visualisasi Interaktif Lokasi & Aktivitas Gempa Real-time</p>', unsafe_allow_html=True)

# ===========================
# FILTER SECTION - COMPACT
# ===========================
st.markdown('<p class="filter-header">🔍 FILTER PETA</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="medium")

provinces = sorted(df['lokasi'].dropna().unique().tolist())
min_date_picker = df['waktu'].min().date()
max_date_picker = df['waktu'].max().date()

# FILTER 1: PROVINSI
with col1:
    st.markdown("**📍 Provinsi**")
    selected_province = st.selectbox(
        "Pilih provinsi",
        provinces,
        key="province",
        label_visibility="collapsed"
    )

# FILTER 2: MAGNITUDO (Single/Range)
with col2:
    st.markdown("**📊 Magnitudo**")
    mag_type = st.radio(
        "Tipe:",
        ["Single", "Range"],
        horizontal=True,
        key="mag_type",
        label_visibility="collapsed"
    )
    
    if mag_type == "Single":
        mag_val = st.number_input("Nilai:", min_value=1.0, max_value=10.0, value=3.0, step=0.1, key="mag_single", label_visibility="collapsed")
        mag_min, mag_max = mag_val, mag_val + 0.99
    else:
        col_mag_min, col_mag_max = st.columns(2)
        with col_mag_min:
            mag_min = st.number_input("Dari:", min_value=1.0, max_value=10.0, value=3.0, step=0.1, key="mag_min", label_visibility="collapsed")
        with col_mag_max:
            mag_max = st.number_input("Sampai:", min_value=1.0, max_value=10.0, value=5.0, step=0.1, key="mag_max", label_visibility="collapsed")

# FILTER 3: PERIODE (Single/Range)
with col3:
    st.markdown("**📅 Periode**")
    periode_type = st.radio(
        "Tipe:",
        ["Satu Hari", "Range"],
        horizontal=True,
        key="periode_type",
        label_visibility="collapsed"
    )
    
    if periode_type == "Satu Hari":
        selected_date = st.date_input("Pilih tanggal:", key="periode_single", label_visibility="collapsed", min_value=min_date_picker, max_value=max_date_picker)
        selected_periode_display = selected_date.strftime("%d-%m-%Y")
    else:
        col_date_from, col_date_to = st.columns(2)
        with col_date_from:
            date_from = st.date_input("Dari:", key="periode_from", label_visibility="collapsed", min_value=min_date_picker, max_value=max_date_picker)
        with col_date_to:
            date_to = st.date_input("Sampai:", key="periode_to", label_visibility="collapsed", min_value=min_date_picker, max_value=max_date_picker)
        selected_periode_display = f"{date_from.strftime('%d-%m-%Y')} - {date_to.strftime('%d-%m-%Y')}"

# Info tentang data range
st.info(f"📅 **Data tersedia:** {min_date_picker} hingga {max_date_picker}")

# TOMBOL CARI & RESET
st.markdown("")
col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns([1.2, 0.9, 0.8, 0.9, 1.2])

with col_btn2:
    apply_filter = st.button("🔍 CARI", key="cari", use_container_width=True, type="primary")

with col_btn3:
    reset_filter = st.button("🔄 RESET", key="reset", use_container_width=True)

# ===========================
# SESSION STATE
# ===========================
if 'show_map' not in st.session_state:
    st.session_state.show_map = False

if reset_filter:
    st.session_state.show_map = False
    st.rerun()

if apply_filter:
    st.session_state.show_map = True

# ===========================
# FILTER & PREPARE DATA
# ===========================
df_map = df.copy()

if st.session_state.show_map:
    # Filter Provinsi
    df_map = df_map[df_map['lokasi'].str.contains(selected_province, case=False, na=False)]
    
    # Filter Magnitudo
    df_map = df_map[(df_map['magnitudo'] >= mag_min) & (df_map['magnitudo'] <= mag_max)]
    
    # Filter Periode
    if periode_type == "Satu Hari":
        date_str = selected_date.strftime("%d-%m-%Y")
        df_map = df_map[df_map['tanggal'] == date_str]
    else:
        date_from_ts = pd.Timestamp(date_from, tz='UTC')
        date_to_ts = pd.Timestamp(date_to, tz='UTC') + pd.Timedelta(days=1)
        df_map = df_map[(df_map['waktu'] >= date_from_ts) & (df_map['waktu'] < date_to_ts)]

# ===========================
# DISPLAY RESULTS
# ===========================
if not st.session_state.show_map:
    st.info("👈 Pilih filter di atas dan klik **🔍 CARI** untuk menampilkan peta")
else:
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(df_map):,}</div>
            <div class="metric-label">Total Gempa</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        max_mag = df_map['magnitudo'].max() if len(df_map) > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{max_mag:.2f}</div>
            <div class="metric-label">Magnitudo Max</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        mean_mag = df_map['magnitudo'].mean() if len(df_map) > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{mean_mag:.2f}</div>
            <div class="metric-label">Magnitudo Rata-rata</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        mean_depth = df_map['kedalaman_km'].mean() if len(df_map) > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{mean_depth:.1f} km</div>
            <div class="metric-label">Kedalaman Rata-rata</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Data Source breakdown
    if 'source' in df_map.columns:
        source_breakdown = df_map['source'].value_counts()
        col_breakdown1, col_breakdown2 = st.columns(2)
        with col_breakdown1:
            st.subheader("📊 Breakdown Data Source:")
            for source, count in source_breakdown.items():
                if "Excel" in source:
                    st.markdown(f'<span class="source-badge source-excel">{source}</span> {count} gempa', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="source-badge source-bmkg">{source}</span> {count} gempa', unsafe_allow_html=True)
    
    if len(df_map) > 0:
        # Create Map
        map_center = [df_map['latitude'].mean(), df_map['longitude'].mean()]
        m = folium.Map(location=map_center, zoom_start=5, tiles="OpenStreetMap")
        
        def get_color(mag):
            if mag < 3:
                return "green"
            elif mag < 4:
                return "yellow"
            elif mag < 5:
                return "orange"
            else:
                return "red"
        
        # Add Markers
        for idx, row in df_map.iterrows():
            color = get_color(row['magnitudo'])
            popup_text = f"""
            <b>Gempa Bumi</b><br>
            Waktu: {row['waktu_display']}<br>
            Magnitudo: <b>{row['magnitudo']}</b><br>
            Kedalaman: {row['kedalaman_km']} km<br>
            Lokasi: <b>{row['lokasi']}</b>
            """
            
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=5 + (row['magnitudo'] * 0.5),
                popup=folium.Popup(popup_text, max_width=250),
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                weight=2
            ).add_to(m)
        
        # Detailed Legend with Explanations
        legend_html = '''<div style="position: fixed; bottom: 50px; right: 50px; width: 220px;
background-color: white; border:2px solid #1e3a5f; z-index:9999; font-size:12px; 
padding: 12px; border-radius: 5px; box-shadow: 0 0 15px rgba(0,0,0,0.3);">
<p style="margin: 0 0 10px 0; font-weight: bold; color: #1e3a5f; border-bottom: 2px solid #1e3a5f; padding-bottom: 8px;">LEGENDA MAGNITUDO</p>

<p style="margin: 7px 0; padding: 5px; background-color: #f0f0f0; border-radius: 3px;">
<span style="display: inline-block; width: 12px; height: 12px; background-color: green; border-radius: 50%; margin-right: 8px; vertical-align: middle;"></span>
<b>Magnitudo < 3</b><br>
<span style="margin-left: 20px; font-size: 11px; color: #555;">Gempa Kecil - Jarang Terasa</span>
</p>

<p style="margin: 7px 0; padding: 5px; background-color: #f0f0f0; border-radius: 3px;">
<span style="display: inline-block; width: 12px; height: 12px; background-color: gold; border-radius: 50%; margin-right: 8px; vertical-align: middle;"></span>
<b>Magnitudo 3-4</b><br>
<span style="margin-left: 20px; font-size: 11px; color: #555;">Gempa Ringan - Sedikit Terasa</span>
</p>

<p style="margin: 7px 0; padding: 5px; background-color: #f0f0f0; border-radius: 3px;">
<span style="display: inline-block; width: 12px; height: 12px; background-color: orange; border-radius: 50%; margin-right: 8px; vertical-align: middle;"></span>
<b>Magnitudo 4-5</b><br>
<span style="margin-left: 20px; font-size: 11px; color: #555;">Gempa Menengah - Terasa Jelas</span>
</p>

<p style="margin: 7px 0; padding: 5px; background-color: #f0f0f0; border-radius: 3px;">
<span style="display: inline-block; width: 12px; height: 12px; background-color: red; border-radius: 50%; margin-right: 8px; vertical-align: middle;"></span>
<b>Magnitudo > 5</b><br>
<span style="margin-left: 20px; font-size: 11px; color: #555;">Gempa Besar - Sangat Terasa</span>
</p>
</div>'''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Display Map
        col_empty1, col_map, col_empty2 = st.columns([0.05, 0.9, 0.05])
        with col_map:
            st_folium(m, width=1000, height=520)
        
        st.markdown("---")
        
        # Useful Information & Statistics
        st.subheader("📊 Statistik & Informasi Mitigasi")
        
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.markdown("""
            <div class="info-box">
                <div class="info-title">⚠️ Informasi Magnitudo</div>
                <div class="info-text">
                <b>Skala Magnitudo Richter:</b><br>
                • < 3: Tidak terasa atau sangat jarang terasa<br>
                • 3-4: Getaran ringan, benda-benda bergerak<br>
                • 4-5: Getaran kuat, kerusakan pada bangunan<br>
                • 5-6: Kerusakan berat pada bangunan<br>
                • > 6: Kerusakan serius, dapat menghancurkan<br><br>
                <b>Analisis Data Saat Ini:</b><br>
                • Gempa Terkuat: {:.2f} Skala Richter<br>
                • Gempa Terlemah: {:.2f} Skala Richter<br>
                • Total Kejadian: {:,} gempa
                </div>
            </div>
            """.format(df_map['magnitudo'].max(), df_map['magnitudo'].min(), len(df_map)), unsafe_allow_html=True)
        
        with col_info2:
            st.markdown("""
            <div class="info-box">
                <div class="info-title">🏘️ Daerah Paling Rawan</div>
                <div class="info-text">
                <b>Area Dengan Aktivitas Tinggi:</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Top daerah
            top_daerah = df_map['lokasi'].value_counts().head(5)
            for idx, (daerah, count) in enumerate(top_daerah.items(), 1):
                persentase = (count / len(df_map)) * 100
                st.markdown(f"""
                <div class="stat-item">
                <b>{idx}. {daerah}</b><br>
                {count} gempa ({persentase:.1f}%)
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Recommendation
        st.markdown("""
        <div class="info-box">
            <div class="info-title">🛡️ Rekomendasi Mitigasi Bencana</div>
            <div class="info-text">
            <b>Untuk Penduduk Area Gempa:</b><br>
            • Persiapkan rencana evakuasi keluarga<br>
            • Perkuat struktur bangunan tahan gempa<br>
            • Stockpile air bersih dan pangan cadangan<br>
            • Latihan rutin simulasi gempa bumi<br>
            • Hubungi BMKG untuk informasi terkini<br><br>
            <i>Data dari: Badan Meteorologi, Klimatologi, dan Geofisika (BMKG)</i>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.warning("⚠️ Tidak ada data yang sesuai dengan filter yang dipilih")

# ===========================
# FOOTER
# ===========================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em; margin-top: 1rem;">
    <p>🗺️ <strong>Peta Gempa Indonesia - Sistem Informasi GIS</strong></p>
    <p>Seamless Data: Excel (Aug-Dec 2025) + BMKG Real-time (1 Jan - sekarang)</p>
    <p>Sumber: BMKG (Badan Meteorologi, Klimatologi, dan Geofisika) + Historical Excel</p>
</div>

""", unsafe_allow_html=True)
