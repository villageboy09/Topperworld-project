import os
from flask import Flask, request, jsonify
from PIL import Image
import google.generativeai as genai
import io

# Set up the Flask app
app = Flask(__name__)

# Set the environment variable for API key
os.environ["API_KEY"] = "AIzaSyCroPtzjFYNxHBuf_f-S_10cxu-B9TBhQI"

# Configure the API
api_key = os.environ.get("API_KEY")
if not api_key:
    raise ValueError("API key is not set in environment variables.")
genai.configure(api_key=api_key)

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

# Define supported crops
SUPPORTED_CROPS = [
    "tomato", "chilli", "paddy", "pearl millet", 
    "sorghum", "wheat", "maize", "groundnut", 
    "soybean", "sugarcane"
]

# Function to process the image using PIL
def process_image_with_pil(image_file):
    image = Image.open(image_file).convert("RGB")
    processed_image = image.convert("L")
    return processed_image

# Function to upload an image using File API
def upload_image(image_file):
    try:
        processed_image = process_image_with_pil(image_file)
        temp_path = '/tmp/temp_image.png'
        processed_image.save(temp_path)
        response = genai.upload_file(path=temp_path, display_name="Processed Image")
        return response.uri
    except Exception as e:
        return None

# Function to analyze image and get recommendations
def analyze_image(image_uri):
    try:
        prompt = (
            "Identify any crop diseases from the uploaded image and provide recommendations for the following crops: "
            + ", ".join(SUPPORTED_CROPS) + "."
        )
        response = model.generate_content([image_uri, prompt])
        return response.text
    except Exception as e:
        return "Unable to generate recommendations."

# Define the API endpoint
@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    image_file = request.files['image']
    image_uri = upload_image(image_file)
    
    if image_uri:
        recommendations = analyze_image(image_uri)
        return jsonify({"recommendations": recommendations})
    else:
        return jsonify({"error": "Failed to upload image"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
