import requests
import streamlit as st
import google.generativeai as genai
import os

# Function to fetch agriculture news from NewsAPI
def fetch_agriculture_news(api_key, num_news=10):
    url = f'https://newsapi.org/v2/top-headlines?category=business&country=us&q=agriculture&pageSize={num_news}&apiKey={api_key}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure we notice bad responses
        data = response.json()
        
        news_items = []
        for article in data.get('articles', []):
            news_items.append({
                'headline': article.get('title'),
                'image_url': article.get('urlToImage'),
                'brief': article.get('description')
            })
        
        return news_items
    except Exception as e:
        st.error(f"Error fetching news: {e}")
        return []

# Initialize Google Generative AI
def initialize_gemini_api(api_key):
    # Set up the environment variable for API key
    os.environ["GEMINI_API_KEY"] = api_key
    
    # Configure the Gemini AI with your API key
    genai.configure(api_key=api_key)
    
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction="Professional and Formal\nConcise and Direct\nDetailed and Explanatory",
        tools='code_execution',
    )
    
    return model

# Function to format news for model input
def format_news_for_model(news_items):
    formatted_news = ""
    for item in news_items:
        formatted_news += f"Headline: {item['headline']}\nImage: {item['image_url']}\nBrief: {item['brief']}\n\n"
    return formatted_news

# Streamlit app setup
st.title("Agriculture News Summary")
st.write("Fetching and processing news...")

# Fixed NewsAPI key for demonstration
news_api_key = "9bf84e1aa0da493dbd620fe3eaf359d1"
gemini_api_key = st.text_input("AIzaSyCroPtzjFYNxHBuf_f-S_10cxu-B9TBhQI")

if gemini_api_key:
    # Fetch news
    news_items = fetch_agriculture_news(news_api_key)
    
    if news_items:
        # Display raw news data for debugging
        st.write("Raw News Data:", news_items)
        
        # Format news and get summary from Gemini AI
        news_summary = format_news_for_model(news_items)
        
        # Initialize Gemini AI
        model = initialize_gemini_api(gemini_api_key)
        chat_session = model.start_chat(history=[])
        
        # Send request to Gemini AI
        response = chat_session.send_message(f"Here is the latest agriculture news:\n{news_summary}")
        
        # Display the summary from Gemini AI
        st.write("Model Response:")
        st.write(response.text)
        
        # Display individual news items
        st.write("Latest Agriculture News:")
        for item in news_items:
            st.write(f"**Headline:** {item['headline']}")
            if item['image_url']:
                st.image(item['image_url'])
            st.write(f"**Brief:** {item['brief']}")
            st.write("---")
    else:
        st.write("No news items found.")
else:
    st.write("Please enter your Gemini API key to fetch and process news.")
