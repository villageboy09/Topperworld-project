import requests
import pandas as pd
from google.oauth2.service_account import Credentials
import gspread
import streamlit as st
import json

# Configuration
SHEET_ID = '1rMMbedzEVB9s72rUmwUAEdqlHt5Ri4VCRxmeOe651Yg'
NEWS_API_TOKEN = 'UkK6MzB7AEmOmAbcSvbIHVvozyeqUaXEe2WdpWrc'

def fetch_agriculture_news():
    url = f'https://api.thenewsapi.com/v1/news/all?api_token={NEWS_API_TOKEN}&language=en&limit=10'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        articles = data.get('data', [])  # Extract articles from the 'data' key

        # Filter articles related to agriculture
        agriculture_articles = [article for article in articles if 'agriculture' in article.get('title', '').lower() or 'agriculture' in article.get('description', '').lower()]

        news_data = []
        for article in agriculture_articles:
            description = article.get('description', '')
            # Ensure description is at least 250 characters
            if len(description) < 250:
                description = f"{description} {' '.join(['Additional information'] * ((250 - len(description)) // 20))}"
            news_data.append({
                'Image URL': article.get('image_url', ''),
                'Title': article.get('title', ''),
                'Description': description
            })
        
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
                st.info(f"Fetched {len(news_data)} agriculture-related news articles.")
                with st.spinner("Updating Google Sheet..."):
                    update_google_sheet(news_data)
            else:
                st.warning("No agriculture-related news data to update.")
    
    st.markdown("---")
    st.write("This app fetches agriculture-related news and updates a Google Sheet.")

if __name__ == '__main__':
    main()
