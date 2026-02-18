import streamlit as st
from views import beranda, dataset, akurasi, latih, klasifikasi
from PIL import Image
import base64

# Inisialisasi state untuk halaman saat ini
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Beranda"

# ==================== CSS CONFIGURATION ==================== #
st.markdown("""
<style>
    :root {
        --dark-red: #DF0000;
        --white: #FFFFFF;
        --soft-bg: #FFF5F5;
        --text-dark: #2d3436;
        --text-light: #f5f6fa;
        --sidebar-bg: #FFB6B6;
    }

    .stApp {
        background-color: var(--soft-bg);
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
        color:  #DF0000 !important; /* Ubah warna menjadi #E91E63 */
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

# ==================== SIDEBAR ==================== #
def create_sidebar():
    st.sidebar.markdown(f"""
    <div class="sidebar-header">
        <img src="data:image/png;base64,{base64.b64encode(open('logo_freshpi.png', 'rb').read()).decode()}" class="sidebar-logo" />
        <div class="sidebar-text-container">
            <h3 class="sidebar-subtitle"> KLASIFIKASI KESEGARAN DAGING SAPI</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    options = ["Beranda", "Dataset Penelitian", "Latih Model Baru", "Klasifikasi Dengan Model Tersimpan", "Akurasi Terbaik"]
    
    with st.sidebar:
        st.markdown('<div class="sidebar-button-container">', unsafe_allow_html=True)
        
        for menu in options:
            if st.button(menu, 
                        key=f"btn_{menu}",
                        type="primary" if st.session_state.current_page == menu else "secondary"):
                st.session_state.current_page = menu
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== MAIN CONTENT ==================== #
def render():
    create_sidebar()
    
    # Render halaman berdasarkan pilihan
    if st.session_state.current_page == "Beranda":
        beranda.render()
    elif st.session_state.current_page == "Dataset Penelitian":
        dataset.render()
    elif st.session_state.current_page == "Latih Model Baru":
        latih.render()
    elif st.session_state.current_page == "Klasifikasi Dengan Model Tersimpan":
        klasifikasi.render()
    elif st.session_state.current_page == "Akurasi Terbaik":
        akurasi.render()

if __name__ == "__main__":
    render()