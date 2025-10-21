import streamlit as st
import requests
import base64
from PIL import Image
import io
import os

st.set_page_config(
    page_title="BLIP Image Captioning",
    page_icon="📝",
    layout="wide"
)


def main():
    st.title("📝 BLIP Image Captioning")

    # Sidebar - Use environment variable for backend URL in Docker
    st.sidebar.title("Settings")

    # In Docker, backend service is accessible via service name 'backend'
    # For local development, fall back to localhost
    default_backend = os.getenv('BACKEND_URL', 'http://localhost:8000')
    api_url = st.sidebar.text_input("Backend API URL", default_backend)

    max_length = st.sidebar.slider("Max Caption Length", 10, 100, 50)
    num_beams = st.sidebar.slider("Number of Beams", 1, 10, 5)

    # File upload
    uploaded_file = st.file_uploader(
        "Choose an image...",
        type=['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'webp']
    )

    col1, col2 = st.columns(2)

    with col1:
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)

            if st.button("Generate Caption", type="primary"):
                with st.spinner("Generating caption..."):
                    try:
                        # Test backend connection first
                        st.info("Testing backend connection...")
                        health_response = requests.get(f"{api_url}/health", timeout=10)

                        if health_response.status_code == 200:
                            st.success("✅ Backend connected successfully!")
                        else:
                            st.error(f"❌ Backend health check failed: {health_response.status_code}")
                            return

                        # Prepare the file for upload
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}

                        st.info("🔄 Generating caption... This may take a moment.")
                        response = requests.post(
                            f"{api_url}/caption/",
                            files=files,
                            params={"max_length": max_length, "num_beams": num_beams},
                            timeout=60  # Increased timeout for model processing
                        )

                        if response.status_code == 200:
                            result = response.json()

                            with col2:
                                st.subheader("Results")

                                # Display processed image
                                processed_image_data = base64.b64decode(result["processed_image"])
                                processed_image = Image.open(io.BytesIO(processed_image_data))
                                st.image(processed_image, caption="Processed Image", use_column_width=True)

                                # Display caption
                                st.subheader("Generated Caption:")
                                st.success(f'**"{result["caption"]}"**')

                                # Show model info
                                with st.expander("📊 Model Information"):
                                    st.json(result["parameters"])

                        else:
                            error_detail = response.json().get('detail', 'Unknown error')
                            st.error(f"❌ Caption generation failed: {error_detail}")

                    except requests.exceptions.ConnectionError:
                        st.error("""
                        ❌ Cannot connect to backend service. 

                        **Troubleshooting steps:**
                        1. Make sure the backend is running
                        2. Check if the backend URL is correct
                        3. In Docker, use 'http://backend:8000' as the backend URL
                        4. Check Docker logs: `docker-compose logs backend`
                        """)
                    except requests.exceptions.Timeout:
                        st.error(
                            "⏰ Request timed out. The backend might be processing a large image or loading the model.")
                    except Exception as e:
                        st.error(f"❌ Unexpected error: {str(e)}")

    # Display current backend status
    with st.sidebar:
        st.subheader("Backend Status")
        try:
            status_response = requests.get(f"{api_url}/health", timeout=5)
            if status_response.status_code == 200:
                st.success("✅ Backend is healthy")
            else:
                st.error("❌ Backend is not healthy")
        except:
            st.error("❌ Cannot reach backend")

    # Instructions
    with st.expander("📖 How to use & Troubleshooting"):
        st.markdown("""
        ### Usage:
        1. **Upload an image** (JPG, PNG, BMP, TIFF, WEBP)
        2. **Click 'Generate Caption'**
        3. **View the generated description**

        ### Troubleshooting:

        **If you see connection errors:**

        **Docker Environment:**
        - Backend URL should be: `http://backend:8000`
        - Run with: `docker-compose up --build`

        **Local Development:**
        - Backend URL should be: `http://localhost:8000`
        - Start backend first: `./run_backend.sh`
        - Then start frontend: `./run_frontend.sh`

        **First Time Setup:**
        - The first request might take 1-2 minutes to download the BLIP model
        - Subsequent requests will be faster
        - Check logs for detailed error information
        """)


if __name__ == "__main__":
    main()