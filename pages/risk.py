import streamlit as st
import pandas as pd
import numpy as np
import requests
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.graph_objects as go
from datetime import datetime

# ===========================
# PAGE CONFIG
# ===========================
st.set_page_config(
    page_title="Risk Scoring & Hazard Assessment",
    page_icon="⚠️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main { padding-top: 1.5rem; }
    
    .header-title {
        text-align: center;
        color: #1e3a5f;
        font-size: 2.5em;
        font-weight: 700;
        margin-bottom: 0.2rem;
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
        background-color: #cfe2ff;
        color: #084298;
        border: 1px solid #b6d4fe;
    }
    
    .section {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.8rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .section-title {
        color: #1e3a5f;
        font-size: 1.4em;
        font-weight: 700;
        margin-bottom: 0.2rem;
        padding-bottom: 0.8rem;
        border-bottom: 3px solid #1e3a5f;
    }
    
    .section-subtitle {
        color: #999;
        font-size: 0.9em;
        margin-bottom: 1.5rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f0f4f8 0%, #e8f1f8 100%);
        padding: 1.5rem;
        border-radius: 0.8rem;
        border-left: 5px solid #1e3a5f;
        text-align: center;
        box-shadow: 0 2px 8px rgba(30, 58, 95, 0.08);
    }
    
    .metric-value {
        font-size: 1.9em;
        font-weight: 700;
        color: #1e3a5f;
        margin-bottom: 0.4rem;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9em;
        font-weight: 500;
    }
    
    .risk-table-header {
        background: linear-gradient(90deg, #1e3a5f 0%, #2d5a8a 100%);
        color: white;
        padding: 1.2rem;
        font-weight: 700;
        font-size: 1.2em;
        border-radius: 0.5rem 0.5rem 0 0;
        margin-bottom: 0;
    }
    
    .risk-row {
        padding: 1.2rem;
        border-bottom: 1px solid #e0e0e0;
        display: grid;
        grid-template-columns: 0.5fr 2.5fr 1fr 1.2fr;
        gap: 1rem;
        align-items: center;
        transition: background-color 0.2s;
    }
    
    .risk-row:hover {
        background-color: #f9f9f9;
    }
    
    .risk-row:last-child {
        border-bottom: none;
        border-radius: 0 0 0.5rem 0.5rem;
    }
    
    .risk-rank {
        font-weight: 700;
        font-size: 1.1em;
        color: #1e3a5f;
    }
    
    .risk-location {
        font-weight: 600;
        color: #333;
        font-size: 1em;
    }
    
    .risk-score {
        font-weight: 700;
        font-size: 1.3em;
        text-align: center;
        padding: 0.6rem;
        border-radius: 0.5rem;
    }
    
    .score-very-high {
        background-color: #ffe0e0;
        color: #dc3545;
    }
    
    .score-high {
        background-color: #fff3e0;
        color: #fd7e14;
    }
    
    .score-medium {
        background-color: #fff9e6;
        color: #ffc107;
    }
    
    .score-low {
        background-color: #e8f5e9;
        color: #28a745;
    }
    
    .badge {
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: 600;
        font-size: 0.85em;
        text-align: center;
    }
    
    .badge-very-high {
        background-color: #ffe0e0;
        color: #dc3545;
    }
    
    .badge-high {
        background-color: #fff3e0;
        color: #fd7e14;
    }
    
    .badge-medium {
        background-color: #fff9e6;
        color: #ffc107;
    }
    
    .badge-low {
        background-color: #e8f5e9;
        color: #28a745;
    }
    
    .detail-card {
        background: linear-gradient(135deg, #f0f4f8 0%, #e8f1f8 100%);
        border-left: 5px solid #1e3a5f;
        padding: 1.5rem;
        border-radius: 0.8rem;
        margin-bottom: 1.5rem;
    }
    
    .detail-title {
        color: #1e3a5f;
        font-weight: 700;
        font-size: 1.3em;
        margin-bottom: 1.2rem;
        padding-bottom: 0.8rem;
        border-bottom: 2px solid #1e3a5f;
    }
    
    .detail-row {
        display: grid;
        grid-template-columns: 220px 1fr;
        gap: 1rem;
        margin-bottom: 0.8rem;
        padding-bottom: 0.8rem;
        border-bottom: 1px solid rgba(30, 58, 95, 0.1);
    }
    
    .detail-row:last-child {
        border-bottom: none;
    }
    
    .detail-label {
        color: #1e3a5f;
        font-weight: 700;
        font-size: 0.95em;
    }
    
    .detail-value {
        color: #333;
        font-weight: 500;
        font-size: 0.95em;
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
    
    .rec-section {
        background: linear-gradient(135deg, #e8f4f8 0%, #dff0f5 100%);
        border-left: 5px solid #1e3a5f;
        padding: 1.5rem;
        border-radius: 0.8rem;
        margin-top: 1.5rem;
    }
    
    .rec-title {
        color: #1e3a5f;
        font-weight: 700;
        font-size: 1.15em;
        margin-bottom: 1rem;
        padding-bottom: 0.8rem;
        border-bottom: 2px solid #1e3a5f;
    }
    
    .rec-category {
        color: #1e3a5f;
        font-weight: 700;
        font-size: 1em;
        margin-top: 0.8rem;
        margin-bottom: 0.6rem;
    }
    
    .rec-text {
        color: #333;
        font-size: 0.95em;
        line-height: 1.8;
        margin-left: 0;
    }
    
    .rec-item {
        margin-left: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .divider {
        border-top: 2px solid #e0e0e0;
        margin: 2.5rem 0;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        margin-bottom: 0.8rem;
        font-size: 0.95em;
    }
    
    .legend-color {
        width: 30px;
        height: 30px;
        border-radius: 0.3rem;
        margin-right: 1rem;
        border: 1px solid #ccc;
    }
    
    .footer {
        text-align: center;
        color: #999;
        font-size: 0.9em;
        margin-top: 2.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e0e0e0;
    }
    
    @media (max-width: 1200px) {
        .risk-row { grid-template-columns: 1fr; }
        .detail-row { grid-template-columns: 1fr; }
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
    df["bulan"] = df["waktu"].dt.strftime("%b %Y")
    df["tanggal"] = df["waktu"].dt.strftime("%d-%m-%Y")
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
# RISK SCORING ALGORITHM
# ===========================
@st.cache_data
def calculate_risk_scores(df_data):
    """Calculate risk scores for each location with data source breakdown"""
    if df_data.empty:
        return pd.DataFrame()
    
    risk_scores = []
    
    for lokasi in df_data['lokasi'].unique():
        df_lokasi = df_data[df_data['lokasi'] == lokasi]
        
        # Calculate metrics
        total_gempa = len(df_lokasi)
        mag_mean = df_lokasi['magnitudo'].mean()
        mag_max = df_lokasi['magnitudo'].max()
        high_mag_count = len(df_lokasi[df_lokasi['magnitudo'] >= 5])
        kedalaman_mean = df_lokasi['kedalaman_km'].mean()
        kedalaman_min = df_lokasi['kedalaman_km'].min()
        
        # Data source breakdown
        source_breakdown = df_lokasi['source'].value_counts().to_dict()
        excel_count = source_breakdown.get('Excel (Historical)', 0)
        bmkg_count = source_breakdown.get('BMKG Real-time', 0)
        
        # Risk score calculation
        frequency_score = min(total_gempa / 100, 10)
        intensity_score = mag_mean if not pd.isna(mag_mean) else 0
        high_mag_score = min(high_mag_count / 10, 10)
        
        risk_score = (frequency_score * 0.35) + (intensity_score * 0.4) + (high_mag_score * 0.25)
        risk_score = min(risk_score, 10)
        
        # Risk level classification
        if risk_score >= 8:
            risk_level, risk_color = "🔴 VERY HIGH", "very-high"
        elif risk_score >= 6:
            risk_level, risk_color = "🟠 HIGH", "high"
        elif risk_score >= 4:
            risk_level, risk_color = "🟡 MEDIUM", "medium"
        elif risk_score >= 2:
            risk_level, risk_color = "🟢 LOW", "low"
        else:
            risk_level, risk_color = "🔵 VERY LOW", "very-low"
        
        risk_scores.append({
            'lokasi': lokasi,
            'total_gempa': total_gempa,
            'excel_count': excel_count,
            'bmkg_count': bmkg_count,
            'mag_mean': mag_mean,
            'mag_max': mag_max,
            'high_mag_count': high_mag_count,
            'kedalaman_mean': kedalaman_mean,
            'kedalaman_min': kedalaman_min,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_color': risk_color,
            'lat_mean': df_lokasi['latitude'].mean(),
            'lon_mean': df_lokasi['longitude'].mean()
        })
    
    risk_df = pd.DataFrame(risk_scores).sort_values('risk_score', ascending=False).reset_index(drop=True)
    risk_df['rank'] = range(1, len(risk_df) + 1)
    
    return risk_df

risk_df = calculate_risk_scores(df)

# ===========================
# HEADER
# ===========================
st.markdown('<p class="header-title">⚠️ RISK SCORING & HAZARD ASSESSMENT</p>', unsafe_allow_html=True)

# Calculate data range
min_date = df['waktu'].min()
max_date = df['waktu'].max()
days_span = (max_date - min_date).days

# Status Badge
if is_combined:
    st.markdown(f'<div class="status-badge">🔵 {data_source} | Range: {min_date.strftime("%d-%m-%Y")} s/d {max_date.strftime("%d-%m-%Y")} ({days_span} hari)</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="status-badge">⚠️ {data_source}</div>', unsafe_allow_html=True)

st.markdown('<p class="header-subtitle">Sistem Evaluasi Risiko Gempa untuk Pengambilan Keputusan Mitigasi Bencana</p>', unsafe_allow_html=True)

# ===========================
# FILTER & SEARCH
# ===========================
st.markdown('<div class="section">', unsafe_allow_html=True)

col_f1, col_f2, col_f3 = st.columns([2.5, 2.5, 1.2])

with col_f1:
    st.markdown("**📍 Pilih Lokasi**")
    unique_locs = sorted([str(x) for x in risk_df['lokasi'].unique()])
    locations = ["Semua"] + unique_locs
    selected_location = st.selectbox("Lokasi", locations, label_visibility="collapsed", key="risk_loc")

with col_f2:
    st.markdown("**⚖️ Kategori Risiko**")
    risk_levels = ["Semua", "🔴 VERY HIGH", "🟠 HIGH", "🟡 MEDIUM", "🟢 LOW", "🔵 VERY LOW"]
    selected_risk_level = st.selectbox("Risk Level", risk_levels, label_visibility="collapsed", key="risk_level")

with col_f3:
    st.markdown("**🔍**")
    search_button = st.button("🔍 CARI", use_container_width=True, type="primary")

st.markdown('</div>', unsafe_allow_html=True)

# Apply Filters
if search_button:
    risk_filtered = risk_df.copy()
    if selected_location != "Semua":
        risk_filtered = risk_filtered[risk_filtered['lokasi'] == selected_location]
    if selected_risk_level != "Semua":
        risk_filtered = risk_filtered[risk_filtered['risk_level'] == selected_risk_level]
    
    st.session_state.search_performed = True
    st.session_state.filtered_data = risk_filtered
else:
    if 'search_performed' not in st.session_state:
        st.session_state.search_performed = False
        st.session_state.filtered_data = pd.DataFrame()

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ===========================
# SHOW RESULTS ONLY IF SEARCH PERFORMED
# ===========================
if st.session_state.search_performed and not st.session_state.filtered_data.empty:
    risk_filtered = st.session_state.filtered_data
    
    # ===========================
    # STATISTICS
    # ===========================
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">📊 Ringkasan Statistik Lokasi</p>', unsafe_allow_html=True)
    
    col_metrics = st.columns(5)
    
    high_risk_count = len(risk_filtered[risk_filtered['risk_score'] >= 8])
    high_plus_count = len(risk_filtered[risk_filtered['risk_score'] >= 6])
    total_locations = len(risk_filtered)
    avg_risk = risk_filtered['risk_score'].mean()
    highest_risk_loc = risk_filtered.iloc[0]['lokasi']
    highest_risk_score = risk_filtered.iloc[0]['risk_score']
    
    # Determine color untuk highest risk
    if highest_risk_score >= 8:
        score_color = "#dc3545"
    elif highest_risk_score >= 6:
        score_color = "#fd7e14"
    elif highest_risk_score >= 4:
        score_color = "#ffc107"
    else:
        score_color = "#28a745"
    
    metrics_data = [
        ("Total Lokasi", f"{total_locations}", "📍"),
        ("Avg Risk Score", f"{avg_risk:.2f}/10", "📊"),
        ("Very High Risk", f"{high_risk_count}", "🔴"),
        ("High Risk+", f"{high_plus_count}", "🟠"),
        ("Highest Risk", f"{highest_risk_loc} ({highest_risk_score:.2f})", "⚠️", score_color)
    ]
    
    for idx, item in enumerate(metrics_data):
        with col_metrics[idx]:
            if len(item) == 4:
                label, value, emoji, color = item
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 1.8em; margin-bottom: 0.3rem;">{emoji}</div>
                    <div class="metric-value" style="color: {color};">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                label, value, emoji = item
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 1.8em; margin-bottom: 0.3rem;">{emoji}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # ===========================
    # LEGEND
    # ===========================
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">📋 Risk Score Legend</p>', unsafe_allow_html=True)
    
    col_legend = st.columns(5)
    legend_items = [
        ("🔴 VERY HIGH", "8.0 - 10.0", "#dc3545"),
        ("🟠 HIGH", "6.0 - 7.9", "#fd7e14"),
        ("🟡 MEDIUM", "4.0 - 5.9", "#ffc107"),
        ("🟢 LOW", "2.0 - 3.9", "#28a745"),
        ("🔵 VERY LOW", "0.0 - 1.9", "#0dcaf0")
    ]
    
    for idx, (label, range_val, color) in enumerate(legend_items):
        with col_legend[idx]:
            st.markdown(f"""
            <div class="legend-item">
                <div class="legend-color" style="background-color: {color};"></div>
                <div style="font-weight: 600; font-size: 0.9em;">{label}<br><span style="font-size: 0.8em; color: #999;">{range_val}</span></div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # ===========================
    # RISK ASSESSMENT TABLE
    # ===========================
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">🏆 Risk Assessment Table</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Daerah terurut berdasarkan tingkat risiko gempa bumi (Data kombinasi Excel + BMKG)</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="risk-table-header">⚠️ RISK ASSESSMENT - DATA DETAIL (Excel + BMKG Combined)</div>', unsafe_allow_html=True)
    
    for idx, row in risk_filtered.iterrows():
        score_class = f"score-{row['risk_color']}"
        badge_class = f"badge badge-{row['risk_color']}"
        
        st.markdown(f"""
        <div class="risk-row">
            <div class="risk-rank">#{int(row['rank'])}</div>
            <div class="risk-location">{row['lokasi']}</div>
            <div class="risk-score {score_class}">{row['risk_score']:.2f}/10</div>
            <div class="{badge_class}">{row['risk_level']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # DETAIL EXPANDER
        with st.expander(f"📌 Detail Lengkap - {row['lokasi']}", expanded=False):
            st.markdown('<div class="detail-card">', unsafe_allow_html=True)
            st.markdown(f'<p class="detail-title">{row["lokasi"]} - Risk Score {row["risk_score"]:.2f}/10 {row["risk_level"]}</p>', unsafe_allow_html=True)
            
            col_d1, col_d2 = st.columns(2)
            
            with col_d1:
                st.markdown(f"""
                <div class="detail-row">
                    <div class="detail-label">🔢 Total Gempa:</div>
                    <div class="detail-value"><b>{int(row['total_gempa'])}</b> kejadian</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">📊 Data Source:</div>
                    <div class="detail-value">
                        <span class="source-badge source-excel">Excel: {int(row['excel_count'])}</span>
                        <span class="source-badge source-bmkg">BMKG: {int(row['bmkg_count'])}</span>
                    </div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">📈 Magnitudo Rata-rata:</div>
                    <div class="detail-value"><b>{row['mag_mean']:.2f}</b> Skala Richter</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">⚡ Magnitudo Maksimal:</div>
                    <div class="detail-value"><b>{row['mag_max']:.2f}</b> Skala Richter</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_d2:
                st.markdown(f"""
                <div class="detail-row">
                    <div class="detail-label">🔴 Gempa > Mag 5:</div>
                    <div class="detail-value"><b>{int(row['high_mag_count'])}</b> kejadian (Sangat Berbahaya)</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">📍 Kedalaman Rata-rata:</div>
                    <div class="detail-value"><b>{row['kedalaman_mean']:.1f}</b> km</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">🎯 Kedalaman Minimum:</div>
                    <div class="detail-value"><b>{row['kedalaman_min']:.1f}</b> km (Superfisial)</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # DETAILED RECOMMENDATIONS
            st.markdown('<div class="rec-section">', unsafe_allow_html=True)
            st.markdown('<p class="rec-title">🎯 Rekomendasi Mitigasi Bencana Gempa</p>', unsafe_allow_html=True)
            
            if row['risk_score'] >= 8:
                st.markdown("""
                <p class="rec-category">🔴 PRIORITAS TERTINGGI - Wilayah Dengan Risiko Sangat Tinggi</p>
                <p class="rec-text">Lokasi ini menunjukkan aktivitas seismik yang sangat intensif dengan frekuensi tinggi dan potensi gempa besar yang signifikan. Tindakan mitigasi dan preparedness harus dilakukan segera dan berkelanjutan:</p>
                <div class="rec-item">• <b>Sistem Peringatan Dini (Early Warning System):</b> Implementasi sistem monitoring gempa real-time yang terintegrasi dengan sensor lokal. Sistem harus mampu mendeteksi gempa dalam hitungan detik dan mengirimkan peringatan ke masyarakat melalui berbagai channel (SMS, sirene, aplikasi mobile).</div>
                <div class="rec-item">• <b>Infrastruktur Tahan Gempa:</b> Bangun dan perkuat shelter tahan gempa serta ruang evakuasi aman di setiap desa/kelurahan. Standar konstruksi harus mengikuti SNI 1726 dan memiliki kapasitas mencukupi untuk seluruh populasi.</div>
                <div class="rec-item">• <b>Program Edukasi Keselamatan Gempa:</b> Jalankan program edukasi intensif di sekolah, kantor, dan komunitas. Materi mencakup cara berlindung saat gempa, rencana evakuasi keluarga, dan pengenalan zona aman.</div>
                <div class="rec-item">• <b>Penguatan Infrastruktur Kritis:</b> Perkuat bangunan pemerintah, rumah sakit, kantor polisi, dan fasilitas publik lainnya agar tetap berfungsi pasca gempa untuk koordinasi tanggap darurat.</div>
                <div class="rec-item">• <b>Simulasi Evakuasi Rutin:</b> Lakukan simulasi gempa dan evakuasi setiap bulan di sekolah, kantor, dan komunitas untuk memastikan semua orang paham prosedur dan dapat melakukannya dalam keadaan darurat.</div>
                <div class="rec-item">• <b>Tim Respons Darurat 24/7:</b> Bentuk dan latih tim respons darurat yang siaga sepanjang waktu dengan peralatan dan logistik lengkap untuk respons cepat pasca gempa.</div>
                <div class="rec-item">• <b>Koordinasi dengan BMKG & TNI:</b> Jalin koordinasi kuat dengan Badan Meteorologi, Klimatologi, dan Geofisika (BMKG) dan TNI untuk monitoring, respons, dan rehabilitasi.</div>
                """, unsafe_allow_html=True)
            
            elif row['risk_score'] >= 6:
                st.markdown("""
                <p class="rec-category">🟠 PRIORITAS TINGGI - Wilayah Dengan Risiko Tinggi</p>
                <p class="rec-text">Lokasi ini memiliki aktivitas seismik yang signifikan dengan potensi kerusakan sedang hingga berat. Tindakan preventif dan preparedness harus diperkuat:</p>
                <div class="rec-item">• <b>Perbaikan Sistem Peringatan Gempa:</b> Tingkatkan efektivitas sistem peringatan gempa yang ada dengan memperbanyak sensor dan meningkatkan aksesibilitas informasi peringatan.</div>
                <div class="rec-item">• <b>Rehabilitasi Bangunan Tidak Tahan Gempa:</b> Identifikasi dan rehabilitasi bangunan lama yang tidak memenuhi standar tahan gempa, terutama sekolah dan rumah sakit.</div>
                <div class="rec-item">• <b>Program Edukasi untuk Institusi:</b> Lakukan program edukasi keselamatan gempa khusus untuk sekolah, kantor, dan institusi publik dengan frekuensi minimal 1 tahun sekali.</div>
                <div class="rec-item">• <b>Pelatihan Respons Darurat:</b> Selenggarakan pelatihan respons darurat untuk staff BPBD, polisi, petugas kesehatan, dan relawan minimal 2 kali per tahun.</div>
                <div class="rec-item">• <b>Pemetaan Risiko Detail:</b> Buat pemetaan risiko detail per blok/kelurahan untuk menentukan zona evakuasi dan lokasi shelter yang optimal.</div>
                <div class="rec-item">• <b>Monitoring Berkelanjutan:</b> Jalin kerja sama dengan BMKG untuk monitoring aktivitas seismik berkelanjutan dan update informasi risiko secara berkala.</div>
                """, unsafe_allow_html=True)
            
            elif row['risk_score'] >= 4:
                st.markdown("""
                <p class="rec-category">🟡 PRIORITAS SEDANG - Wilayah Dengan Risiko Sedang</p>
                <p class="rec-text">Lokasi ini memiliki aktivitas seismik dengan potensi kerusakan ringan hingga sedang. Tindakan preparedness dasar perlu diterapkan:</p>
                <div class="rec-item">• <b>Penguatan Kode Bangunan:</b> Pastikan pembangunan baru mengikuti standar tahan gempa SNI 1726. Lakukan edukasi kepada kontraktor dan pemilik bangunan tentang pentingnya standar konstruksi.</div>
                <div class="rec-item">• <b>Program Edukasi Dasar:</b> Jalankan program edukasi keselamatan gempa dasar di sekolah dan komunitas minimal 1 tahun sekali.</div>
                <div class="rec-item">• <b>Pelatihan Respons Tahunan:</b> Lakukan pelatihan respons darurat untuk pemerintah lokal, polisi, dan relawan minimal 1 tahun sekali.</div>
                <div class="rec-item">• <b>Identifikasi Zona Evakuasi:</b> Tentukan zona aman dan zona evakuasi untuk diketahui masyarakat luas melalui peta dan tanda-tanda di lapangan.</div>
                <div class="rec-item">• <b>Kesiapan Logistik Dasar:</b> Siapkan logistik darurat dasar (tenda, obat, makanan) untuk respons cepat pasca gempa.</div>
                """, unsafe_allow_html=True)
            
            else:
                st.markdown("""
                <p class="rec-category">🟢 PRIORITAS MONITOR - Wilayah Dengan Risiko Rendah</p>
                <p class="rec-text">Lokasi ini memiliki aktivitas seismik rendah namun tetap perlu monitoring dan preparedness dasar:</p>
                <div class="rec-item">• <b>Monitoring Berkelanjutan:</b> Tetap melakukan monitoring aktivitas seismik melalui data BMKG untuk early detection jika ada peningkatan aktivitas.</div>
                <div class="rec-item">• <b>Program Edukasi Awareness:</b> Jalankan program edukasi awareness umum tentang gempa bumi dan keselamatan dasar, minimal 1 tahun sekali.</div>
                <div class="rec-item">• <b>Persiapan Keselamatan Umum:</b> Siapkan kit keselamatan dasar (first aid, lampu darurat, air minum) di rumah dan kantor.</div>
                <div class="rec-item">• <b>Update Rencana Darurat:</b> Tinjau dan update rencana darurat sesuai dengan data seismik terbaru dari BMKG.</div>
                <div class="rec-item">• <b>Koordinasi Lokal:</b> Jalin koordinasi dengan pemerintah lokal dan BMKG untuk mendapatkan update informasi gempa terbaru.</div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # ===========================
    # HEATMAP
    # ===========================
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">🗺️ Heatmap Konsentrasi Risiko Gempa</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Visualisasi spasial distribusi dan intensitas risiko gempa di lokasi yang dipilih</p>', unsafe_allow_html=True)
    
    if not df.empty:
        m = folium.Map(
            location=[df['latitude'].mean(), df['longitude'].mean()],
            zoom_start=5,
            tiles="OpenStreetMap"
        )
        
        df_for_heatmap = df[df['lokasi'].isin(risk_filtered['lokasi'].tolist())]
        heat_data = [[row['latitude'], row['longitude'], row['magnitudo']/10] 
                     for _, row in df_for_heatmap.iterrows()]
        
        HeatMap(heat_data, min_opacity=0.3, radius=35, blur=20, max_zoom=1).add_to(m)
        
        col_empty1, col_map, col_empty2 = st.columns([0.05, 0.9, 0.05])
        with col_map:
            st_folium(m, width=1000, height=520)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # ===========================
    # DISTRIBUTION CHARTS
    # ===========================
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">📊 Distribusi Risk Score</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Analisis sebaran daerah berdasarkan kategori risiko (Data Combined: Excel + BMKG)</p>', unsafe_allow_html=True)
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown('**📊 Bar Chart - Jumlah Daerah**')
        risk_dist = risk_filtered['risk_level'].value_counts()
        colors_map = {
            '🔴 VERY HIGH': '#dc3545',
            '🟠 HIGH': '#fd7e14',
            '🟡 MEDIUM': '#ffc107',
            '🟢 LOW': '#28a745',
            '🔵 VERY LOW': '#0dcaf0'
        }
        
        fig_bar = go.Figure(data=[go.Bar(
            x=risk_dist.index,
            y=risk_dist.values,
            marker=dict(color=[colors_map.get(x, '#1e3a5f') for x in risk_dist.index]),
            text=risk_dist.values,
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Jumlah Daerah: %{y}<extra></extra>'
        )])
        fig_bar.update_layout(height=360, showlegend=False, template='plotly_white',
            font=dict(size=11), xaxis=dict(title='Kategori Risiko', showgrid=False),
            yaxis=dict(title='Jumlah Daerah', showgrid=True, gridcolor='#f0f0f0'),
            margin=dict(l=50, r=30, t=30, b=60))
        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
    
    with col_chart2:
        st.markdown('**🥧 Pie Chart - Persentase**')
        fig_pie = go.Figure(data=[go.Pie(
            labels=risk_dist.index,
            values=risk_dist.values,
            marker=dict(colors=[colors_map.get(x, '#1e3a5f') for x in risk_dist.index]),
            textposition='inside',
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Jumlah: %{value}<br>Persentase: %{percent}<extra></extra>'
        )])
        fig_pie.update_layout(height=360, showlegend=True, template='plotly_white',
            font=dict(size=11), margin=dict(l=30, r=30, t=30, b=30))
        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # ===========================
    # EXPORT
    # ===========================
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">📥 Download Data & Report</p>', unsafe_allow_html=True)
    
    col_export1, col_export2 = st.columns(2)
    
    with col_export1:
        csv_risk = risk_filtered[['rank', 'lokasi', 'risk_score', 'risk_level', 'total_gempa', 
                                   'excel_count', 'bmkg_count', 'mag_mean', 'high_mag_count', 'kedalaman_mean']].to_csv(index=False)
        st.download_button("📊 Download Risk Scoring CSV", csv_risk, f"risk_scoring_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv", use_container_width=True)
    
    with col_export2:
        csv_full = df[['waktu_display', 'magnitudo', 'kedalaman_km', 'latitude', 'longitude', 'lokasi', 'source']].to_csv(index=False)
        st.download_button("📋 Download Full Data CSV", csv_full, f"full_gempa_data_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

else:
    if st.session_state.search_performed:
        st.warning("⚠️ Tidak ada data yang sesuai dengan filter yang dipilih. Silakan coba filter lain.")
    else:
        st.info("👈 Pilih lokasi dan kategori risiko, lalu klik tombol **🔍 CARI** untuk menampilkan hasil analisis.")

# ===========================
# FOOTER
# ===========================
st.markdown("""
<div class="footer">
    <p>⚠️ <strong>Risk Scoring & Hazard Assessment System</strong></p>
    <p>Sistem Evaluasi Risiko Gempa untuk Pengambilan Keputusan Mitigasi Bencana</p>
    <p>Seamless Data: Excel (Aug-Dec 2025) + BMKG Real-time (1 Jan - sekarang)</p>
    <p>Sumber Data: BMKG (Badan Meteorologi, Klimatologi, dan Geofisika) + Historical Excel</p>
</div>

""", unsafe_allow_html=True)
