import streamlit as st
from websocket import create_connection
import json
import requests
import base64
# WebSocket and API URLs
WS_URL = "wss://lckhw3fof3.execute-api.ap-northeast-1.amazonaws.com/production"  # Replace with actual WebSocket URL
API_URL = "https://j0kn8pau5l.execute-api.ap-northeast-1.amazonaws.com/develop/upload"
# Set up Streamlit layout
st.sidebar.title("FundastA R.A.G Chatbot")
uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")
st.sidebar.write("Maximum file size: 10 MB")
# Initialize session state to store file content and name
if "file_uploaded" not in st.session_state:
    st.session_state["file_uploaded"] = False
    st.session_state["file_name"] = ""
    st.session_state["file_content_base64"] = ""
if uploaded_file and not st.session_state["file_uploaded"]:
    # Check file size
    file_size = uploaded_file.size
    max_size = 10 * 1024 * 1024  # 10 MB in bytes
    if file_size > max_size:
        st.error("File exceeds the 10 MB limit. Please choose a smaller file.")
    else:
        # Read and encode the PDF file content in base64
        file_content = uploaded_file.read()
        st.session_state["file_content_base64"] = base64.b64encode(file_content).decode("utf-8")
        st.session_state["file_name"] = uploaded_file.name
        st.session_state["file_uploaded"] = True

        # Prepare the JSON payload
        payload = {
            "file_name": st.session_state["file_name"],
            "file_content": st.session_state["file_content_base64"]
        }
      
        try:
            # Send the POST request to the API
            response = requests.post(API_URL, json=payload)
            
            # Check the response
            if response.status_code == 200:
                st.sidebar.success("File uploaded successfully!")
            else:
                st.sidebar.error(f"Failed to upload file. Status code: {response.status_code}")
                st.sidebar.write(response.text)
                
        except requests.RequestException as e:
            st.error(f"Request failed: {e}")
# Store conversation in session state
if "conversation" not in st.session_state:
    st.session_state["conversation"] = []
# WebSocket connection function
def ask_websocket(question):
    try:
        # Establish WebSocket connection
        ws = create_connection(WS_URL)
        
        # Format and send message to WebSocket
        payload = json.dumps({"action": "ask", "question": question})
        ws.send(payload)
        
        # Receive responses (blocking call)
        responses = []
        while True:
            result = ws.recv()
            if not result:
                break
            
            # Parse response
            response_data = json.loads(result)
            responses.append(response_data)
        
        # Close WebSocket connection
        ws.close()
        
        return responses
    
    except Exception as e:
        return [{"response": f"Error: {e}"}]
# Message input box
user_input = st.chat_input("Type your question here")
# Handle user input
if user_input:
    # Display user's message
    st.session_state.conversation.append({"user": user_input})

    # Send user's message to backend and get response
    backend_responses = ask_websocket(user_input)
    
    # Process backend responses
    for response in backend_responses:
        if "response" in response:
            st.session_state.conversation.append({"bot": response["response"]})

# Display the conversation
for message in st.session_state.conversation:
    if "user" in message:
        st.write(f"▲ {message['user']}")
    elif "bot" in message:
        st.write(f"▼ {message['bot']}")
