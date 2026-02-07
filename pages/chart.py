import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ===========================
# PAGE CONFIG
# ===========================
st.set_page_config(
    page_title="Analisis & Insight Gempa",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .main {
        padding-top: 1.5rem;
    }
    
    .header-title {
        text-align: center;
        color: #1e3a5f;
        font-size: 2.5em;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    
    .header-subtitle {
        text-align: center;
        color: #666;
        font-size: 1.05em;
        margin-bottom: 1.5rem;
        font-weight: 400;
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
    
    .metric-container {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
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
        line-height: 1.4;
    }
    
    .chart-section {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.8rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .chart-title {
        color: #1e3a5f;
        font-size: 1.4em;
        font-weight: 700;
        margin-bottom: 0.2rem;
        padding-bottom: 0.8rem;
        border-bottom: 3px solid #1e3a5f;
    }
    
    .chart-subtitle {
        color: #999;
        font-size: 0.9em;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }
    
    .insight-box {
        background: linear-gradient(135deg, #e8f4f8 0%, #dff0f5 100%);
        border-left: 5px solid #1e3a5f;
        padding: 1.2rem;
        border-radius: 0.6rem;
        margin-top: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .insight-title {
        color: #1e3a5f;
        font-weight: 700;
        font-size: 1em;
        margin-bottom: 0.6rem;
    }
    
    .insight-text {
        color: #333;
        font-size: 0.95em;
        line-height: 1.7;
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
    
    .divider {
        border-top: 2px solid #e0e0e0;
        margin: 2.5rem 0;
    }
    
    .decision-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .decision-box {
        background: linear-gradient(135deg, #f0f4f8 0%, #e8f1f8 100%);
        border-left: 5px solid #1e3a5f;
        padding: 1.5rem;
        border-radius: 0.8rem;
        box-shadow: 0 2px 8px rgba(30, 58, 95, 0.08);
    }
    
    .decision-title {
        color: #1e3a5f;
        font-weight: 700;
        font-size: 1.1em;
        margin-bottom: 1rem;
    }
    
    .decision-text {
        color: #333;
        font-size: 0.95em;
        line-height: 1.8;
    }
    
    .footer-text {
        text-align: center;
        color: #999;
        font-size: 0.9em;
        margin-top: 2.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e0e0e0;
    }
    
    @media (max-width: 1200px) {
        .metric-container {
            grid-template-columns: repeat(3, 1fr);
        }
        .decision-grid {
            grid-template-columns: 1fr;
        }
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
    df["bulan_sort"] = df["waktu"].dt.strftime("%Y-%m")
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
# HEADER
# ===========================
st.markdown('<p class="header-title">📊 ANALISIS & INSIGHT GEMPA INDONESIA</p>', unsafe_allow_html=True)

# Calculate data range
min_date = df['waktu'].min()
max_date = df['waktu'].max()
days_span = (max_date - min_date).days

# Status Badge
if is_combined:
    st.markdown(f'<div class="status-badge">🔵 {data_source} | Range: {min_date.strftime("%d-%m-%Y")} s/d {max_date.strftime("%d-%m-%Y")} ({days_span} hari)</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="status-badge">⚠️ {data_source}</div>', unsafe_allow_html=True)

st.markdown('<p class="header-subtitle">Dashboard Data-Driven untuk Pengambilan Keputusan (Combined: Excel + Real-time BMKG)</p>', unsafe_allow_html=True)

# ===========================
# FILTER (SIMPLE - NO SESSION STATE ISSUES)
# ===========================
col_f1, col_f2, col_f3 = st.columns([2.5, 2.5, 1.2])

with col_f1:
    st.markdown("**📍 Provinsi/Wilayah**")
    provinces = ["Semua"] + sorted(df['lokasi'].dropna().unique().tolist())
    selected_province = st.selectbox("Pilih", provinces, label_visibility="collapsed", key="prov_chart")

with col_f2:
    st.markdown("**📅 Periode**")
    periods = ["Semua"] + sorted(set(df['bulan'].tolist()))
    selected_period = st.selectbox("Pilih", periods, label_visibility="collapsed", key="period_chart")

with col_f3:
    st.markdown("**⚙️**")
    col_reset, col_empty = st.columns([1, 1])
    with col_reset:
        if st.button("🔄 Reset", use_container_width=True):
            selected_province = "Semua"
            selected_period = "Semua"

# Apply Filters
df_filtered = df.copy()

if selected_province != "Semua":
    df_filtered = df_filtered[df_filtered['lokasi'].str.contains(selected_province, case=False, na=False)]

if selected_period != "Semua":
    df_filtered = df_filtered[df_filtered['bulan'] == selected_period]

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ===========================
# STATISTICS
# ===========================
st.markdown('<p class="chart-title">📊 Ringkasan Statistik</p>', unsafe_allow_html=True)

col_metrics = st.columns(5)

metrics_data = [
    ("Total Gempa", f"{len(df_filtered):,}", "🔢"),
    ("Magnitudo Max", f"{df_filtered['magnitudo'].max():.2f}" if len(df_filtered) > 0 else "0", "⚡"),
    ("Magnitudo Avg", f"{df_filtered['magnitudo'].mean():.2f}" if len(df_filtered) > 0 else "0", "📈"),
    ("Kedalaman Avg", f"{df_filtered['kedalaman_km'].mean():.1f} km" if len(df_filtered) > 0 else "0 km", "📍"),
    ("Gempa > Mag 5", f"{len(df_filtered[df_filtered['magnitudo'] >= 5])}" if len(df_filtered) > 0 else "0", "⚠️")
]

for idx, (label, value, emoji) in enumerate(metrics_data):
    with col_metrics[idx]:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.8em; margin-bottom: 0.3rem;">{emoji}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

# Data source info
if is_combined and len(df_filtered) > 0:
    source_counts = df_filtered['source'].value_counts()
    st.info(f"📊 **Data Source:** {', '.join([f'{k}: {v} gempa' for k, v in source_counts.items()])}")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ===========================
# CHART 1: TIMELINE
# ===========================
st.markdown('<div class="chart-section">', unsafe_allow_html=True)
st.markdown('<p class="chart-title">📈 Timeline Aktivitas Gempa Bulanan</p>', unsafe_allow_html=True)
st.markdown('<p class="chart-subtitle">Tren jumlah kejadian gempa dari waktu ke waktu (Combined: Excel + BMKG)</p>', unsafe_allow_html=True)

timeline_data = df_filtered.groupby('bulan').size().reset_index(name='jumlah')
timeline_data['bulan_sort'] = df_filtered.groupby('bulan')['bulan_sort'].first()
timeline_data = timeline_data.sort_values('bulan_sort')

if len(timeline_data) > 0:
    fig_timeline = go.Figure()
    fig_timeline.add_trace(go.Scatter(
        x=timeline_data['bulan'], y=timeline_data['jumlah'],
        mode='lines+markers', line=dict(color='#1e3a5f', width=4),
        marker=dict(size=12, color='#1e3a5f'),
        fill='tozeroy', fillcolor='rgba(30, 58, 95, 0.15)',
        hovertemplate='<b>%{x}</b><br>Jumlah: %{y:,.0f}<extra></extra>'
    ))
    fig_timeline.update_layout(
        height=380, showlegend=False, template='plotly_white',
        font=dict(size=12), xaxis=dict(title='Periode', showgrid=True, gridcolor='#f0f0f0'),
        yaxis=dict(title='Jumlah Gempa', showgrid=True, gridcolor='#f0f0f0'),
        margin=dict(l=60, r=40, t=40, b=60)
    )
    st.plotly_chart(fig_timeline, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("""
    <div class="insight-box">
        <div class="insight-title">💡 Insight</div>
        <div class="insight-text">
        Grafik menunjukkan tren aktivitas seismik bulanan dari data Excel (Aug-Dec 2025) dan real-time BMKG (1 Jan - sekarang). 
        Bulan dengan aktivitas tinggi memerlukan persiapan khusus untuk mitigasi dan edukasi masyarakat tentang keselamatan gempa.
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("⚠️ Tidak ada data untuk filter yang dipilih")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ===========================
# CHART 2: DISTRIBUSI MAGNITUDO
# ===========================
st.markdown('<div class="chart-section">', unsafe_allow_html=True)
st.markdown('<p class="chart-title">📊 Distribusi Magnitudo Gempa</p>', unsafe_allow_html=True)
st.markdown('<p class="chart-subtitle">Sebaran gempa berdasarkan kategori magnitudo (Data Combined)</p>', unsafe_allow_html=True)

def categorize_magnitude(mag):
    if mag < 3: return "1-2 (Kecil)"
    elif mag < 4: return "3-4 (Ringan)"
    elif mag < 5: return "4-5 (Menengah)"
    else: return "5+ (Besar)"

df_filtered['mag_kategori'] = df_filtered['magnitudo'].apply(categorize_magnitude)
mag_dist = df_filtered['mag_kategori'].value_counts().reindex(["1-2 (Kecil)", "3-4 (Ringan)", "4-5 (Menengah)", "5+ (Besar)"], fill_value=0)

col_mag1, col_mag2 = st.columns(2)

with col_mag1:
    st.markdown('**Bar Chart - Jumlah Gempa**')
    colors = ['#28a745', '#ffc107', '#fd7e14', '#dc3545']
    fig_bar = go.Figure(data=[go.Bar(
        x=mag_dist.index, y=mag_dist.values, marker=dict(color=colors),
        text=mag_dist.values, textposition='auto',
        hovertemplate='<b>%{x}</b><br>Jumlah: %{y:,.0f}<extra></extra>'
    )])
    fig_bar.update_layout(
        height=360, showlegend=False, template='plotly_white', font=dict(size=11),
        xaxis=dict(title='Kategori Magnitudo', showgrid=False),
        yaxis=dict(title='Jumlah Gempa', showgrid=True, gridcolor='#f0f0f0'),
        margin=dict(l=50, r=30, t=30, b=60)
    )
    st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

with col_mag2:
    st.markdown('**Pie Chart - Persentase**')
    fig_pie = go.Figure(data=[go.Pie(
        labels=mag_dist.index, values=mag_dist.values, marker=dict(colors=colors),
        textposition='inside', textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Jumlah: %{value}<br>Persentase: %{percent}<extra></extra>'
    )])
    fig_pie.update_layout(
        height=360, showlegend=True, template='plotly_white', font=dict(size=11),
        margin=dict(l=30, r=30, t=30, b=30)
    )
    st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

st.markdown("""
<div class="insight-box">
    <div class="insight-title">💡 Insight</div>
    <div class="insight-text">
    Mayoritas gempa adalah kategori ringan (3-4). Fokus mitigasi pada area dengan gempa besar (>5) yang 
    meskipun jarang tetapi memiliki dampak signifikan terhadap infrastruktur dan keselamatan. Data ini 
    menggabungkan historical (Excel) dan real-time (BMKG) untuk gambaran komprehensif.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ===========================
# CHART 3: TOP 10 DAERAH
# ===========================
st.markdown('<div class="chart-section">', unsafe_allow_html=True)
st.markdown('<p class="chart-title">🗺️ Top 10 Daerah Paling Rawan Gempa</p>', unsafe_allow_html=True)
st.markdown('<p class="chart-subtitle">Wilayah dengan aktivitas seismik tertinggi (Excel + BMKG Combined)</p>', unsafe_allow_html=True)

top_daerah = df_filtered['lokasi'].value_counts().head(10)

fig_top = go.Figure(data=[go.Bar(
    x=top_daerah.values, y=top_daerah.index, orientation='h',
    marker=dict(color='#1e3a5f'), text=top_daerah.values, textposition='auto',
    hovertemplate='<b>%{y}</b><br>Jumlah: %{x:,.0f}<extra></extra>'
)])

fig_top.update_layout(
    height=420, showlegend=False, template='plotly_white', font=dict(size=11),
    xaxis=dict(title='Jumlah Gempa', showgrid=True, gridcolor='#f0f0f0'),
    yaxis=dict(title='Daerah', categoryorder='total ascending'),
    margin=dict(l=180, r=40, t=30, b=50)
)

st.plotly_chart(fig_top, use_container_width=True, config={'displayModeBar': False})

st.markdown("""
<div class="insight-box">
    <div class="insight-title">💡 Insight</div>
    <div class="insight-text">
    Daerah-daerah ini memerlukan perhatian khusus untuk sistem early warning, pembangunan infrastruktur 
    tahan gempa, dan program disaster preparedness yang berkelanjutan dan terukur.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ===========================
# CHART 4: SCATTER PLOT
# ===========================
st.markdown('<div class="chart-section">', unsafe_allow_html=True)
st.markdown('<p class="chart-title">📐 Relasi Kedalaman vs Magnitudo</p>', unsafe_allow_html=True)
st.markdown('<p class="chart-subtitle">Analisis hubungan antara kedalaman dan kekuatan gempa</p>', unsafe_allow_html=True)

fig_scatter = px.scatter(
    df_filtered, x='kedalaman_km', y='magnitudo',
    color='magnitudo', size='magnitudo',
    hover_data={'lokasi': True, 'tanggal': True, 'kedalaman_km': ':.1f', 'magnitudo': ':.2f'},
    color_continuous_scale='Viridis', labels={'kedalaman_km': 'Kedalaman (km)', 'magnitudo': 'Magnitudo'},
    template='plotly_white'
)

fig_scatter.update_layout(
    height=420, font=dict(size=11),
    xaxis=dict(title='Kedalaman (km)', showgrid=True, gridcolor='#f0f0f0'),
    yaxis=dict(title='Magnitudo', showgrid=True, gridcolor='#f0f0f0'),
    hovermode='closest', coloraxis_colorbar=dict(title='Magnitudo'),
    margin=dict(l=60, r=80, t=30, b=60)
)

st.plotly_chart(fig_scatter, use_container_width=True, config={'displayModeBar': False})

st.markdown("""
<div class="insight-box">
    <div class="insight-title">💡 Insight</div>
    <div class="insight-text">
    Gempa superfisial (< 70 km) umumnya lebih terasa di permukaan dengan dampak lokal lebih besar. 
    Perhatian khusus diperlukan untuk preparedness dan mitigasi di area dengan gempa superfisial.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ===========================
# CHART 5: JAM GEMPA - OVERVIEW
# ===========================
st.markdown('<div class="chart-section">', unsafe_allow_html=True)
st.markdown('<p class="chart-title">🕐 Distribusi Waktu Gempa Per Daerah</p>', unsafe_allow_html=True)
st.markdown('<p class="chart-subtitle">Jam puncak terjadinya gempa di setiap daerah (Data historis + real-time)</p>', unsafe_allow_html=True)

if len(df_filtered) > 0:
    # Calculate hour for each earthquake
    df_filtered_copy = df_filtered.copy()
    df_filtered_copy['jam'] = pd.to_datetime(df_filtered_copy['waktu']).dt.hour
    
    # Get top 15 locations for readability
    top_15_daerah = df_filtered_copy['lokasi'].value_counts().head(15).index
    df_top_15 = df_filtered_copy[df_filtered_copy['lokasi'].isin(top_15_daerah)]
    
    # Find most common hour for each location
    jam_per_daerah = df_top_15.groupby('lokasi')['jam'].agg(lambda x: x.value_counts().idxmax()).reset_index()
    jam_per_daerah.columns = ['lokasi', 'jam_terbanyak']
    jam_per_daerah = jam_per_daerah.sort_values('jam_terbanyak')
    
    # Create bar chart
    fig_jam = go.Figure(data=[go.Bar(
        y=jam_per_daerah['lokasi'],
        x=jam_per_daerah['jam_terbanyak'],
        orientation='h',
        marker=dict(
            color=jam_per_daerah['jam_terbanyak'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Jam (0-23)")
        ),
        text=[f"{int(jam):02d}:00" for jam in jam_per_daerah['jam_terbanyak']],
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>Jam Puncak: %{text}<extra></extra>'
    )])
    
    fig_jam.update_layout(
        height=420,
        showlegend=False,
        font=dict(size=11),
        xaxis=dict(title='Jam (0-23)', showgrid=True, gridwidth=1, gridcolor='#f0f0f0', range=[0, 24]),
        yaxis=dict(title='Daerah'),
        template='plotly_white',
        margin=dict(l=150, r=80, t=30, b=50)
    )
    
    st.plotly_chart(fig_jam, use_container_width=True, config={'displayModeBar': False})
    
    # Insights
    col_jam1, col_jam2 = st.columns(2)
    
    with col_jam1:
        st.markdown("""
        <div class="insight-box">
            <div class="insight-title">💡 Insight Waktu Gempa</div>
            <div class="insight-text">
            Grafik menunjukkan jam puncak terjadinya gempa di setiap daerah berdasarkan data combined (Excel historical + BMKG real-time). 
            Informasi ini dapat digunakan untuk:<br><br>
            • <b>Perencanaan Respons:</b> Siapkan tim respons pada jam-jam dengan aktivitas tinggi<br>
            • <b>Edukasi Masyarakat:</b> Jadwalkan simulasi & sosialisasi pada jam-jam kritis<br>
            • <b>Monitoring BMKG:</b> Tingkatkan kesiagaan monitoring pada periode rawan
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_jam2:
        st.markdown("""
        <div class="insight-box">
            <div class="insight-title">⚠️ Catatan Penting</div>
            <div class="insight-text">
            • Gempa bumi bersifat acak dan tidak dapat diprediksi dengan akurat<br>
            • Pola waktu berdasarkan data historis, bukan jaminan di masa depan<br>
            • Preparedness harus diterapkan 24 jam sehari<br>
            • Data ini untuk insight analisis, bukan prediksi gempa
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.warning("⚠️ Tidak ada data untuk filter yang dipilih")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ===========================
# CHART 6: ANALISIS WAKTU DETAIL PER DAERAH
# ===========================
st.markdown('<div class="chart-section">', unsafe_allow_html=True)
st.markdown('<p class="chart-title">🕐 Analisis Waktu Gempa Per Daerah (Detail)</p>', unsafe_allow_html=True)
st.markdown('<p class="chart-subtitle">Rata-rata jam terjadinya gempa dan statistik waktu di setiap lokasi</p>', unsafe_allow_html=True)

if len(df_filtered) > 0:
    # Extract jam dari waktu gempa
    df_filtered_copy = df_filtered.copy()
    df_filtered_copy['jam'] = pd.to_datetime(df_filtered_copy['waktu']).dt.hour
    
    # Get all unique locations
    all_locations = sorted(df_filtered_copy['lokasi'].unique())
    
    # Filter untuk tampilan - top 15 untuk chart
    top_15_daerah = df_filtered_copy['lokasi'].value_counts().head(15).index
    df_top_15 = df_filtered_copy[df_filtered_copy['lokasi'].isin(top_15_daerah)]
    
    # Hitung jam paling sering gempa di setiap daerah
    jam_per_daerah = df_top_15.groupby('lokasi')['jam'].agg(lambda x: x.value_counts().idxmax()).reset_index()
    jam_per_daerah.columns = ['lokasi', 'jam_terbanyak']
    jam_per_daerah = jam_per_daerah.sort_values('jam_terbanyak')
    
    # Buat bar chart horizontal dengan key unik
    fig_jam = go.Figure(data=[go.Bar(
        y=jam_per_daerah['lokasi'],
        x=jam_per_daerah['jam_terbanyak'],
        orientation='h',
        marker=dict(
            color=jam_per_daerah['jam_terbanyak'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Jam (0-23)")
        ),
        text=[f"{int(jam):02d}:00" for jam in jam_per_daerah['jam_terbanyak']],
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>Jam Puncak: %{text}<extra></extra>'
    )])
    
    fig_jam.update_layout(
        height=420,
        showlegend=False,
        template='plotly_white',
        font=dict(size=11),
        xaxis=dict(title='Jam (0-23)', showgrid=True, gridwidth=1, gridcolor='#f0f0f0', range=[0, 24]),
        yaxis=dict(title='Daerah'),
        margin=dict(l=150, r=80, t=30, b=50)
    )
    
    st.plotly_chart(fig_jam, use_container_width=True, config={'displayModeBar': False}, key="waktu_chart_1")
    
    # DETAIL STATISTIK WAKTU PER DAERAH
    st.markdown('<p class="chart-subtitle" style="margin-top: 1.5rem; margin-bottom: 1rem;">📊 Statistik Waktu Gempa Detail Per Daerah</p>', unsafe_allow_html=True)
    
    # Pilih daerah untuk detail
    selected_daerah_waktu = st.selectbox(
        "Pilih Daerah untuk Melihat Detail Waktu Gempa:",
        all_locations,
        key="select_daerah_waktu"
    )
    
    # Filter data untuk daerah yang dipilih
    df_selected_daerah = df_filtered_copy[df_filtered_copy['lokasi'] == selected_daerah_waktu]
    
    if len(df_selected_daerah) > 0:
        # Hitung statistik waktu
        jam_counts = df_selected_daerah['jam'].value_counts().sort_index()
        jam_mean = df_selected_daerah['jam'].mean()
        jam_median = df_selected_daerah['jam'].median()
        jam_mode = df_selected_daerah['jam'].mode()[0] if len(df_selected_daerah['jam'].mode()) > 0 else 0
        jam_max_freq = jam_counts.max()
        jam_max_freq_hour = jam_counts.idxmax()
        
        # Tampilkan statistik dalam metric cards
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.8em; margin-bottom: 0.3rem;">🕐</div>
                <div class="metric-value">{int(jam_mode):02d}:00</div>
                <div class="metric-label">Jam Puncak (Mode)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_stat2:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.8em; margin-bottom: 0.3rem;">📊</div>
                <div class="metric-value">{int(jam_mean):02d}:00</div>
                <div class="metric-label">Rata-rata Jam</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_stat3:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.8em; margin-bottom: 0.3rem;">📈</div>
                <div class="metric-value">{jam_max_freq}</div>
                <div class="metric-label">Gempa Puncak (Jam {int(jam_max_freq_hour):02d}:00)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_stat4:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.8em; margin-bottom: 0.3rem;">🔢</div>
                <div class="metric-value">{len(df_selected_daerah)}</div>
                <div class="metric-label">Total Gempa</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Chart distribusi jam untuk daerah yang dipilih
        st.markdown('<p class="chart-subtitle" style="margin-top: 1.5rem; margin-bottom: 1rem;">Distribusi Gempa Per Jam di {}</p>'.format(selected_daerah_waktu), unsafe_allow_html=True)
        
        fig_jam_detail = go.Figure(data=[go.Bar(
            x=jam_counts.index,
            y=jam_counts.values,
            marker=dict(
                color=jam_counts.index,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Jam")
            ),
            text=jam_counts.values,
            textposition='auto',
            hovertemplate='<b>Jam %{x}:00</b><br>Jumlah Gempa: %{y}<extra></extra>'
        )])
        
        fig_jam_detail.update_layout(
            height=350,
            showlegend=False,
            template='plotly_white',
            font=dict(size=11),
            xaxis=dict(title='Jam (0-23)', showgrid=True, gridwidth=1, gridcolor='#f0f0f0'),
            yaxis=dict(title='Jumlah Gempa', showgrid=True, gridwidth=1, gridcolor='#f0f0f0'),
            margin=dict(l=60, r=80, t=30, b=50)
        )
        
        st.plotly_chart(fig_jam_detail, use_container_width=True, config={'displayModeBar': False}, key="waktu_chart_2")
        
        # Insight untuk daerah yang dipilih
        col_insight_1, col_insight_2 = st.columns(2)
        
        with col_insight_1:
            st.markdown(f"""
            <div class="insight-box">
                <div class="insight-title">💡 Insight Waktu Gempa {selected_daerah_waktu}</div>
                <div class="insight-text">
                • <b>Jam Puncak:</b> Pukul {int(jam_mode):02d}:00 (kemungkinan tertinggi gempa terjadi)<br>
                • <b>Total Gempa:</b> {len(df_selected_daerah)} kejadian dalam periode ini<br>
                • <b>Rata-rata:</b> Gempa terjadi rata-rata pada pukul {int(jam_mean):02d}:00<br>
                • <b>Frekuensi Puncak:</b> {jam_max_freq} gempa pada pukul {int(jam_max_freq_hour):02d}:00
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_insight_2:
            st.markdown("""
            <div class="insight-box">
                <div class="insight-title">⚠️ Rekomendasi Waktu</div>
                <div class="insight-text">
                • <b>Perencanaan Respons:</b> Siapkan tim standby pada jam-jam puncak<br>
                • <b>Simulasi Evakuasi:</b> Lakukan pada waktu yang berbeda (24 jam preparedness)<br>
                • <b>Monitoring BMKG:</b> Tingkatkan alert level pada jam-jam rawan<br>
                • <b>Catatan:</b> Gempa acak - preparedness tetap 24 jam sehari
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Tidak ada data gempa untuk daerah ini")

else:
    st.warning("⚠️ Tidak ada data untuk filter yang dipilih")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ===========================
# DECISION SUPPORT
# ===========================
st.markdown('<p class="chart-title">🎯 Rekomendasi & Decision Support</p>', unsafe_allow_html=True)

st.markdown('<div class="decision-grid">', unsafe_allow_html=True)

st.markdown("""
<div class="decision-box">
    <div class="decision-title">⚠️ Prioritas Mitigasi</div>
    <div class="decision-text">
    • Fokus pada top-10 daerah untuk sistem peringatan dini<br>
    • Area dengan gempa besar (>5) untuk infrastruktur tahan gempa<br>
    • Zone superfisial untuk edukasi dan pelatihan masyarakat<br>
    • Program disaster preparedness berkelanjutan berdasarkan data Excel + real-time BMKG
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="decision-box">
    <div class="decision-title">🛡️ Strategi Preparedness</div>
    <div class="decision-text">
    • Simulasi evakuasi rutin di daerah rawan gempa<br>
    • Penguatan kode bangunan tahan gempa yang ketat<br>
    • Pelatihan respons darurat berkelanjutan untuk masyarakat<br>
    • Monitoring real-time dengan BMKG API integration
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ===========================
# DATA TABLE
# ===========================
with st.expander("📋 Lihat Data Detail Lengkap", expanded=False):
    st.markdown('**Tabel Data Gempa Terfilter (Combined: Excel + BMKG)**')
    
    display_df = df_filtered[["waktu_display", "magnitudo", "kedalaman_km", "latitude", "longitude", "lokasi", "source"]].copy()
    display_df.columns = ["Waktu", "Magnitudo", "Kedalaman (km)", "Latitude", "Longitude", "Lokasi", "Source"]
    
    st.dataframe(display_df, use_container_width=True, height=500, hide_index=True)
    
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV", data=csv,
        file_name=f"analisis_gempa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

# ===========================
# FOOTER
# ===========================
st.markdown("""
<div class="footer-text">
    <p>📊 <strong>Dashboard Analisis Gempa Indonesia - GIS & Decision Support System</strong></p>
    <p>Seamless Data: Excel (Aug-Dec 2025) + BMKG Real-time (1 Jan - sekarang)</p>
    <p>Sumber: BMKG (Badan Meteorologi, Klimatologi, dan Geofisika) + Historical Excel</p>
</div>

""", unsafe_allow_html=True)
