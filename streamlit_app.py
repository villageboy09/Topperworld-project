import streamlit as st
import requests

# Define the URL of the Flask API
FLASK_API_URL = 'https://apiend.streamlit.app/analyze'  # Replace with your actual URL

st.title('Crop Disease Detection and Recommendations')

uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    files = {'image': uploaded_file}
    response = requests.post(FLASK_API_URL, files=files)
    
    if response.status_code == 200:
        st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)
        data = response.json()
        recommendations = data.get('recommendations', 'No recommendations found.')
        st.subheader('Recommendations')
        st.write(recommendations)
    else:
        st.error("Failed to analyze image.")
else:
    st.info("Please upload an image file.")
