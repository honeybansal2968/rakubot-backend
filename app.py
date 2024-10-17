from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import base64
import io
from dotenv import load_dotenv
import numpy as np
import sys
import os
from PIL import Image

# Get the current directory and the path to the parent directory
# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.dirname(current_dir)

# Add the parent directory to the Python path
# sys.path.append(parent_dir)

# Import your modules
import Voice_to_Text
import Data_Recommendation
import Gemini_API

# Initialize FastAPI
app = FastAPI()

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict it by specifying allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()
api_key = os.getenv('API_KEY')

# Start chat using the Gemini API
Gemini_API.Start_a_Chat(api_key)

# Define the directory to save images
SAVE_DIR = 'saved_images'
os.makedirs(SAVE_DIR, exist_ok=True)

# Routes

@app.get("/")
async def home():
    return {"message": "Hello There"}

@app.get("/voice_input")
async def voice(text: str):
    # Return recommendation based on voice input
    return Data_Recommendation.show_recommendation(text)

@app.get("/text_input")
async def text_search(text: str):
    # Return recommendation based on text search
    return Data_Recommendation.getRecommendedProducts(text)

@app.get("/transcript")
async def transcriptAPI(Path: str):
    # Convert voice to text
    text_data = Voice_to_Text.speech_to_text(Path)
    return {"transcript": text_data}

@app.post("/image")
async def image(request: Request):
    try:
        data = await request.json()
        base64_string = data.get('imageData')

        if not base64_string:
            raise HTTPException(status_code=400, detail="No image data provided")
        
        # Decode the base64 string
        image_data = base64.b64decode(base64_string)
        
        # Load the image using PIL
        image = Image.open(io.BytesIO(image_data))
        
        # Convert image to RGB if necessary
        if image.mode not in ('RGB', 'RGBA'):
            image = image.convert('RGB')

        # Create a unique filename
        filename = 'image.jpg'
        file_path = os.path.join(SAVE_DIR, filename)

        # Save the image
        image.save(file_path, 'JPEG')
        
        # Call the recommendation function
        response_data = Data_Recommendation.show_image_recommendation(file_path)

        # Clean up: delete the saved image
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/default")
async def default_search():
    # Generate random default products
    default_products = np.random.randint(1, 100, 50).tolist()
    return Data_Recommendation.get_data(default_products)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=7860)
    