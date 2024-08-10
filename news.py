import requests
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# Configuration
NEWS_API_KEY = '9bf84e1aa0da493dbd620fe3eaf359d1'
SHEET_ID = '1rMMbedzEVB9s72rUmwUAEdqlHt5Ri4VCRxmeOe651Yg'
SERVICE_ACCOUNT_FILE = 'https://github.com/villageboy09/Topperworld-project/main/news.json'

# Function to fetch news
def fetch_agriculture_news():
    url = f'https://newsapi.org/v2/everything?q=agriculture&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    data = response.json()
    articles = data['articles']
    
    news_data = []
    for article in articles:
        image_url = article.get('urlToImage', '')
        title = article.get('title', '')
        description = article.get('description', '')
        news_data.append({'Image URL': image_url, 'Title': title, 'Description': description})
    
    return news_data

# Function to update Google Sheet
def update_google_sheet(data):
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
    client = gspread.authorize(credentials)
    
    sheet = client.open_by_key(SHEET_ID).sheet1
    df = pd.DataFrame(data)
    sheet.update([df.columns.tolist()] + df.values.tolist())

# Main function
def main():
    news_data = fetch_agriculture_news()
    update_google_sheet(news_data)

if __name__ == '__main__':
    main()
