import streamlit as st
from PIL import Image
import base64
from io import BytesIO
import requests

# Fungsi untuk base64
def image_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Konfigurasi halaman
st.set_page_config(page_title="Home", layout="centered")

# CSS untuk menyembunyikan sidebar
hide_sidebar = """
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

# Redirect jika sudah upload
if st.session_state.get("go_to_prediction"):
    st.session_state["go_to_prediction"] = False
    st.switch_page("D:\wayang_streamlit_app\pages\klasifikasi.py")  

# Logo
logo = Image.open("D:/wayang_streamlit_app/assets/naraclass.png")
logo_base64 = image_to_base64(logo)
st.markdown(
    f"""
    <div style="text-align: center; margin-bottom: -10px;">
        <img src="data:image/png;base64,{logo_base64}" width="140" style="border-radius: 50%;">
        <h3 style="margin-top: 10px;">🎭 Klasifikasi Karakter Wayang Kulit</h3>
    </div>
    """,
    unsafe_allow_html=True
)

# Deskripsi Aplikasi 
st.write("""
Aplikasi ini bisa bantu kamu mengenali karakter wayang kulit dari gambar yang diunggah.  
Karakter yang saat ini dikenali: Anoman, Arjuna, Bagong, Bima, Gareng, Gatotkaca, Kresna, Petruk, Puntadewa, dan Semar.

Yuk, upload gambar dari perangkat kamu atau tempelkan link gambar biar bisa langsung dikenali!
""")

# Upload
upload_method = st.selectbox("Pilih metode upload:", ["", "📁 Upload dari perangkat", "🌐 Masukkan URL gambar"])
image = None

# Upload dari perangkat
if upload_method == "📁 Upload dari perangkat":
    uploaded_file = st.file_uploader("Pilih gambar", type=["jpg", "jpeg", "png", "webp"])
    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")

# Upload dari URL
elif upload_method == "🌐 Masukkan URL gambar":
    image_url = st.text_input("📥 Tempel URL gambar online di sini (yang formatnya langsung gambar)")
    if image_url.strip():
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(image_url, headers=headers, timeout=2)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content)).convert("RGB")
            else:
                st.error("Gagal mengambil gambar dari URL.")
        except Exception as e:
            st.error(f"❌ Error: {e}")

file_size = None  # default

# Jika gambar berhasil dimuat
if image is not None:
    # Tampilkan ukuran file URL di atas kiri (hanya untuk URL) 
    if upload_method == "🌐 Masukkan URL gambar" and image_url.strip():
        file_size = "Unknown size"
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(image_url, headers=headers, timeout=5)
            if response.status_code == 200:
                size_bytes = len(response.content)
                if size_bytes < 1024:
                    file_size = f"{size_bytes} B"
                elif size_bytes < 1024*1024:
                    file_size = f"{size_bytes/1024:.2f} KB"
                else:
                    file_size = f"{size_bytes/(1024*1024):.2f} MB"
        except:
            pass

        # Menampilkan ukuran file (khusus URL)
        st.markdown(
            f"""
            <style>
                .file-size-text {{
                    color: #b3b3b3 !important;       
                    font-size: 14px !important;      
                    font-weight: normal !important;
                    padding-left: 15px !important;   
                    text-align: left !important;
                }}
            </style>

            <div class="file-size-text">
                {file_size}
            </div>
            """,
            unsafe_allow_html=True
        )

        
    # Tampilkan gambar
    img_base64 = image_to_base64(image)
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; margin-top: 20px;">
            <img src="data:image/png;base64,{img_base64}" width="300" style="border: 2px solid #ccc; border-radius: 10px;">
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Spasi antara gambar dan tombol
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    
    # Tombol di bawah gambar dan di tengah
    col1, col2, col3 = st.columns([1.05, 1, 0.95])
    with col2:
        # Tombol lihat hasil klasifikasi
        if st.button("👀 Yuk, lihat hasilnya!"):
            st.session_state['image_uploaded'] = image
            if upload_method == "🌐 Masukkan URL gambar":
                st.session_state['image_url'] = image_url
            st.session_state['go_to_prediction'] = True
            
            # rerun lalu langsung switch_page
            st.rerun()   

