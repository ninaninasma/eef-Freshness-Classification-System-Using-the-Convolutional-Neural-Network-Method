# utils.py
import mysql.connector
import os
import pandas as pd
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, IMAGE_DIR_SEGAR, IMAGE_DIR_TIDAK_SEGAR
import streamlit as st

def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def get_recommendation(result):
    return "Aman jika dikonsumsi" if result == 'segar' else "Berbahaya jika dikonsumsi"

def save_classification(result, image_path):
    recommendation = get_recommendation(result)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Gambar (FileGambar) VALUES (%s)", (image_path,))
        gambar_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO Klasifikasi (Id_Gambar, HasilKlasifikasi, SaranKlasifikasi) VALUES (%s, %s, %s)",
            (gambar_id, result, recommendation)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        st.warning(f"Gagal menyimpan ke database: {e}")

def get_image_paths(label):
    if label == 'segar':
        image_dir = IMAGE_DIR_SEGAR
    else:
        image_dir = IMAGE_DIR_TIDAK_SEGAR
    if not os.path.exists(image_dir):
        return []
    return [os.path.join(image_dir, f) for f in os.listdir(image_dir)[:6]]

def count_images(label):
    if label == 'segar':
        path = IMAGE_DIR_SEGAR
    else:
        path = IMAGE_DIR_TIDAK_SEGAR
    if not os.path.exists(path):
        return 0
    return len(os.listdir(path))

def get_accuracy_data():
    data_dengan_cahaya = pd.DataFrame({
        "Keterangan Data": ["1440 data asli", "914 data cropping seleksi", "1080 data cropping "],
        "Data Latih": [99.42, 97.50, 96.65],
        "Data Validasi": [98.65, 98.35, 96.75],
        "Data Uji": [100.00, 98.91, 96.30],
        "Rata-rata": [99.36,  98.25, 96.54]
    })

    data_tanpa_cahaya = pd.DataFrame({
        "Keterangan Data": ["600 data asli", "460 data cropping seleksi", "600 data cropping"],
        "Data Latih": [96.90, 94.10, 94.29],
        "Data Validasi": [90.00, 88.04, 95.00],
        "Data Uji": [98.33,  100.00, 85.00],
        "Rata-rata": [95.08, 94.05, 91.43]
    })
    return data_dengan_cahaya, data_tanpa_cahaya