import os
import google.generativeai as genai

os.environ["GEMINI_API_KEY"] = AIzaSyCroPtzjFYNxHBuf_f-S_10cxu-B9TBhQI

# Configure the API key for the Google Generative AI
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Define the generation configuration for the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Create the GenerativeModel object with the specified model and configuration
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Start a chat session
chat_session = model.start_chat(
    history=[]
)

# Define the input prompt for generating agriculture news
prompt = """
Generate 10 latest agriculture news headlines from all over the world.
Format the response as follows:
Image URL, Headline, and Description
"""

# Send the input prompt to the chat session
response = chat_session.send_message(prompt)

# Print the response text
print(response.text)
