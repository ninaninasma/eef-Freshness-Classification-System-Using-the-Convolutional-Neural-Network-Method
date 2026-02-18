import streamlit as st
from utils import get_image_paths

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
        
        /* Sidebar styling - Sama persis dengan beranda.py */
        :root {
            --dark-red: #DF0000;
            --white: #FFFFFF;
            --soft-bg: #FFF5F5;
            --text-dark: #2d3436;
            --text-light: #f5f6fa;
            --sidebar-bg: #FFB6B6;
        }

        [data-testid="stSidebar"] {
            background-color: var(--sidebar-bg);
            padding: 0rem 0.2rem; /* Hapus padding atas untuk posisi paling atas */
        }

        /* Sidebar header container */
        .sidebar-header {
            display: flex;
            align-items: center; /* Tetap center untuk vertikal */
            gap: 0.8rem;
            margin-bottom: 0.2rem; /* Mengurangi jarak bawah */
            border-bottom: 2px solid var(--dark-red); /* Tambahkan garis bawah dengan warna merah gelap */
        }

        /* Logo styling */
        .sidebar-logo {
            width: 100px; /* Dikecilkan dari 120px untuk presisi */
            height: auto;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
        }

        /* Text container untuk subtitle */
        .sidebar-text-container {
            display: flex;
            flex-direction: column;
            justify-content: center; /* Tetap center untuk horizontal */
            flex: 1; /* Mengisi ruang agar teks terpusat relatif logo */
            gap: -0.1rem; /* Jarak negatif dipertahankan untuk presisi */
            margin-top: 0.1rem; /* Disesuaikan untuk menjaga proporsi */
            padding: 0 0.2rem; /* Padding kecil untuk penyesuaian */
        }

        /* Sidebar subtitle styling - DIKECILKAN LAGI */
        .sidebar-subtitle {
            color: #DF0000 !important; /* Ubah warna menjadi #E91E63 */
            font-size: 0.45rem; /* Diperkecil dari 0.5rem untuk presisi */
            margin: 0;
            line-height: 1.0; /* Diperkecil dari 1.1 untuk keterbacaan */
            padding-bottom: 0.1rem;
            font-weight: 500;
            text-align: center; /* Memusatkan teks secara horizontal */
            height: 100px !important; /* Sesuai tinggi logo (100px dari .sidebar-logo) */
            display: flex !important;
            align-items: center !important;
            justify-content: center !important; /* Memastikan teks terpusat vertikal dan horizontal */
        }

        /* Button container - Dipindah lebih ke atas */
        .sidebar-button-container {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            width: 100%;
            margin-top: -1rem; /* Menggeser tombol lebih ke atas */
        }

        /* Base button style */
        .stButton > button {
            width: 100%;
            height: 44px;
            background-color: var(--white);
            color: var(--text-dark);
            border: none;
            border-radius: 8px;
            padding: 0 1rem;
            margin: 0;
            font-weight: 600;
            font-size: 1rem;
            text-align: left;
            transition: none;
        }

        /* Active button style */
        .stButton > button[kind="primary"] {
            background-color: var(--dark-red);
            color: var(--text-light);
            position: relative;
        }

        /* Active indicator */
        .stButton > button[kind="primary"]::after {
            content: "";
            position: absolute;
            right: 0;
            top: 0;
            height: 100%;
            width: 4px;
            background-color: var(--dark-red);
            border-top-right-radius: 8px;
            border-bottom-right-radius: 8px;
        }

        /* Hover effect */
        .stButton > button:not([kind="primary"]):hover {
            background-color: #f0f0f0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Judul besar
    st.markdown('<div class="big-title">DATASET PENELITIAN</div>', unsafe_allow_html=True)
    
    # Info box
    st.warning("Berikut contoh dataset primer daging sapi yang digunakan dalam penelitian")

    # Membuat tabs
    tab1, tab2 = st.tabs([" Daging Sapi Segar", "Daging Sapi Tidak Segar"])

    # Image captions
    captions = [
        "Data Asli (Cerah)",
        "Data Cropping Seleksi (Cerah)",
        "Data Cropping Tanpa Seleksi (Cerah)",
        "Data Asli (Gelap)",
        "Data Cropping Seleksi (Gelap)",
        "Data Cropping Tanpa Seleksi (Gelap)"
    ]

    def display_images(condition):
        """Helper function to display images"""
        images = get_image_paths(condition)
        
        if len(images) < 6:
            st.warning(f"Jumlah gambar {condition} kurang dari 6. Pastikan dataset lengkap.")
            return
        
        with st.container():
            st.markdown(f'<h3>SAMPLE DATASET DAGING SAPI {"SEGAR" if condition == "segar" else "TIDAK SEGAR"}</h3>', 
                       unsafe_allow_html=True)
            
            # Baris pertama gambar
            cols = st.columns(3)
            for idx in range(3):
                with cols[idx]:
                    st.markdown('<div class="dataset-image">', unsafe_allow_html=True)
                    st.image(
                        images[idx], 
                        use_container_width=True,
                        caption=captions[idx]
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Baris kedua gambar
            cols = st.columns(3)
            for idx in range(3, 6):
                with cols[idx%3]:
                    st.markdown('<div class="dataset-image">', unsafe_allow_html=True)
                    st.image(
                        images[idx], 
                        use_container_width=True,
                        caption=captions[idx]
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Keterangan dalam box
            st.markdown("""
            <div class="info-box">
                <strong>Keterangan:</strong><br>
                • <strong>Cerah</strong>: Kondisi dengan tambahan cahaya<br>
                • <strong>Gelap</strong>: Kondisi tanpa tambahan cahaya<br>
                • <strong>Cropping</strong>: Fokus pada daging sapi<br>
                • <strong>Seleksi</strong>: Tidak ada data blur<br>
                • <strong>Tanpa Seleksi</strong>: Ada data blur
            </div>
            """, unsafe_allow_html=True)

    with tab1:
        display_images("segar")

    with tab2:
        display_images("tidak segar")
    
    # Copyright text at the very bottom
    st.markdown("""
    <div class="copyright-container">
        <p>© 2025 FreshPi - Sistem Klasifikasi Kesegaran Daging Sapi. All Rights Reserved.</p>
    </div>
    """, unsafe_allow_html=True)