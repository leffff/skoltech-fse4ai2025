import os
import requests
import streamlit as st
from PIL import Image

# Page config
st.set_page_config(
    page_title="BLIP Image Captioning",
    page_icon="📝",
    layout="wide"
)

def main():
    st.title("📝 BLIP Image Captioning")

    # Sidebar settings
    st.sidebar.title("⚙️ Settings")
    default_backend = os.getenv("BACKEND_URL", "http://localhost:8000")
    api_url = st.sidebar.text_input("Backend API URL", value=default_backend)

    # Caption generation parameters
    max_length = st.sidebar.slider("Max Caption Length", min_value=10, max_value=150, value=100)
    num_beams = st.sidebar.slider("Number of Beams", min_value=1, max_value=10, value=5)

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload an image (JPG, PNG, BMP, TIFF, WEBP)",
        type=["jpg", "jpeg", "png", "bmp", "tiff", "webp"]
    )

    if uploaded_file is not None:
        # Display uploaded image once
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        if st.button("Generate Caption", type="primary"):
            with st.spinner("Generating caption..."):
                try:
                    # Health check
                    health_resp = requests.get(f"{api_url}/health", timeout=10)
                    if health_resp.status_code != 200:
                        st.error("❌ Backend is unhealthy. Check logs.")
                        return

                    # Send image to backend
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(
                        f"{api_url}/caption/",
                        files=files,
                        params={"max_length": max_length, "num_beams": num_beams},
                        timeout=60
                    )

                    if response.status_code == 200:
                        result = response.json()
                        caption = result["caption"]

                        st.subheader("Generated Caption")
                        st.success(f'**"{caption}"**')

                        # Optional: show generation params
                        with st.expander("📊 Generation Parameters"):
                            st.json(result["parameters"])

                    else:
                        error_detail = response.json().get("detail", "Unknown error")
                        st.error(f"❌ Failed to generate caption: {error_detail}")

                except requests.exceptions.ConnectionError:
                    st.error(
                        "❌ Cannot connect to backend.\n\n"
                        "**Tips:**\n"
                        "- In Docker: use `http://backend:8000`\n"
                        "- Locally: ensure backend runs on `http://localhost:8000`\n"
                        "- Check `docker-compose logs backend`"
                    )
                except requests.exceptions.Timeout:
                    st.error("⏰ Request timed out. The model may still be loading or processing.")
                except Exception as e:
                    st.error(f"💥 Unexpected error: {str(e)}")

    # Backend status indicator
    st.sidebar.markdown("### 🌐 Backend Status")
    try:
        status = requests.get(f"{api_url}/health", timeout=5)
        if status.status_code == 200:
            st.sidebar.success("✅ Healthy")
        else:
            st.sidebar.error("❌ Unhealthy")
    except:
        st.sidebar.error("❌ Offline")

    # Help section
    with st.expander("📖 Help & Tips"):
        st.markdown("""
        ### How to Use
        1. Upload an image.
        2. Adjust caption length if needed (default: 100 tokens).
        3. Click **Generate Caption**.

        ### Notes
        - First run may take 1–2 minutes (model download).
        - Captions are longer by default now (up to 150 tokens).
        - The image is shown only once—no duplicate display.

        ### Docker vs Local
        - **Docker**: Backend URL = `http://backend:8000`
        - **Local**: Backend URL = `http://localhost:8000`
        """)

if __name__ == "__main__":
    main()