import streamlit as st
import base64
from config import LOGO_PATH

def load_logo_base64():
    with open(LOGO_PATH, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

def render():
    logo_base64 = load_logo_base64()
    
    st.markdown("""
    <style>
        .main-container {
            text-align: center;
            padding: 2rem 1rem;
            font-family: 'Arial', sans-serif;
            background-color: #ffe6e6;
        }
        .logo-img {
            width: 500px;
            margin-bottom: 1rem;
        }
        .main-title {
            color: #c62828;
            font-weight: 700;
            margin-bottom: 0.5rem;
            font-size: 2.5rem;
        }
        .subtitle {
            color: #555;
            margin-bottom: 2rem;
            font-size: 1.2rem;
        }
        .features-container {
            display: flex;
            justify-content: space-between;
            gap: 2rem;
            margin: 2rem auto;
            flex-wrap: wrap;
            max-width: 900px;
        }
        .feature-box {
            flex: 1;
            min-width: 300px;
            max-width: 400px;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            background-color: #ffb6c1;
        }
        .feature-title {
            margin-top: 0;
            font-size: 1.3rem;
            color: #8b0000;
        }
        .feature-list {
            padding-left: 1.2rem;
            font-weight: 500;
            line-height: 1.6;
            color: #8b0000;
        }
        .info-box {
            max-width: 800px;
            margin: 2rem auto;
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: left;
        }
        .info-title {
            color: #c62828;
            margin-top: 0;
            font-size: 1.2rem;
        }
        .cta-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin: 2rem 0;
        }
        .cta-text {
            font-size: 1.2rem;
            color: #333;
            font-weight: 600;
            text-align: center;
            margin-bottom: 1rem;
        }
        .custom-button {
            display: flex;
            justify-content: center;
            width: 100%;
            background-color: #DF0000 !important;
        }
        /* Styling spesifik untuk button "MULAI KLASIFIKASI" */
        [data-testid="stButton"] > button#start_classification_btn {
            background-color: #DF0000 !important; /* Warna merah tetap */
            color: #DF0000 !important;
            border-radius: 20px;
            padding: 0.5rem 2rem;
            font-weight: 600;
            font-size: 1rem;
            margin: 0 auto;
            border: none;
            cursor: pointer;
            box-shadow: none !important; /* Hapus shadow lain */
        }
        /* Hapus efek hover jika tidak diinginkan */
        [data-testid="stButton"] > button#start_classification_btn:hover {
            background-color: #DF0000 !important; /* Tetap merah saat hover */
        }
        /* Copyright styling */
        .copyright-container {
            text-align: center;
            margin-top: 3rem;
            padding: 1rem;
            color: #c62828; 
            font-family: 'Roboto', 'Arial', sans-serif; 
            font-size: 0.8rem; 
        }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown(f"""
    <div class="main-container">
        <img src="data:image/png;base64,{logo_base64}" class="logo-img" />
        <h1 class="main-title">FRESHPI</h1>
        <h3 class="subtitle">Klasifikasi Kesegaran Daging Sapi</h3>
    </div>
    """, unsafe_allow_html=True)

    # Fitur
    st.markdown("""
    <div class="features-container">
        <div class="feature-box">
            <h3 class="feature-title">Daging Segar</h3>
            <ul class="feature-list">
                <li>Warna merah cerah</li>
                <li>Tekstur kenyal dan elastis</li>
                <li>Bau segar, tidak amis</li>
                <li>Aman jika dikonsumsi</li>
            </ul>
        </div>
        <div class="feature-box">
            <h3 class="feature-title">Daging Tidak Segar</h3>
            <ul class="feature-list">
                <li>Warna gelap atau kecoklatan</li>
                <li>Tekstur lengket dan berlendir</li>
                <li>Bau tidak sedap, amis</li>
                <li>Berbahaya jika dikonsumsi</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Informasi
    st.markdown("""
    <div class="info-box">
        <h4 class="info-title">Mengapa Penting Mengenali Kesegaran Daging Sapi?</h4>
        <p>Daging sapi termasuk dalam produk subsektor peternakan yang menjadi komoditas pangan strategis karena memiliki kualitas tinggi dalam memenuhi kebutuhan protein.</p>
        <p>Daging sapi yang tidak segar dapat membahayakan kesehatan karena mengandung banyak kuman yang berpotensi menyebabkan penyakit.</p>
        <p>Dengan metode CNN untuk klasifikasi, Anda dapat mengidentifikasi kesegaran daging sapi untuk mencegah risiko kesehatan.</p>
        <p style="font-style: italic; color: #666;">Selalu periksa kualitas daging sebelum dikonsumsi, ya!</p>
    </div>
    """, unsafe_allow_html=True)

    # Tombol Klasifikasi
    st.markdown('<div class="cta-container">', unsafe_allow_html=True)
    st.markdown('<p class="cta-text">Mulai klasifikasi sekarang dan pastikan daging Anda aman!</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="custom-button">', unsafe_allow_html=True)
        if st.button("**MULAI KLASIFIKASI**", key="start_classification_btn"):
            st.session_state.current_page = "Klasifikasi Dengan Model Tersimpan"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Copyright text at the very bottom
    st.markdown("""
    <div class="copyright-container">
        <p>© 2025 FreshPi - Sistem Klasifikasi Kesegaran Daging Sapi. All Rights Reserved.</p>
    </div>
    """, unsafe_allow_html=True)