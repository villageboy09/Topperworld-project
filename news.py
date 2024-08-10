import requests
from bs4 import BeautifulSoup
import streamlit as st
import google.generativeai as genai
import os

# Function to scrape news from a given URL
def scrape_agriculture_news(url, num_news=10):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Ensure we notice bad responses

        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_items = []
        
        # Adjust selectors based on the actual HTML structure of the website
        for item in soup.find_all('article', limit=num_news):
            headline = item.find('h2').get_text(strip=True) if item.find('h2') else 'No headline'
            image_url = item.find('img')['src'] if item.find('img') else 'No image'
            brief = item.find('p').get_text(strip=True) if item.find('p') else 'No brief'
            
            news_items.append({
                'headline': headline,
                'image_url': image_url,
                'brief': brief
            })
        
        return news_items
    except Exception as e:
        st.error(f"Error scraping news from {url}: {e}")
        return []

# List of well-known agriculture websites
news_urls = [
    'https://krishijagran.com',  # Krishi Jagran
    'https://pib.gov.in/PressReleasePage.aspx?PRID=1585098',  # PIB
    'https://www.agribusinessglobal.com',  # Agribusiness Global
    'https://www.agri-tech-e.co.uk',  # Agri-Tech East
    'https://www.agweb.com',  # AgWeb
    'https://www.fwi.co.uk',  # Farmers Weekly
    'https://www.usda.gov',  # USDA
    'https://www.agmrc.org',  # Ag Marketing Resource Center
    'https://www.farmprogress.com'  # Farm Progress
]

# Scrape news from all URLs
all_news_items = []
for url in news_urls:
    news_items = scrape_agriculture_news(url)
    all_news_items.extend(news_items)

# Streamlit app setup
st.title("Agriculture News Summary")
st.write("Fetching and processing news...")

# Display raw news data for debugging
st.write("Raw News Data:", all_news_items)

# Example of processing and displaying results
if all_news_items:
    for item in all_news_items:
        st.write(f"**Headline:** {item['headline']}")
        st.image(item['image_url'])
        st.write(f"**Brief:** {item['brief']}")
        st.write("---")
else:
    st.write("No news items found.")

# Google Generative AI setup
os.environ["GEMINI_API_KEY"] = "AIzaSyCroPtzjFYNxHBuf_f-S_10cxu-B9TBhQI"

# Configure the model with your API key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Define the generation configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize the GenerativeModel
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="Professional and Formal\nConcise and Direct\nDetailed and Explanatory",
    tools='code_execution',
)

# Start a chat session
chat_session = model.start_chat(
    history=[]
)

# Format news for model input
def format_news_for_model(news_items):
    formatted_news = ""
    for item in news_items:
        formatted_news += f"Headline: {item['headline']}\nImage: {item['image_url']}\nBrief: {item['brief']}\n\n"
    return formatted_news

# Prepare news summary and request model response
news_summary = format_news_for_model(all_news_items)
response = chat_session.send_message(f"Here is the latest agriculture news:\n{news_summary}")

# Display model response
st.write("Model Response:")
st.write(response.text)
