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
        response = requests.post(f"https://h8l1p5yxsj.execute-api.ap-northeast-1.amazonaws.com/Initial/", json=payload)
        
        if response.status_code == 200:
            st.success(f"PDF '{filename}' uploaded and processed successfully.")
        else:
            st.error(f"Error: {response.json().get('detail')}")

# Function to ask question
def ask_question(question):
    if question:
        payload = {"question": question}
        response = requests.post(f"{API_URL}/ask", json=payload)
        
        if response.status_code == 200:
            answer = response.json().get("response")
            return answer
        else:
            st.error(f"Error: {response.json().get('detail')}")
            return None

# # Streamlit App Layout
# st.sidebar.title("Document Q&A Chatbot")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# # Section for PDF Upload
# st.sidebar.header("Upload a PDF")
# uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")
# if uploaded_file:
#     if st.sidebar.button("Upload PDF"):
#         upload_pdf(uploaded_file)

# Section for asking questions
st.header("Ask a Question")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input box for user question
if user_input := st.chat_input("Ask a question..."):
    # Display the user's message in the chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Get response from backend
    response = ask_question(user_input)
    
    # Display the agent's response in the chat
    if response:
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
