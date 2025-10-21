from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch
from PIL import Image
import io
import base64
import os
from datetime import datetime

app = FastAPI(title="BLIP Image Captioning API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize BLIP model and processor
processor = None
model = None


def load_blip_model():
    """Load BLIP model from Hugging Face"""
    global processor, model

    try:
        print("Loading BLIP model...")

        # Load processor and model
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

        # Use GPU if available
        if torch.cuda.is_available():
            model = model.to('cuda')
            print("BLIP model loaded on GPU")
        else:
            print("BLIP model loaded on CPU")

        print("BLIP model loaded successfully!")
        return True

    except Exception as e:
        print(f"Error loading BLIP model: {e}")
        return False


# Load model on startup
model_loaded = load_blip_model()


def validate_image_file(file: UploadFile) -> bool:
    """Validate that the uploaded file is actually an image"""
    # Check filename extension
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    file_extension = os.path.splitext(file.filename.lower())[1]

    if file_extension not in allowed_extensions:
        return False

    return True


def validate_image_content(image_data: bytes) -> bool:
    """Validate that the file content is actually an image"""
    try:
        image = Image.open(io.BytesIO(image_data))
        image.verify()  # Verify that it is, in fact, an image
        return True
    except Exception:
        return False


@app.get("/")
async def root():
    return {"message": "BLIP Image Captioning API"}


@app.get("/health")
async def health_check():
    """Enhanced health check that verifies model is actually loaded"""
    if model is None or processor is None:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": "BLIP model not loaded"}
        )

    # Test model with a simple operation
    try:
        # Create a small test image
        test_image = Image.new('RGB', (10, 10), color='red')
        inputs = processor(test_image, return_tensors="pt")

        # Quick test generation
        with torch.no_grad():
            _ = model.generate(**inputs, max_length=5, num_beams=1)

        return {
            "status": "healthy",
            "model_loaded": True,
            "device": "cuda" if torch.cuda.is_available() else "cpu"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": f"Model test failed: {str(e)}"}
        )


@app.get("/model-info")
async def model_info():
    """Endpoint to check model information"""
    if model is None:
        return {"error": "Model not loaded"}

    return {
        "model_name": "Salesforce/blip-image-captioning-base",
        "model_type": "BLIP",
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "status": "loaded"
    }


@app.post("/caption/")
async def generate_caption(file: UploadFile = File(...), max_length: int = 50, num_beams: int = 5):
    """Generate caption for uploaded image"""
    if model is None or processor is None:
        raise HTTPException(status_code=500, detail="BLIP model not loaded")

    try:
        print(f"Received file: {file.filename}, Content-Type: {file.content_type}")

        # ✅ FIXED: Use multiple validation methods
        # 1. Check filename extension
        if not validate_image_file(file):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: JPG, JPEG, PNG, BMP, TIFF, WEBP"
            )

        # Read image data
        image_data = await file.read()

        # 2. Check file content to ensure it's actually an image
        if not validate_image_content(image_data):
            raise HTTPException(
                status_code=400,
                detail="File content is not a valid image"
            )

        # Reset file pointer after reading
        image = Image.open(io.BytesIO(image_data))

        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Preprocess image
        inputs = processor(image, return_tensors="pt")

        # Use GPU if available
        if torch.cuda.is_available():
            inputs = {k: v.to('cuda') for k, v in inputs.items()}

        # Generate caption
        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_length=max_length,
                num_beams=num_beams,
                early_stopping=True
            )

        # Decode caption
        caption = processor.decode(output[0], skip_special_tokens=True)

        # Convert image to base64 for response
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        image_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return JSONResponse(content={
            "caption": caption,
            "processed_image": image_b64,
            "model_used": "Salesforce/blip-image-captioning-base",
            "parameters": {
                "max_length": max_length,
                "num_beams": num_beams
            }
        })

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@app.post("/caption-detailed/")
async def generate_detailed_caption(
        file: UploadFile = File(...),
        max_length: int = 50,
        num_beams: int = 5,
        temperature: float = 1.0,
        do_sample: bool = False
):
    """Generate caption with more parameters"""
    if model is None or processor is None:
        raise HTTPException(status_code=500, detail="BLIP model not loaded")

    try:
        print(f"Received file: {file.filename}, Content-Type: {file.content_type}")

        # ✅ FIXED: Use multiple validation methods
        if not validate_image_file(file):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: JPG, JPEG, PNG, BMP, TIFF, WEBP"
            )

        # Read image data
        image_data = await file.read()

        if not validate_image_content(image_data):
            raise HTTPException(
                status_code=400,
                detail="File content is not a valid image"
            )

        image = Image.open(io.BytesIO(image_data))

        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Preprocess image
        inputs = processor(image, return_tensors="pt")

        # Use GPU if available
        if torch.cuda.is_available():
            inputs = {k: v.to('cuda') for k, v in inputs.items()}

        # Generate caption with more parameters
        with torch.no_grad():
            if do_sample:
                output = model.generate(
                    **inputs,
                    max_length=max_length,
                    num_beams=num_beams,
                    temperature=temperature,
                    do_sample=do_sample,
                    early_stopping=True
                )
            else:
                output = model.generate(
                    **inputs,
                    max_length=max_length,
                    num_beams=num_beams,
                    early_stopping=True
                )

        caption = processor.decode(output[0], skip_special_tokens=True)

        # Convert image to base64
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        image_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return JSONResponse(content={
            "caption": caption,
            "processed_image": image_b64,
            "model_used": "Salesforce/blip-image-captioning-base",
            "parameters": {
                "max_length": max_length,
                "num_beams": num_beams,
                "temperature": temperature,
                "do_sample": do_sample
            }
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)