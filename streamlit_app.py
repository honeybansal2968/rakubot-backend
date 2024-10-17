import streamlit as st
import requests
st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
api_url = "https://ubiquitous-pancake-wxv4v7pjq74h5jjw-7860.app.github.dev/"  # Make sure Flask is running at this URL

# Send request to Flask API's "/" endpoint when the Streamlit app is loaded
try:
    response = requests.get(api_url)
    if response.status_code == 200:
        st.write("Backend API is working! 🎉")
        st.write("Response from backend:", response.json())
    else:
        st.write("Failed to connect to backend API.")
except Exception as e:
    st.write(f"Error connecting to backend: {e}")