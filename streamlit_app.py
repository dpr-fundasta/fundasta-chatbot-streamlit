import streamlit as st
import io
import PyPDF2
from langchain_openai import ChatOpenAI
from openai import OpenAI
from pinecone import Pinecone
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from prompt import CONTEXT_PROMPT
import requests
API_URL = "https://g28ts5sgtg.execute-api.ap-northeast-1.amazonaws.com"
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"]

# Set up OpenAI and Pinecone clients
client = OpenAI(api_key=OPENAI_API_KEY)
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small", api_key=OPENAI_API_KEY)
chat_model = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY, temperature=0.4)
pc = Pinecone(PINECONE_API_KEY)
index_name = "test-c"
index = pc.Index(index_name)

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


def generate_chunk_context(whole_document: str, chunk: str) -> str:
    """Generates context for a chunk using ChatOpenAI model."""
    variables = {"WHOLE_DOCUMENT": whole_document, "CHUNK_CONTENT": chunk}
    openai_chain = CONTEXT_PROMPT | chat_model
    response = openai_chain.invoke(variables)
    return response.content

def upload_pdf(pdf_file, filename):
    try:
        text = ""
        reader = PyPDF2.PdfReader(pdf_file)
        total_pages = len(reader.pages)

        # Initialize progress bar
        progress_bar = st.sidebar.progress(0)

        for i, page in enumerate(reader.pages):
            text += page.extract_text() or ""
            # Update progress bar
            progress_bar.progress((i + 1) / total_pages)

        # Check if text is extracted
        if not text:
            st.sidebar.error("No text could be extracted from the PDF.")
            #return "No text could be extracted from the PDF."

        # Split text into chunks
        text_splitter = SemanticChunker(embeddings_model, breakpoint_threshold_type="percentile", breakpoint_threshold_amount=45)
        docs = text_splitter.create_documents([text])

        vectors = []
        for i, doc in enumerate(docs):
            chunk_text = doc.page_content
            context = generate_chunk_context(text, chunk_text)
            enriched_chunk = f"{context}\n{chunk_text}"
            embedding_response = client.embeddings.create(input=enriched_chunk, model="text-embedding-3-small")
            embedding_vector = embedding_response.data[0].embedding

            # Create vector for Pinecone
            vectors.append((f"{filename}_{i}", embedding_vector, {"text": enriched_chunk}))

            # Update progress bar for embedding creation
            progress_bar.progress((total_pages + i + 1) / (total_pages + len(docs)))

        # Upsert vectors to Pinecone
        index.upsert(vectors=vectors)
        st.sidebar.success(f"PDF successfully processed and stored. Chunk count: {len(docs)}")
        #return f"PDF successfully processed and stored. Chunk count: {len(docs)}"
    except Exception as e:
        st.sidebar.error(f"Failed to process PDF: {str(e)}")
        #return f"Failed to process PDF: {str(e)}"
# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

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

uploaded_file = st.sidebar.file_uploader("Upload a PDF file", type="pdf")
if uploaded_file is not None:
    filename = uploaded_file.name
    result = upload_pdf(io.BytesIO(uploaded_file.read()), filename)
    st.write(result)
