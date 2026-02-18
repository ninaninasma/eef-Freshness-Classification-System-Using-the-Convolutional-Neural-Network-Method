import streamlit as st
from PIL import Image
import os
import re
import mysql.connector
import cv2
import numpy as np
from model import classify_image, load_freshpi_model, load_svm_model, load_feature_model, model_selection_ui
from utils import get_recommendation
import tensorflow as tf
from tensorflow.keras.models import Model  # type: ignore
from tensorflow.keras.applications import InceptionV3  # type: ignore
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, BatchNormalization  # type: ignore
from tensorflow.keras.preprocessing.image import ImageDataGenerator  # type: ignore
import joblib
import pandas as pd
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'freshpi_v2'
}

# Path ke folder model dan SVM
MODEL_FOLDER = 'best model/'
SVM_PATH = 'one_class_svm.pkl'

# Fungsi untuk memindai folder best model/ dan membuat MODEL_OPTIONS secara dinamis
def natural_sort_key(text):
    return [int(t) if t.isdigit() else t.lower()
            for t in re.split(r'(\d+)', text)]

def get_model_options():
    os.makedirs(MODEL_FOLDER, exist_ok=True)

    model_files = [f for f in os.listdir(MODEL_FOLDER) if f.endswith('.h5')]
    model_files.sort(key=natural_sort_key)

    if not model_files:
        return {}

    return {
        os.path.splitext(f)[0]: os.path.join(MODEL_FOLDER, f)
        for f in model_files
    }

# Inisialisasi MODEL_OPTIONS di session state
if 'MODEL_OPTIONS' not in st.session_state or not st.session_state.MODEL_OPTIONS:
    st.session_state.MODEL_OPTIONS = get_model_options()

# Fungsi untuk menyimpan hasil ke database
def save_to_database(file_path, result, recommendation, confidence_segar, confidence_tidak_segar):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Konversi ke persentase
        confidence_segar = min(100.0, max(0.0, round(float(confidence_segar) * 100, 2)))
        confidence_tidak_segar = min(100.0, max(0.0, round(float(confidence_tidak_segar) * 100, 2)))
        
        # Simpan ke tabel Gambar
        file_name = os.path.basename(file_path)
        cursor.execute("INSERT INTO Gambar (FileGambar) VALUES (%s)", (file_name,))
        image_id = cursor.lastrowid
        
        # Simpan ke tabel Klasifikasi
        truncated_recommendation = recommendation[:25]
        cursor.execute(
            """INSERT INTO Klasifikasi 
            (Id_Gambar, HasilKlasifikasi, SaranKlasifikasi, Confidence_Segar, Confidence_TidakSegar) 
            VALUES (%s, %s, %s, %s, %s)""",
            (image_id, result, truncated_recommendation, confidence_segar, confidence_tidak_segar)
        )
        conn.commit()
        return True
    except mysql.connector.Error as err:
        st.error(f"Database error: {err}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Fungsi utama untuk render aplikasi
def render():
    # CSS Custom untuk styling
    st.markdown("""
    <style>
        /* Judul besar */
        .big-title {
            font-size: 36px !important;
            font-weight: bold !important;
            text-align: center !important;
            margin-bottom: 20px !important;
            color: #E91E63 !important;  /* Warna pink gelap */
        }

        /* Style untuk tabs */
        .stTabs [data-baseweb="tab"] {
            background: #F8BBD0 !important;  /* Pink muda */
            border: 1px solid #E91E63 !important;  /* Pink gelap */
            border-radius: 5px !important;
            margin: 0 5px !important;
            padding: 10px 20px !important;
        }
        
        .stTabs [aria-selected="true"] {
            background: #E91E63 !important;  /* Pink gelap */
            color: white !important;
        }
        
        .stAlert {
            background-color: #FCE4EC !important;
            border-left: 5px solid #E91E63 !important;
            border-radius: 8px !important;
        }
        
        .center-button {
            display: flex;
            justify-content: center;
            margin: 20px 0;
        }
        
        .result-container {
            text-align: center;
            margin: 20px 0;
        }
        
        .confidence-box {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
            background-color: #f9f9f9;
        }
        
        .confidence-item {
            margin: 10px 0;
        }
        
        .confidence-bar-container {
            height: 24px;
            background-color: #e0e0e0;
            border-radius: 12px;
            margin: 5px 0;
            position: relative;
        }
        
        .confidence-bar-fill {
            height: 100%;
            border-radius: 12px;
            position: relative;
        }
        
        .confidence-number {
            position: absolute;
            left: 10px;
            top: 50%;
            transform: translateY(-50%);
            color: black;
            font-weight: bold;
            font-size: 12px;
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
    st.markdown('<div class="big-title">KLASIFIKASI KESEGARAN DAGING SAPI</div>', unsafe_allow_html=True)

    # Klasifikasi dengan Model Tersimpan
    st.warning("""
        **Pastikan gambar yang diupload sesuai dengan model yang akan dipilih:**\n
        1. **Asli** untuk gambar tanpa crop\n
        2. **Crop Seleksi** untuk crop tanpa blur\n
        3. **Crop Tanpa Seleksi** untuk crop dengan blur\n
        4. **Cerah** untuk gambar dengan cahaya tambahan\n
        5. **Gelap** untuk tanpa cahaya tambahan\n
        6. Gambar serupa dengan dataset yang digunakan saat **Latih Model Baru**.
        """)

        # Upload gambar
    uploaded_file = st.file_uploader(
            "Drag and drop file here\nLimit 200MB per file • JPG, JPEG, PNG",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed",
            key="uploader_tab1"
        )

    if uploaded_file:
            try:
                img = Image.open(uploaded_file)
                st.image(img, caption="Gambar yang diupload", use_container_width=True)
                
                # Simpan ke folder 'temp'
                os.makedirs("temp", exist_ok=True)
                uploaded_path = os.path.join("temp", uploaded_file.name)
                img.save(uploaded_path)
                
                # Konversi gambar ke PIL Image untuk classify_image
                img_input = Image.open(uploaded_path)
            except Exception as e:
                st.error(f"Error: {e}")
                return

            # Perbarui MODEL_OPTIONS untuk memastikan daftar model terbaru
            st.session_state.MODEL_OPTIONS = get_model_options()

            # Pilihan model
            if not st.session_state.MODEL_OPTIONS:
                st.error("Tidak ada model yang tersedia. Tambahkan model di folder 'best model/' atau latih model baru di Tab 'Latih Model Baru'.")
                return
            model_choice = st.selectbox(
                "Pilih model:",
                options=list(st.session_state.MODEL_OPTIONS.keys()),
                help="Pilih model untuk klasifikasi kesegaran daging sapi",
                key="model_choice_tab1"
            )
            
            try:
                model_path = st.session_state.MODEL_OPTIONS[model_choice]
            except KeyError:
                st.error(f"Model '{model_choice}' tidak ditemukan. Silakan pilih model lain atau perbarui folder 'best model/'.")
                return

            model = load_freshpi_model(model_path)
            if model is None:
                st.error(f"Gagal memuat model dari: {model_path}")
                return

            svm_model = load_svm_model()
            if svm_model is None:
                st.error(f"Gagal memuat model SVM dari: {SVM_PATH}")
                return

            feature_model = load_feature_model(model_path)
            if feature_model is None:
                st.error(f"Gagal memuat model fitur dari: {model_path}")
                return

            # Tombol klasifikasi
            st.markdown('<div class="center-button">', unsafe_allow_html=True)
            if st.button("Mulai Klasifikasi", help="Proses gambar untuk menentukan kesegaran", type="primary", key="classify_tab1"):
                with st.spinner("Menganalisis..."):
                    try:
                        # Klasifikasi gambar menggunakan fungsi dari model.py
                        result, confidence_segar, confidence_tidak_segar = classify_image(img_input, model, svm_model, feature_model)
                        result = result.lower()
                        
                        # Tampilkan hasil
                        st.markdown('<div class="result-container">', unsafe_allow_html=True)
                        st.markdown("---")
                        
                        if result == "bukan daging sapi":
                            st.error(f"**Hasil:** **bukan** daging sapi")
                            recommendation = "Upload daging sapi untuk analisis kesegaran"
                            st.info(f"**Saran:** {recommendation}")
                            
                            # Tingkat kepercayaan untuk outlier
                            confidence_segar = 0.0
                            confidence_tidak_segar = 0.0
                            segar_percent = 0.0
                            tidak_segar_percent = 0.0
                            
                            st.markdown("**Tingkat Kepercayaan:**")
                            
                            # Bar Segar
                            st.markdown('<div class="confidence-item">', unsafe_allow_html=True)
                            st.markdown('**Segar**')
                            st.markdown(
                                f"""<div class="confidence-bar-container">
                                    <div class="confidence-bar-fill" style="width: {segar_percent}%; background-color: #4CAF50;">
                                        <div class="confidence-number">{segar_percent:.2f}%</div>
                                    </div>
                                </div>""", 
                                unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Bar Tidak Segar
                            st.markdown('<div class="confidence-item">', unsafe_allow_html=True)
                            st.markdown('**Tidak Segar**')
                            st.markdown(
                                f"""<div class="confidence-bar-container">
                                    <div class="confidence-bar-fill" style="width: {tidak_segar_percent}%; background-color: #F44336;">
                                        <div class="confidence-number">{tidak_segar_percent:.2f}%</div>
                                    </div>
                                </div>""", 
                                unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)  # Tutup confidence-box
                        else:
                            if result == 'segar':
                                st.success(f"**Hasil:** Daging sapi **segar**")
                            else:
                                st.error(f"**Hasil:** Daging sapi **tidak segar**")
                            
                            # Tampilkan tingkat kepercayaan
                            confidence_segar = round(max(0.0, min(1.0, float(confidence_segar))), 2)
                            confidence_tidak_segar = round(max(0.0, min(1.0, float(confidence_tidak_segar))), 2)
                            segar_percent = confidence_segar * 100
                            tidak_segar_percent = confidence_tidak_segar * 100
                            
                            st.markdown("**Tingkat Kepercayaan:**")
                            
                            # Bar Segar
                            st.markdown('<div class="confidence-item">', unsafe_allow_html=True)
                            st.markdown('**Segar**')
                            st.markdown(
                                f"""<div class="confidence-bar-container">
                                    <div class="confidence-bar-fill" style="width: {segar_percent}%; background-color: #4CAF50;">
                                        <div class="confidence-number">{segar_percent:.2f}%</div>
                                    </div>
                                </div>""", 
                                unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Bar Tidak Segar
                            st.markdown('<div class="confidence-item">', unsafe_allow_html=True)
                            st.markdown('**Tidak Segar**')
                            st.markdown(
                                f"""<div class="confidence-bar-container">
                                    <div class="confidence-bar-fill" style="width: {tidak_segar_percent}%; background-color: #F44336;">
                                        <div class="confidence-number">{tidak_segar_percent:.2f}%</div>
                                    </div>
                                </div>""", 
                                unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)  # Tutup confidence-box
                            
                            recommendation = get_recommendation(result)
                            st.info(f"**Saran:** {recommendation}")
                        
                        # Simpan ke database
                        if save_to_database(uploaded_path, result, recommendation, 
                                           confidence_segar, confidence_tidak_segar):
                            st.success("**Informasi telah tersimpan di database**")
                        else:
                            st.warning("Data klasifikasi berhasil tapi gagal menyimpan ke database")
                        
                        st.markdown('</div>', unsafe_allow_html=True)  # Tutup result-container
                        
                    except Exception as e:
                        st.error(f"**Error:** {str(e)}")

    # Copyright
    st.markdown("""
    <div class="copyright-container">
        <p>© 2025 FreshPi - Sistem Klasifikasi Kesegaran Daging Sapi. All Rights Reserved.</p>
    </div>
    """, unsafe_allow_html=True)

# Jalankan aplikasi
if __name__ == "__main__":
    render()