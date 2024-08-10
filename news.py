import requests
import pandas as pd
from google.oauth2.service_account import Credentials
import gspread
import streamlit as st
import json
import base64

# Configuration
NEWS_API_KEY = '9bf84e1aa0da493dbd620fe3eaf359d1'
SHEET_ID = '1rMMbedzEVB9s72rUmwUAEdqlHt5Ri4VCRxmeOe651Yg'

def fetch_agriculture_news():
    url = f'https://newsapi.org/v2/everything?q=agriculture&apiKey={NEWS_API_KEY}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        articles = data.get('articles', [])
        
        news_data = [
            {
                'Image URL': article.get('urlToImage', ''),
                'Title': article.get('title', ''),
                'Description': article.get('description', '')
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
        
        # Debug: Print the keys in credentials_dict
        print("Credentials dict keys:", credentials_dict.keys())
        
        if 'private_key' in credentials_dict:
            private_key = credentials_dict['private_key']
            
            # Debug: Print the first and last 10 characters of the private key
            print("Private key start:", private_key[:10])
            print("Private key end:", private_key[-10:])
            
            # Remove any whitespace and newline characters
            private_key = ''.join(private_key.split())
            
            # Ensure the key has the correct start and end markers
            if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
                private_key = '-----BEGIN PRIVATE KEY-----' + private_key
            if not private_key.endswith('-----END PRIVATE KEY-----'):
                private_key = private_key + '-----END PRIVATE KEY-----'
            
            # Add newline every 64 characters
            private_key = '\n'.join(private_key[i:i+64] for i in range(0, len(private_key), 64))
            
            # Update the credentials_dict with the formatted private key
            credentials_dict['private_key'] = private_key
        
        # Try to create credentials
        try:
            credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
        except ValueError as e:
            print("Error creating credentials:", str(e))
            # If there's an error, try to decode the private key
            if 'private_key' in credentials_dict:
                try:
                    decoded_key = base64.b64decode(credentials_dict['private_key'])
                    print("Successfully decoded private key")
                except Exception as decode_error:
                    print("Error decoding private key:", str(decode_error))
            raise

        # Rest of your function...
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
