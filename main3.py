import streamlit as st
import requests
import base64

# API URL (replace with your backend's URL)
API_URL = "https://g28ts5sgtg.execute-api.ap-northeast-1.amazonaws.com"

# Function to upload PDF
def upload_pdf(file):
    if file is not None:
        # Read file content and encode in base64
        file_data = file.read()
        encoded_file = base64.b64encode(file_data).decode('utf-8')
        filename = file.name

        # Prepare payload for PDF upload
        payload = {
            "pdf_base64": encoded_file,
            "filename": filename
        }

        # Send request to the backend API
        try:
            response = requests.post(f"{API_URL}/upload", json=payload)
            response.raise_for_status()  # Raise exception if status code is not 200-299
            response_data = response.json()  # Parse the JSON response

            if response.status_code == 200:
                detail = response_data.get("detail", "Upload successful.")
                st.success(detail)  # Display success message with details
            else:
                error_message = response_data.get("detail", "Unknown error occurred.")
                st.error(f"Error: {error_message}")

        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")

# Streamlit App Layout
st.sidebar.title("FundastA Chatbot")

# Section for PDF Upload
st.sidebar.header("Upload a PDF")
uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")
if uploaded_file:
    if st.sidebar.button("Upload PDF"):
        with st.spinner("Processing PDF upload..."):
            upload_pdf(uploaded_file)
