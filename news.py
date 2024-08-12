import requests
import pandas as pd
from google.oauth2.service_account import Credentials
import gspread
import streamlit as st
import json

# Configuration
GEMINI_API_KEY = 'AIzaSyCroPtzjFYNxHBuf_f-S_10cxu-B9TBhQI'
SHEET_ID = '1rMMbedzEVB9s72rUmwUAEdqlHt5Ri4VCRxmeOe651Yg'

def fetch_agriculture_news():
    # Replace with the actual Gemini API endpoint
    url = f'https://api.gemini.com/v1/news?q=agriculture&apiKey={GEMINI_API_KEY}&pageSize=10'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        articles = data.get('articles', [])
        
        # Adjust based on the actual Gemini API response structure
        news_data = [
            {
                'Image URL': article.get('urlToImage', ''),
                'Title': article.get('title', ''),
                'Content': article.get('content', '')
            }
            for article in articles
        ]
        
        return news_data
    
    except requests.RequestException as e:
        st.error(f"Error fetching news: {e}")
        return []

def update_google_sheet(data):
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    
    try:
        google_credentials = st.secrets["google"]["credentials"]
        credentials_dict = json.loads(google_credentials)
        
        if 'private_key' in credentials_dict:
            private_key = credentials_dict['private_key']
            # Ensure private key is correctly formatted
            private_key = private_key.replace('\\n', '\n')  # Handle escaped newline characters
            credentials_dict['private_key'] = private_key
        
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
        
        client = gspread.authorize(credentials)
        sheet = client.open_by_key(SHEET_ID).sheet1
        df = pd.DataFrame(data)
        sheet.clear()
        sheet.update([df.columns.tolist()] + df.values.tolist())
        st.success("Google Sheet updated successfully.")
    
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    st.title("Agriculture News Updater")
    
    if st.button("Fetch and Update News"):
        with st.spinner("Fetching news..."):
            news_data = fetch_agriculture_news()
        
        if news_data:
            st.info(f"Fetched {len(news_data)} news articles.")
            with st.spinner("Updating Google Sheet..."):
                update_google_sheet(news_data)
        else:
            st.warning("No news data to update.")
    
    st.markdown("---")
    st.write("This app fetches agriculture news and updates a Google Sheet.")

if __name__ == '__main__':
    main()
