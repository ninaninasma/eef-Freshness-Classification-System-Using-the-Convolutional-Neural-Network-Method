import streamlit as st
from PIL import Image
import os
import numpy as np
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

# Path ke folder model dan SVM
MODEL_FOLDER = 'best model/'
ACCURACY_CSV_PATH = 'model_accuracies.csv'  # Path untuk menyimpan akurasi model baru

# Fungsi untuk memindai folder best model/ dan membuat MODEL_OPTIONS secara dinamis
def get_model_options():
    os.makedirs(MODEL_FOLDER, exist_ok=True)
    model_files = [f for f in os.listdir(MODEL_FOLDER) if f.endswith('.h5')]
    model_files.sort()  # Urutkan file berdasarkan abjad
    if not model_files:
        return {}
    return {os.path.splitext(f)[0]: os.path.join(MODEL_FOLDER, f) for f in model_files}

# Fungsi untuk menghitung confusion matrix
def compute_confusion_matrix(model, generator):
    # Reset generator untuk memastikan mulai dari awal
    generator.reset()
    y_true = []
    y_pred = []
    
    # Iterasi melalui generator untuk mendapatkan prediksi
    for _ in range(len(generator)):
        images, labels = next(generator)
        # Konversi label one-hot ke indeks kelas (0: segar, 1: tidak segar)
        true_labels = np.argmax(labels, axis=1)
        # Prediksi menggunakan model
        pred_probs = model.predict(images, verbose=0)
        pred_labels = np.argmax(pred_probs, axis=1)
        y_true.extend(true_labels)
        y_pred.extend(pred_labels)
    
    # Hitung confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    return cm

# Fungsi untuk menampilkan confusion matrix sebagai heatmap
def plot_confusion_matrix(cm, title):
    labels = ['Segar', 'Tidak Segar']
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels, ax=ax)
    ax.set_xlabel('Prediksi')
    ax.set_ylabel('Aktual')
    ax.set_title(title)
    plt.tight_layout()
    return fig

# Fungsi untuk menyimpan akurasi ke CSV
def save_accuracy_to_csv(model_name, train_accuracy, val_accuracy, test_accuracy):
    try:
        # Data akurasi untuk disimpan
        data = {
            "Nama Model": [model_name],
            "Data Latih": [round(train_accuracy, 2)],
            "Data Validasi": [round(val_accuracy, 2)],
            "Data Uji": [round(test_accuracy, 2)],
            "Rata-rata": [round((train_accuracy + val_accuracy + test_accuracy) / 3, 2)]
        }
        df = pd.DataFrame(data)
        
        # Jika file CSV sudah ada, tambahkan data baru tanpa duplikasi
        if os.path.exists(ACCURACY_CSV_PATH):
            existing_df = pd.read_csv(ACCURACY_CSV_PATH)
            # Hapus entri lama untuk model dengan nama yang sama
            existing_df = existing_df[existing_df["Nama Model"] != model_name]
            # Tambahkan data baru
            df = pd.concat([existing_df, df], ignore_index=True)
        # Simpan ke CSV dan ditampilkan di Akurasi Sistem
        df.to_csv(ACCURACY_CSV_PATH, index=False)
        st.success(f"Akurasi model {model_name} tersimpan di **Akurasi Sistem**")
    except Exception as e:
        st.error(f"Gagal menyimpan akurasi ke CSV: {str(e)}")

# Fungsi untuk melatih model baru
def train_new_model(train_path, validation_path, test_path, model_save_path, epochs=10, batch_size=32, dense_nodes=256, dropout_rates=0.0, learning_rate=0.001, use_two_layers=False):
    try:
        # Normalisasi path untuk kompatibilitas lintas platform
        train_path = os.path.normpath(train_path)
        validation_path = os.path.normpath(validation_path)
        test_path = os.path.normpath(test_path)

        # Data generator untuk augmentasi
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest'
        )

        validation_datagen = ImageDataGenerator(rescale=1./255)
        test_datagen = ImageDataGenerator(rescale=1./255)

        # Load dataset
        train_generator = train_datagen.flow_from_directory(
            train_path,
            target_size=(299, 299),
            batch_size=batch_size,
            class_mode='categorical',
            classes=['segar', 'tidak segar'],
            shuffle=True  # Aktifkan shuffle untuk pelatihan
        )

        validation_generator = validation_datagen.flow_from_directory(
            validation_path,
            target_size=(299, 299),
            batch_size=batch_size,
            class_mode='categorical',
            classes=['segar', 'tidak segar'],
            shuffle=False
        )

        test_generator = test_datagen.flow_from_directory(
            test_path,
            target_size=(299, 299),
            batch_size=batch_size,
            class_mode='categorical',
            classes=['segar', 'tidak segar'],
            shuffle=False
        )

        # Buat model InceptionV3 dengan arsitektur baru
        base_model = InceptionV3(weights='imagenet', include_top=False, input_shape=(299, 299, 3))
        x = base_model.output
        x = GlobalAveragePooling2D(name='global_average_pooling2d')(x)
        x = BatchNormalization()(x)
        x = Dense(dense_nodes[0] if use_two_layers else dense_nodes, activation='relu')(x)
        if use_two_layers and dropout_rates[0] > 0.0:
            x = Dropout(dropout_rates[0])(x)
        if use_two_layers:
            x = BatchNormalization()(x)
            x = Dense(dense_nodes[1], activation='relu')(x)
            if dropout_rates[1] > 0.0:
                x = Dropout(dropout_rates[1])(x)
        else:
            if dropout_rates > 0.0:
                x = Dropout(dropout_rates)(x)
        outputs = Dense(2, activation='softmax')(x)
        model = Model(inputs=base_model.input, outputs=outputs)

        # Bekukan lapisan base model
        for layer in base_model.layers:
            layer.trainable = False

        # Kompilasi model dengan learning rate yang dipilih
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate), 
                     loss='categorical_crossentropy', 
                     metrics=['accuracy'])

        # Latih model
        with st.spinner("Melatih model CNN..."):
            history = model.fit(
                train_generator,
                epochs=epochs,
                validation_data=validation_generator,
                verbose=1
            )

        # Ambil akurasi dan loss dari pelatihan
        train_accuracy = history.history['accuracy'][-1] * 100
        train_loss = history.history['loss'][-1]
        val_accuracy = history.history['val_accuracy'][-1] * 100
        val_loss = history.history['val_loss'][-1]

        # Evaluasi model pada data uji
        with st.spinner("Mengevaluasi model pada data uji..."):
            test_loss, test_accuracy = model.evaluate(test_generator, verbose=0)
            test_accuracy = test_accuracy * 100

        # Hitung rata-rata akurasi
        avg_accuracy = (train_accuracy + val_accuracy + test_accuracy) / 3

        # Hitung confusion matrix setelah pelatihan
        with st.spinner("Menghitung confusion matrix..."):
            # Buat generator baru untuk data latih dengan shuffle=False untuk evaluasi
            train_eval_generator = train_datagen.flow_from_directory(
                train_path,
                target_size=(299, 299),
                batch_size=batch_size,
                class_mode='categorical',
                classes=['segar', 'tidak segar'],
                shuffle=False
            )
            train_cm = compute_confusion_matrix(model, train_eval_generator)
            val_cm = compute_confusion_matrix(model, validation_generator)
            test_cm = compute_confusion_matrix(model, test_generator)

        # Tampilkan hasil akurasi dalam format persen
        st.write("**Hasil Akurasi Pelatihan Model:**")
        st.markdown(f"""
        <div class="confidence-box">
            <div class="confidence-item"><b>Data Latih</b>: {train_accuracy:.2f}%</div>
            <div class="confidence-item"><b>Data Validasi</b>: {val_accuracy:.2f}%</div>
            <div class="confidence-item"><b>Data Uji</b>: {test_accuracy:.2f}%</div>
            <div class="confidence-item"><b>Rata-rata</b>: {avg_accuracy:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

        # Tampilkan confusion matrix sebagai heatmap
        st.write("**Confusion Matrix:**")
        
        st.write("**Data Latih:**")
        fig_train = plot_confusion_matrix(train_cm, "Confusion Matrix - Data Latih")
        st.pyplot(fig_train)
        plt.close(fig_train)
        
        st.write("**Data Validasi:**")
        fig_val = plot_confusion_matrix(val_cm, "Confusion Matrix - Data Validasi")
        st.pyplot(fig_val)
        plt.close(fig_val)
        
        st.write("**Data Uji:**")
        fig_test = plot_confusion_matrix(test_cm, "Confusion Matrix - Data Uji")
        st.pyplot(fig_test)
        plt.close(fig_test)

        # Simpan model
        os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
        model.save(model_save_path)
        #st.success(f"Model CNN tersimpan di: {model_save_path}")

        # Simpan akurasi ke CSV
        model_name = os.path.splitext(os.path.basename(model_save_path))[0]
        save_accuracy_to_csv(model_name, train_accuracy, val_accuracy, test_accuracy)

        # Perbarui MODEL_OPTIONS di session state
        st.session_state.MODEL_OPTIONS = get_model_options()
        st.success("Model baru telah ditambahkan ke pilihan model di **Klasifikasi Dengan Model Tersimpan**")

        return True
    except Exception as e:
        st.error(f"Error saat melatih model: {str(e)}")
        return False

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
        
        /* Style untuk subjudul */
        h3 {
            color: #E91E63 !important;
            text-align: center !important;
            font-size: 18px !important;
            margin-top: 1em !important;
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
    st.markdown('<div class="big-title">LATIH MODEL BARU KLASIFIKASI KESEGARAN DAGING SAPI</div>', unsafe_allow_html=True)

    # Buat tab
    tab1, tab2 = st.tabs(["Latih Model Baru", "Akurasi Model Baru"])

    with tab1:
        st.warning("""
        **Masukkan path folder untuk data latih, validasi, dan uji dengan ketentuan berikut:**\n 
        1. **Salin path** dari direktori lokal (misalnya, file explorer di windows: klik kanan folder → 'Copy as path')\n
        2. Setiap folder harus memiliki subfolder **segar** dan **tidak segar** yang berisi gambar (.jpg, .jpeg, .png)
        """)
        
        # Input path folder
        train_path = st.text_input(
            "Path folder data latih:",
            placeholder="C:/dataset/data latih",
            key="train_path_input",
            help="Salin path dari File Explorer (klik kanan folder → 'Copy as path')"
        )
        validation_path = st.text_input(
            "Path folder data validasi:",
            placeholder="C:/dataset/data validasi",
            key="validation_path_input",
            help="Salin path dari File Explorer (klik kanan folder → 'Copy as path')"
        )
        test_path = st.text_input(
            "Path folder data uji:",
            placeholder="C:/dataset/data uji",
            key="test_path_input",
            help="Salin path dari File Explorer (klik kanan folder → 'Copy as path')"
        )
        model_name = st.text_input("Nama model baru:", placeholder="nama model", help="Tentukan nama model yang akan disimpan")
        epochs = st.slider("Jumlah epoch:", min_value=1, max_value=20, value=10)
        layer_choice = st.selectbox("Jumlah lapisan dense:", ["1 Layer", "2 Layer"], index=0, help="Pilih 1 atau 2 layer")
        if layer_choice == "1 Layer":
            dense_nodes = st.selectbox("Jumlah node di lapisan dense:", [32, 64, 128, 256, 512, 1024], index=0)
            dropout_rates = st.selectbox("Dropout rate:", [0.0, 0.2, 0.3, 0.5, 0.7], 
                                        index=0, 
                                        help="Pilih 0.0 untuk tanpa dropout")
        else:
            dense_nodes = st.selectbox("Jumlah node di lapisan dense (Layer 1, Layer 2):", 
                                      [(128, 64), (256, 128), (512, 256), (1024, 512)], 
                                      format_func=lambda x: f"{x[0]} dan {x[1]}",
                                      index=0)
            dropout_rate_1 = st.selectbox("Dropout rate (Layer 1):", [0.0, 0.2, 0.3, 0.5, 0.7], 
                                         index=0, 
                                         help="Pilih 0.0 untuk tanpa dropout pada Layer 1")
            dropout_rate_2 = st.selectbox("Dropout rate (Layer 2):", [0.0, 0.2, 0.3, 0.5, 0.7], 
                                         index=0, 
                                         help="Pilih 0.0 untuk tanpa dropout pada Layer 2")
            dropout_rates = (dropout_rate_1, dropout_rate_2)
        learning_rate = st.selectbox("Learning rate:", [0.01, 0.001, 0.0001], 
                                    index=0, 
                                    help="Learning rate untuk optimizer Adam")
        
        if train_path and validation_path and test_path and model_name:
            # Validasi struktur direktori
            try:
                for path, name in [(train_path, "latih"), (validation_path, "validasi"), (test_path, "uji")]:
                    path = os.path.normpath(path)
                    if not os.path.exists(path):
                        st.error(f"Folder {name} tidak ditemukan di: {path}")
                        return
                    if not all(os.path.exists(os.path.join(path, c)) for c in ['segar', 'tidak segar']):
                        st.error(f"Folder **segar** dan **tidak segar** harus ada di dalam folder {name}.")
                        return
                    # Validasi bahwa folder berisi gambar
                    for subfolder in ['segar', 'tidak segar']:
                        subfolder_path = os.path.join(path, subfolder)
                        images = [f for f in os.listdir(subfolder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                        if not images:
                            st.error(f"Folder {subfolder} di {name} tidak berisi gambar (.jpg, .jpeg, .png).")
                            return

                model_save_path = os.path.join(MODEL_FOLDER, f"{model_name}.h5")
                
                st.markdown('<div class="center-button">', unsafe_allow_html=True)
                if st.button("Mulai Pelatihan", help="Latih model baru dengan dataset", type="primary", key="train_tab2"):
                    with st.spinner("Memproses dataset dan melatih model..."):
                        if train_new_model(
                            train_path=train_path,
                            validation_path=validation_path,
                            test_path=test_path,
                            model_save_path=model_save_path,
                            epochs=epochs,
                            dense_nodes=dense_nodes,
                            dropout_rates=dropout_rates,
                            learning_rate=learning_rate,
                            use_two_layers=(layer_choice == "2 Layer")
                        ):
                            st.success(f"Pelatihan selesai! Model baru berhasil tersimpan")
                        else:
                            st.error("Pelatihan gagal. Periksa dataset dan coba lagi.")
            except Exception as e:
                st.error(f"Error saat memproses direktori dataset: {str(e)}")

    # Tab 2: Latih Model Baru
    with tab2:
        st.markdown("<h3>HASIL AKURASI LATIH MODEL BARU</h3>", unsafe_allow_html=True)
        # Baca data akurasi dari CSV
        try:
            data_model_baru = pd.read_csv('model_accuracies.csv')
            if data_model_baru.empty:
                st.info("Belum ada data akurasi untuk model baru. Latih model baru terlebih dahulu di Tab 'Latih Model Baru'.")
            else:
                st.dataframe(data_model_baru, use_container_width=True)
                st.line_chart(data_model_baru.set_index("Nama Model"))
        except FileNotFoundError:
            st.info("Belum ada data akurasi untuk model baru. Latih model baru terlebih dahulu di Tab 'Latih Model Baru'.")
        except Exception as e:
            st.error(f"Gagal memuat data akurasi model baru: {str(e)}")

    # Copyright
    st.markdown("""
    <div class="copyright-container">
        <p>© 2025 FreshPi - Sistem Klasifikasi Kesegaran Daging Sapi. All Rights Reserved.</p>
    </div>
    """, unsafe_allow_html=True)

# Jalankan aplikasi
if __name__ == "__main__":
    render()