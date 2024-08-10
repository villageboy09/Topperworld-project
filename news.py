import requests
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import streamlit as st
import json

# Configuration
NEWS_API_KEY = '9bf84e1aa0da493dbd620fe3eaf359d1'
SHEET_ID = '1rMMbedzEVB9s72rUmwUAEdqlHt5Ri4VCRxmeOe651Yg'

# Function to fetch news
def fetch_agriculture_news():
    url = f'https://newsapi.org/v2/everything?q=agriculture&apiKey={NEWS_API_KEY}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        articles = data.get('articles', [])
        
        news_data = []
        for article in articles:
            image_url = article.get('urlToImage', '')
            title = article.get('title', '')
            description = article.get('description', '')
            news_data.append({'Image URL': image_url, 'Title': title, 'Description': description})
        
        return news_data
    
    except requests.RequestException as e:
        st.error(f"Error fetching news: {e}")
        return []

# Function to update Google Sheet
def update_google_sheet(data):
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    
    # Load credentials from Streamlit secrets
    google_credentials = st.secrets["google"]["credentials"]
    credentials_dict = json.loads(google_credentials)
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    
    try:
        client = gspread.authorize(credentials)
        sheet = client.open_by_key(SHEET_ID).sheet1
        df = pd.DataFrame(data)
        sheet.update([df.columns.tolist()] + df.values.tolist())
        st.success("Google Sheet updated successfully.")
    
    except gspread.exceptions.APIError as e:
        st.error(f"Error updating Google Sheet: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

# Main function
def main():
    news_data = fetch_agriculture_news()
    if news_data:
        update_google_sheet(news_data)
    else:
        st.warning("No news data to update.")

if __name__ == '__main__':
    main()
