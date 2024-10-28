import streamlit as st
import requests
import base64

# Replace with your API Gateway endpoint
API_URL = "https://dobsyrx0ci.execute-api.ap-northeast-1.amazonaws.com/develop"

# Set up Streamlit interface
st.title("PDF Processor and Query System")

# PDF upload function
def upload_pdf(file):
    pdf_base64 = base64.b64encode(file.read()).decode('utf-8')
    response = requests.post(
        f"{API_URL}/upload",
        json={
            "pdf_base64": pdf_base64,
            "filename": file.name
        }
    )
    return response.json()

# PDF query function
def ask_question(question):
    response = requests.post(
        f"{API_URL}/ask",
        json={"question": question}
    )
    return response.json()

# Upload PDF
uploaded_file = st.file_uploader("Choose a PDF file to upload", type="pdf")
if uploaded_file is not None:
    st.write("Uploading PDF...")
    upload_response = upload_pdf(uploaded_file)
    st.write(upload_response)

# Ask a question about the PDF
question = st.text_input("Ask a question about the document")
if question:
    st.write("Fetching answer...")
    question_response = ask_question(question)
    st.write(question_response.get("response", "No response available"))
