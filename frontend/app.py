import streamlit as st
import requests
import base64
from PIL import Image
import io

st.set_page_config(
    page_title="BLIP Image Captioning",
    page_icon="📝",
    layout="wide"
)


def main():
    st.title("📝 BLIP Image Captioning")

    # Sidebar
    st.sidebar.title("Settings")
    api_url = st.sidebar.text_input("Backend API URL", "http://localhost:8000")
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
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "image/jpeg")}
                        response = requests.post(
                            f"{api_url}/caption/",
                            files=files,
                            params={"max_length": max_length, "num_beams": num_beams}
                        )

                        if response.status_code == 200:
                            result = response.json()

                            with col2:
                                st.subheader("Results")

                                # Display processed image
                                processed_image_data = base64.b64decode(result["processed_image"])
                                processed_image = Image.open(io.BytesIO(processed_image_data))
                                st.image(processed_image, caption="Processed Image", use_column_width=True)

                                # Display caption - SIMPLE VERSION with visible text
                                st.subheader("Generated Caption:")
                                st.info(f'"{result["caption"]}"')  # ✅ This will have visible text

                                st.success("Caption generated successfully!")
                        else:
                            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    # Instructions
    with st.expander("How to use"):
        st.markdown("""
        1. Upload an image
        2. Click 'Generate Caption'
        3. View the generated description
        """)


if __name__ == "__main__":
    main()