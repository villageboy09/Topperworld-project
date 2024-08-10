import streamlit as st
import requests

# Define the URL of the Flask API
FLASK_API_URL = 'https://arjun0987.pythonanywhere.com//analyze'  # Replace with your actual URL

st.title('Crop Disease Detection and Recommendations')

uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    files = {'image': uploaded_file}
    try:
        response = requests.post(FLASK_API_URL, files=files)
        
        # Debugging output
        st.write("Response status code:", response.status_code)
        st.write("Response content:", response.content)
        
        if response.status_code == 200:
            try:
                data = response.json()
                recommendations = data.get('recommendations', 'No recommendations found.')
                st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)
                st.subheader('Recommendations')
                st.write(recommendations)
            except ValueError as e:
                st.error("Error decoding JSON response: " + str(e))
        else:
            st.error("Failed to analyze image. Status code: {}".format(response.status_code))
    
    except requests.RequestException as e:
        st.error("Request failed: " + str(e))
else:
    st.info("Please upload an image file.")
