import streamlit as st
import requests
from PIL import Image
import io
from streamlit_image_comparison import image_comparison
import numpy as np
import base64
import requests

# -- Page config
st.set_page_config(page_title="Deblurify", layout="centered")

# -- Header / Navbar
st.markdown("""
    <div style="position: fixed; top: 0; left: 0; width: 100%; background-color: #f0f2f6; padding: 10px 20px; z-index: 9999; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <h2 style="margin: 0; color: #0066cc;">Deblurify</h2>
    </div>
    <div style="height: 60px;"></div> 
""", unsafe_allow_html=True)

# -- API URL
API_URL = "https://de10-34-124-231-121.ngrok-free.app/deblur"  # Zamijeni ako treba

# -- Title and subtitle
st.markdown("<h1 style='text-align: center;'>Welcome to our app!</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'><em>Enhancing your blurred images with Autoencoders</em></h3>", unsafe_allow_html=True)
st.markdown("---")

# -- Gallery state
if "gallery" not in st.session_state:
    st.session_state.gallery = []

# -- Upload image
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

def generate_download_link(img, filename="deblurred.png"):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    b64 = base64.b64encode(img_bytes).decode()
    href = f'<a href="data:file/png;base64,{b64}" download="{filename}">Download image</a>'
    return href

st.markdown("""
<style>
div.stButton {
    display: flex;
    justify-content: center;
    margin-top: 20px;
    margin-bottom: 20px;
}
div.stButton > button:first-child {
    background-color: #0066cc !important;  
    color: white !important;
    height: 50px;
    width: 200px;
    border-radius: 10px;
    font-size: 18px;
    font-weight: normal;
    border: none;
    cursor: pointer;
    transition: background-color 0.3s ease, font-weight 0.2s ease, box-shadow 0.2s ease;
}
div.stButton > button:first-child:hover {
    background-color: #004a99 !important;  
}
div.stButton > button:first-child:focus,
div.stButton > button:first-child:active {
    outline: none !important;
    background-color: #0066cc !important;  
    color: white !important;                
    font-weight: bold !important;            
    box-shadow: 0 0 8px rgba(0, 102, 204, 0.7) !important; 
}
</style>
""", unsafe_allow_html=True)

# -- Main logic
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Original image", use_container_width=True)

    if st.button("Run deblur"):
        with st.spinner("Processing your image..."):
            response = requests.post(
                API_URL,
                files={"image": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            )

            if response.status_code == 200:
                output_img = Image.open(io.BytesIO(response.content))
                output_img = output_img.resize(image.size)
                #psnr_header = response.headers.get("X-Image-PSNR")

                # Container for comparison and PSNR
                st.markdown("<div style='max-width: 256px; margin-left: auto; margin-right: auto;'>", unsafe_allow_html=True)

                st.markdown("### Before / After")
                image_comparison(img1=image, img2=output_img, label1="Before", label2="After")

                st.markdown("<p style='text-align: center; color: #888;'>Sharper images. Instant results.</p>", unsafe_allow_html=True)

                similarity = response.headers.get("X-Image-Similarity")
                if similarity:
                    try:
                        percent = float(similarity)
                        st.success(f"Image similarity: {percent:.2f}%")
                    except:
                        st.warning("Could not parse similarity.")

                # Download link
                st.markdown(
                    f"""
                    <div style="text-align: center; margin-top: 10px;">
                        {generate_download_link(output_img)}
                    </div>
                    """,
                    unsafe_allow_html=True)

                st.toast("Image processed successfully!")
                st.session_state.gallery.append((image.copy(), output_img.copy()))
            else:
                st.error("Error processing the image.")

# -- Gallery in horizontal layout (grid)
if st.session_state.gallery:
    st.markdown("---")
    st.markdown("## Previous results")

    num_cols = 3  # broj kolona u jednom redu
    rows = (len(st.session_state.gallery) + num_cols - 1) // num_cols

    for row in range(rows):
        cols = st.columns(num_cols)
        for col in range(num_cols):
            idx = row * num_cols + col
            if idx < len(st.session_state.gallery):
                before, after = st.session_state.gallery[idx]
                with cols[col]:
                    st.markdown(f"**Image {idx + 1}**", unsafe_allow_html=True)
                    st.image(before, caption="Original", width=200)
                    st.image(after, caption="Deblurred", width=200)

# -- Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>© 2025 Alma, Naida & Lana – Deblurify</div>", unsafe_allow_html=True)