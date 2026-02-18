import streamlit as st
import pandas as pd
from utils import get_accuracy_data

def render():
    # CSS Custom dengan rounded corners untuk semua gambar kecuali logo
    st.markdown("""
    <style>
        /* Judul besar */
        .big-title {
            font-size: 36px !important;
            font-weight: bold !important;
            text-align: center !important;
            margin-bottom: 20px !important;
            color: #E91E63 !important;
        }
        
        /* Info box */
        .stAlert {
            background-color: #F8BBD0 !important;
            border-left: 5px solid #E91E63 !important;
            border-radius: 8px !important;
        }
        
        /* Custom box untuk keterangan */
        .info-box {
            background-color: #F8BBD0 !important;
            border-left: 5px solid #E91E63 !important;
            border-radius: 8px !important;
            padding: 1rem !important;
            margin: 1.5rem 0 !important;
        }
        
        /* Style untuk gambar dataset dengan rounded corners */
        .dataset-image img {
            border-radius: 15px !important;
            overflow: hidden !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
            transition: transform 0.3s ease !important;
        }
        
        /* Style khusus untuk logo (tanpa efek) */
        .logo-image img {
            border-radius: 0 !important;
            box-shadow: none !important;
        }
        
        /* Efek hover untuk gambar dataset */
        .dataset-image img:hover {
            transform: scale(1.02) !important;
        }
        
        /* Style untuk tabs */
        .stTabs [data-baseweb="tab"] {
            background: #F8BBD0 !important;
            border: 1px solid #E91E63 !important;
            border-radius: 5px !important;
            margin: 0 5px !important;
            padding: 10px 20px !important;
        }
        
        .stTabs [aria-selected="true"] {
            background: #E91E63 !important;
            color: white !important;
        }
        
        /* Style untuk subjudul */
        h3 {
            color: #E91E63 !important;
            text-align: center !important;
            font-size: 18px !important;
            margin-top: 1em !important;
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

    # Judul besar
    st.markdown('<div class="big-title">AKURASI TERBAIK</div>', unsafe_allow_html=True)
    
    # Info box pink
    st.warning("Berikut hasil akurasi terbaik sistem klasifikasi kesegaran daging sapi")

    # Membuat tab
    tab1, tab2 = st.tabs(["Dengan Cahaya Tambahan", "Tanpa Cahaya Tambahan"])

    with tab1:
        st.markdown("<h3>HASIL AKURASI DENGAN TAMBAHAN CAHAYA (CERAH)</h3>", unsafe_allow_html=True)
        data_dengan_cahaya, _ = get_accuracy_data()
        st.dataframe(data_dengan_cahaya, use_container_width=True)
        st.line_chart(data_dengan_cahaya.set_index("Keterangan Data"))

    with tab2:
        st.markdown("<h3>HASIL AKURASI TANPA TAMBAHAN CAHAYA (GELAP)</h3>", unsafe_allow_html=True)
        _, data_tanpa_cahaya = get_accuracy_data()
        st.dataframe(data_tanpa_cahaya, use_container_width=True)
        st.line_chart(data_tanpa_cahaya.set_index("Keterangan Data"))

    # Copyright text at the very bottom
    st.markdown("""
    <div class="copyright-container">
        <p>© 2025 FreshPi - Sistem Klasifikasi Kesegaran Daging Sapi. All Rights Reserved.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    render()