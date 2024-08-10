import os
import requests
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Set your News API key here
news_api_key = "9bf84e1aa0da493dbd620fe3eaf359d1"

# Define the News API endpoint
news_api_url = "https://newsapi.org/v2/everything"

# Define query parameters for fetching agriculture news
params = {
    'q': 'agriculture',
    'language': 'en',
    'pageSize': 10,  # Fetch 10 news articles
    'apiKey': news_api_key,
}

# Function to truncate the description to 100 words
def truncate_description(description, word_limit=100):
    words = description.split()
    if len(words) > word_limit:
        return ' '.join(words[:word_limit]) + '...'
    return description

# Make a request to the News API
response = requests.get(news_api_url, params=params)

# Check if the request was successful
if response.status_code == 200:
    news_data = response.json()
    articles = news_data.get('articles', [])
    
    # Prepare a list to hold the news data
    news_list = []
    
    # Format the articles as Image URL, Headline, and Description
    for i, article in enumerate(articles):
        image_url = article.get('urlToImage', 'No image available')
        headline = article.get('title', 'No title available')
        description = article.get('description', 'No description available')
        
        # Truncate description to 100 words
        truncated_description = truncate_description(description)
        
        # Append the news data to the list
        news_list.append({
            'Image URL': image_url,
            'Headline': headline,
            'Description': truncated_description
        })
    
    # Convert the news list to a DataFrame
    news_df = pd.DataFrame(news_list)
    
    # Google Sheets authentication
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('news.json', scope)  # Replace with your actual JSON file name
    client = gspread.authorize(creds)
    
    # Open the Google Sheet using its URL
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1rMMbedzEVB9s72rUmwUAEdqlHt5Ri4VCRxmeOe651Yg/edit?gid=0")
    
    # Select the first worksheet
    worksheet = sheet.get_worksheet(0)
    
    # Clear the existing content in the worksheet (optional)
    worksheet.clear()
    
    # Update the worksheet with the new data
    worksheet.update([news_df.columns.values.tolist()] + news_df.values.tolist())
    
    print("News data has been written to your Google Sheet.")
else:
    print(f"Failed to fetch news: {response.status_code}")
