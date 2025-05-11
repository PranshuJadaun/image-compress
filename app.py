import streamlit as st
from PIL import Image
import io

st.set_page_config(
    page_title="Image Compressor & Resizer",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("📷 Image Compressor & Resizer")
st.markdown(
    "Upload an image, choose the desired dimensions and compression quality, then download the optimized image securely."
)

# Sidebar controls
st.sidebar.header("Resize & Compression Settings")
width = st.sidebar.number_input(
    "Width (px)", min_value=1, value=800, step=1
)
height = st.sidebar.number_input(
    "Height (px)", min_value=1, value=600, step=1
)
quality = st.sidebar.slider(
    "JPEG Quality", min_value=10, max_value=100, value=85,
    help="Lower quality reduces file size but may affect image clarity."
)
output_format = st.sidebar.selectbox(
    "Output Format", options=["JPEG", "PNG"], index=0
)

# Globals for cleanup
buffer = None
uploaded_file = None

# Cleanup function to remove sensitive data
def clear_sensitive():
    global buffer, uploaded_file
    # Close buffers/files
    if buffer:
        try:
            buffer.close()
        except Exception:
            pass
    if uploaded_file:
        try:
            uploaded_file.close()
        except Exception:
            pass
    # Clear session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    # Stop further execution
    st.stop()

# File uploader
uploaded_file = st.file_uploader(
    "Choose an image (JPEG, PNG)", type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    # Open image
    image = Image.open(uploaded_file)
    st.subheader("Original Image")
    st.image(image, use_column_width=True)

    # Determine resampling filter
    try:
        resample_filter = Image.Resampling.LANCZOS
    except AttributeError:
        resample_filter = Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.ANTIALIAS

    # Resize image
    resized_img = image.resize((width, height), resample_filter)
    st.subheader("Resized Preview")
    st.image(resized_img, use_column_width=True)

    # Prepare in-memory buffer
    buffer = io.BytesIO()
    fmt = output_format.upper()

    if fmt == "PNG":
        resized_img.save(buffer, format="PNG", optimize=True)
        mime = "image/png"
        ext = "png"
    else:
        # Handle transparency for JPEG
        if resized_img.mode in ("RGBA", "LA"):
            bg = Image.new("RGB", resized_img.size, (255, 255, 255))
            bg.paste(resized_img, mask=resized_img.split()[3])
            save_img = bg
        else:
            save_img = resized_img.convert("RGB")
        save_img.save(buffer, format="JPEG", quality=quality, optimize=True)
        mime = "image/jpeg"
        ext = "jpg"

    buffer.seek(0)

    # Download button with cleanup
    st.download_button(
        label=f"Download {width}×{height} {fmt}",
        data=buffer,
        file_name=f"resized_{width}x{height}.{ext}",
        mime=mime,
        on_click=clear_sensitive
    )
else:
    st.info("📂 Please upload an image to get started.")