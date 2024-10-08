import requests
import pandas as pd
from google.oauth2.service_account import Credentials
import gspread
import streamlit as st
import json

# Configuration
API_KEY = '579b464db66ec23bdd00000178b302e7013b49d67c2084993f975dc9'  # Replace with your actual API key
SHEET_ID = '1rMMbedzEVB9s72rUmwUAEdqlHt5Ri4VCRxmeOe651Yg'

# Function to fetch agriculture data
def fetch_agriculture_data(state=''):
    url = f'https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070'
    params = {
        'api-key': API_KEY,
        'format': 'json',
        'limit': 1000,  # Maximum allowed by the API
        'offset': 0,
    }
    if state:
        params['filters[state]'] = state
    
    all_records = []
    
    try:
        while True:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            records = data.get('records', [])
            
            if not records:
                break
            
            all_records.extend(records)
            
            # Update offset for the next request
            params['offset'] += len(records)
            
            # Check if we've reached the end of the data
            if len(all_records) >= data.get('total', 0):
                break
        
        agriculture_data = [
            {
                'State': record.get('state', ''),
                'District': record.get('district', ''),
                'Market': record.get('market', ''),
                'Commodity': record.get('commodity', ''),
                'Variety': record.get('variety', ''),
                'Arrival Date': record.get('arrival_date', ''),
                'Min Price': record.get('min_price', ''),
                'Max Price': record.get('max_price', ''),
                'Modal Price': record.get('modal_price', '')
            }
            for record in all_records
        ]
        
        return agriculture_data
    
    except requests.RequestException as e:
        st.error(f"Error fetching agriculture data: {e}")
        return []

# Function to update Google Sheet
def update_google_sheet(data):
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    
    try:
        google_credentials = st.secrets["google"]["credentials"]
        credentials_dict = json.loads(google_credentials)

        if 'private_key' in credentials_dict:
            private_key = credentials_dict['private_key']
            private_key = private_key.replace('\\n', '\n')
            credentials_dict['private_key'] = private_key

        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
        client = gspread.authorize(credentials)
        sheet = client.open_by_key(SHEET_ID).sheet1

        # Clear existing data and update with new data
        df = pd.DataFrame(data)
        sheet.clear()
        sheet.update([df.columns.tolist()] + df.values.tolist())
        st.success("Google Sheet updated successfully.")
    
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    st.title("Agriculture Data Updater")
    
    state = st.text_input("Enter state name (optional):", "")
    
    if st.button("Fetch and Update Data"):
        with st.spinner("Fetching agriculture data..."):
            agriculture_data = fetch_agriculture_data(state)
        
        if agriculture_data:
            st.info(f"Fetched {len(agriculture_data)} agriculture records.")
            with st.spinner("Updating Google Sheet..."):
                update_google_sheet(agriculture_data)
        else:
            st.warning("No agriculture data to update.")
    
    st.markdown("---")
    st.write("This app fetches agriculture data from the Indian government API and updates a Google Sheet.")

if __name__ == '__main__':
    main()
