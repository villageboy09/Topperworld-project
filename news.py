import requests
from bs4 import BeautifulSoup

def scrape_agriculture_news(url, num_news=10):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    news_items = []
    
    # Update these selectors based on the website's structure
    for item in soup.find_all('article', class_='news-item')[:num_news]:
        headline = item.find('h2', class_='headline').get_text(strip=True)
        image_url = item.find('img', class_='news-image')['src']
        brief = item.find('p', class_='brief').get_text(strip=True)
        
        news_items.append({
            'headline': headline,
            'image_url': image_url,
            'brief': brief
        })
    
    return news_items

# List of well-known agriculture websites
news_urls = [
    'https://krishijagran.com',
    'https://pib.gov.in/PressReleasePage.aspx?PRID=1585098',
    'https://www.agribusinessglobal.com',
    'https://www.agri-tech-e.co.uk',
    'https://www.agweb.com',
    'https://www.fwi.co.uk',
    'https://www.usda.gov',
    'https://www.agmrc.org',
    'https://www.farmprogress.com'
]

all_news_items = []
for url in news_urls:
    news_items = scrape_agriculture_news(url)
    all_news_items.extend(news_items)

import os
import google.generativeai as genai


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

def format_news_for_model(news_items):
    formatted_news = ""
    for item in news_items:
        formatted_news += f"Headline: {item['headline']}\nImage: {item['image_url']}\nBrief: {item['brief']}\n\n"
    return formatted_news

news_summary = format_news_for_model(all_news_items)

response = chat_session.send_message(f"Here is the latest agriculture news:\n{news_summary}")

print(response.text)
