
import streamlit as st
import pandas as pd
import numpy as np
import joblib

# Load model
model = joblib.load('xgb_karhutla_model.pkl')

st.set_page_config(page_title="Peringatan Dini Karhutla", layout="wide")
st.title("🔥 Dashboard Peringatan Dini Karhutla Kalimantan")
st.write("Masukkan kondisi cuaca dan histori kebakaran hari ini untuk melihat probabilitas titik panas besok.")

# Buat 2 kolom untuk input
col1, col2 = st.columns(2)

with col1:
    st.subheader("Kondisi Cuaca Hari Ini")
    t2m_max = st.number_input("Suhu Maksimum (°C)", min_value=20.0, max_value=45.0, value=33.0)
    rh2m = st.number_input("Kelembaban Relatif (%)", min_value=10.0, max_value=100.0, value=60.0)
    ws2m = st.number_input("Kecepatan Angin (m/s)", min_value=0.0, max_value=20.0, value=2.5)
    prectotcorr = st.number_input("Curah Hujan Hari Ini (mm)", min_value=0.0, max_value=100.0, value=0.0)
    
with col2:
    st.subheader("Histori Kebakaran & Kekeringan")
    hotspot_lag1 = st.number_input("Titik Panas Kemarin", min_value=0, value=0)
    hotspot_lag3 = st.number_input("Total Titik Panas 3 Hari Lalu", min_value=0, value=0)
    hotspot_lag7 = st.number_input("Total Titik Panas 7 Hari Lalu", min_value=0, value=0)
    rain_7d = st.number_input("Akumulasi Hujan 7 Hari (mm)", min_value=0.0, value=5.0)
    rain_14d = st.number_input("Akumulasi Hujan 14 Hari (mm)", min_value=0.0, value=10.0)

# Fitur kalender (otomatis pakai hari ini)
import datetime
today = datetime.date.today()
month = today.month
dayofyear = today.timetuple().tm_yday

# Tombol Prediksi
if st.button("Prediksi Risiko Besok", type="primary"):
    # Susun dataframe input sesuai urutan fitur saat training
    input_df = pd.DataFrame([{
        't2m_max': t2m_max,
        'rh2m': rh2m,
        'ws2m': ws2m,
        'prectotcorr': prectotcorr,
        'hotspot_lag1': hotspot_lag1,
        'hotspot_lag3': hotspot_lag3,
        'hotspot_lag7': hotspot_lag7,
        'rain_7d': rain_7d,
        'rain_14d': rain_14d,
        'month': month,
        'dayofyear': dayofyear
    }])
    
    # Prediksi
    proba = model.predict_proba(input_df)[0][1]
    
    st.markdown("---")
    st.subheader("Hasil Prediksi")
    
    # Tampilkan probabilitas dengan progress bar
    st.metric(label="Probabilitas Titik Panas Besok", value=f"{proba*100:.1f}%")
    st.progress(float(proba))
    
    # Logika Peringatan
    if proba >= 0.70:
        st.error("🚨 **RISIKO SANGAT TINGGI!** Kondisi sangat kering. Segera tingkatkan patroli dan siagakan tim pemadam di area ini.")
    elif proba >= 0.40:
        st.warning("⚠️ **RISIKO SEDANG.** Waspadai potensi percikan api. Pastikan lahan tidak dibuka dengan cara dibakar.")
    else:
        st.success("✅ **RISIKO RENDAH.** Kondisi cuaca dan histori relatif aman.")
