import streamlit as st
import numpy as np
import base64
import hashlib
import time
from PIL import Image
from io import BytesIO
import requests
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from data_wayang import tokoh_wayang

st.set_page_config(page_title="Klasifikasi", layout="centered")

# CSS sembunyikan sidebar
hide_sidebar = """
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

# Fungsi konversi gambar ke base64
def image_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Fungsi hash unik gambar
def get_image_hash(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return hashlib.md5(buffered.getvalue()).hexdigest()

# Label keyakinan
def label_keyakinan(confidence):
    if confidence <= 60:
        return "Tidak Yakin"
    elif 61 <= confidence <= 79:
        return "Cukup Yakin"
    elif 80 <= confidence <= 90:
        return "Yakin"
    else:
        return "Sangat Yakin"

# Cek jika belum ada gambar
if 'image_uploaded' not in st.session_state and 'image_url' not in st.session_state:
    st.warning("⚠️ Belum ada gambar yang dipilih atau URL yang dimasukkan!")
    st.markdown('<meta http-equiv="refresh" content="2; url=/" />', unsafe_allow_html=True)
    st.stop()

# Ambil gambar
if 'image_uploaded' in st.session_state:
    image = st.session_state['image_uploaded']
elif 'image_url' in st.session_state:
    url = st.session_state['image_url']
    try:
        image = Image.open(requests.get(url, stream=True).raw).convert("RGB")
    except:
        st.error("Gagal memuat gambar dari URL")
        st.stop()

# Reset model_loaded jika gambar baru
if st.session_state.get("last_image_hash") != get_image_hash(image):
    st.session_state["model_loaded"] = False
    st.session_state["last_image_hash"] = get_image_hash(image)

if "model_loaded" not in st.session_state:
    st.session_state["model_loaded"] = False

# Tampilkan gambar
img_base64 = image_to_base64(image)
st.markdown(
    f"""
    <div style="display: flex; flex-direction: column; align-items: center; margin-top: 5px;">
        <img src="data:image/png;base64,{img_base64}" width="300" style="border: 2px solid #ccc; border-radius: 10px; margin-bottom: 15px;">
    </div>
    """,
    unsafe_allow_html=True
)

# Placeholder loading
loading_placeholder = st.empty()
if not st.session_state["model_loaded"]:
    loading_placeholder.markdown(
        "<p style='text-align:center;'>🧠 Sebentar ya... sistemnya lagi nyari jawabannya!</p>",
        unsafe_allow_html=True
    )

# LOAD MODEL TANPA RELOAD
@st.cache_resource
def load_cnn():
    return load_model('best_model1__MobilenetV2wayang.keras')

model = load_cnn()

class_names = [
    'anoman', 'arjuna', 'bagong', 'bima', 'gareng',
    'gatotkaca', 'kresna', 'petruk', 'puntadewa', 'semar'
]

# Preprocessing
image_resized = image.resize((224, 224))
img_array = img_to_array(image_resized)
img_array = preprocess_input(img_array)
img_array = np.expand_dims(img_array, axis=0)

# START TIMER 
start_time = time.time()
prediction = model.predict(img_array)
end_time = time.time()
# END TIMER

# Hitung waktu inferensi (ms)
inference_time = (end_time - start_time) * 1000

# Hasil prediksi
pred_index = np.argmax(prediction)
confidence = np.max(prediction) * 100
predicted_class = class_names[pred_index]
status_keyakinan = label_keyakinan(confidence)

# Model selesai diload
st.session_state["model_loaded"] = True
loading_placeholder.empty()

# Tampilkan hasil
if confidence <= 60:
    st.markdown(
        """
        <div style='display: flex; justify-content: center;'>
            <div style='max-width: 300px; text-align: center; background-color: #fff3cd; border: 1px solid #ffeeba; border-radius: 5px; padding: 12px; color: #856404;'>
                ⚠️ Hmm... gambar ini belum dikenali. Coba pakai gambar lain, yuk!
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        f"<p style='text-align: center; margin-top: 10px;'>🧪 Model {status_keyakinan.lower()} ({confidence:.2f}%)</p>",
        unsafe_allow_html=True
    )

else:
    info = tokoh_wayang[predicted_class]

    st.markdown(f"<h4 style='text-align: center; margin-bottom: 10px;'><b>{info['nama_wayang']}</b></h4>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='text-align: center; font-size: 16px;'>🔍 Model <b>{status_keyakinan}</b> ({confidence:.2f}%)</p>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div style="display: table; margin: 0 auto; font-size: 16px; line-height: 1.7;">
            <div style="display: table-row;">
                <div style="display: table-cell; padding-right: 10px; font-weight: bold;">Nama Panggilan</div>
                <div style="display: table-cell; padding-right: 5px;">:</div>
                <div style="display: table-cell;">{info['nama_panggilan']}</div>
            </div>
            <div style="display: table-row;">
                <div style="display: table-cell; padding-right: 10px; font-weight: bold;">Nama Kecil</div>
                <div style="display: table-cell; padding-right: 5px;">:</div>
                <div style="display: table-cell;">{info['nama_kecil']}</div>
            </div>
            <div style="display: table-row;">
                <div style="display: table-cell; padding-right: 10px; font-weight: bold;">Nama Gelar</div>
                <div style="display: table-cell; padding-right: 5px;">:</div>
                <div style="display: table-cell;">{info['nama_gelar']}</div>
            </div>
            <div style="display: table-row; vertical-align: top;">
                <div style="display: table-cell; padding-right: 10px; font-weight: bold;">Deskripsi</div>
                <div style="display: table-cell; padding-right: 5px;">:</div>
                <div style="display: table-cell; max-width: 550px; text-align: justify;">{info['deskripsi']}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Tampilkan waktu inferensi 
st.markdown(
    f"<p style='text-align:center; margin-top:5px; font-size:15px; color:#666;'>⏱️ Waktu Prediksi: <b>{inference_time:.2f} ms</b></p>",
    unsafe_allow_html=True
)

# Tombol Kembali ke Beranda
col1, col2, col3 = st.columns([1.3, 1.7, 1])
with col2:
    if st.button("🔁 Masih penasaran? Balik yuk!"):
        st.switch_page("main.py")
