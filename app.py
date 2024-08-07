import os
import streamlit as st
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain.prompts import load_prompt
from streamlit import session_state as ss
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import uuid
import json
import time
import datetime

# Function to check if a string is a valid JSON
def is_valid_json(data):
    try:
        json.loads(data)
        return True
    except json.JSONDecodeError:
        return False

# Function to initialize connection to Firebase Firestore
@st.cache_resource
def init_connection():
    cred = credentials.Certificate('.streamlit/firestone-key.json')
    firebase_admin.initialize_app(cred)
    return firestore.client()

# Attempt to connect to Firebase Firestore
try:
    db = init_connection()
except Exception as e:
    st.write("Failed to connect to Firebase:", e)

# Access Firebase Firestore collection
if 'db' in locals():
    conversations_collection = db.collection('conversations')
else:
    st.write("Unable to access conversations collection. Firebase connection not established.")

# Retrieve OpenAI API key
if "OPENAI_API_KEY" in os.environ:
    openai_api_key = os.getenv("OPENAI_API_KEY")
else:
    openai_api_key = st.secrets["OPENAI_API_KEY"]

# Streamlit app title and disclaimer
st.title("Ajitesh's resume bot")
# st.image("https://harikrishnad1997.github.io/images/about.jpg")
with st.expander("⚠️Disclaimer"):
    st.write("""This bot is a LLM trained on GPT-3.5-turbo model to answer questions about Ajitesh's professional background and qualifications. Your responses are recorded in a database for quality assurance and improvement purposes. Please be respectful and avoid asking personal or inappropriate questions.""")

# Define file paths and load initial settings
path = os.path.dirname(__file__)
prompt_template = path+"/templates/template.json"
prompt = load_prompt(prompt_template)
faiss_index = path+"/faiss_index"
data_source = path+"/data/about_ajitesh.csv"
pdf_source = path+"/data/Ajitesh_Goswami_Resume.pdf"

# Function to store conversation in Firebase
def store_conversation(conversation_id, user_message, bot_message, answered):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "conversation_id": conversation_id,
        "timestamp": timestamp,
        "user_message": user_message,
        "bot_message": bot_message,
        "answered": answered
    }
    conversations_collection.add(data)

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings()

# Load FAISS index or create a new one if it doesn't exist
if os.path.exists(faiss_index):
    vectors = FAISS.load_local(faiss_index, embeddings, allow_dangerous_deserialization=True)
else:
    # Load data from PDF and CSV sources
    pdf_loader = PyPDFLoader(pdf_source)
    pdf_data = pdf_loader.load_and_split()
    csv_loader = CSVLoader(file_path=data_source, encoding="utf-8")
    csv_data = csv_loader.load()
    data = pdf_data + csv_data

    # Create embeddings for the documents and save the index
    vectors = FAISS.from_documents(data, embeddings)
    vectors.save_local("faiss_index")

# Initialize conversational retrieval chain
retriever = vectors.as_retriever(search_type="similarity", search_kwargs={"k": 6, "include_metadata": True, "score_threshold": 0.6})
chain = ConversationalRetrievalChain.from_llm(llm=ChatOpenAI(temperature=0.5, model_name='gpt-3.5-turbo', openai_api_key=openai_api_key), 
                                              retriever=retriever, return_source_documents=True, verbose=True, chain_type="stuff",
                                              max_tokens_limit=4097, combine_docs_chain_kwargs={"prompt": prompt})

# Function to handle conversational chat
def conversational_chat(query):
    with st.spinner("Thinking..."):
        result = chain({"system": 
        "You are a Resume Bot, a comprehensive, interactive resource for exploring Ajitesh Goswami's background, skills, and expertise. Be polite and provide answers based on the provided context only. You can make up projects with the skills and projects I have if the question requests a skill set related to Machine Learning, Database management or Computer sciences.", 
                        "question": query, 
                        "chat_history": st.session_state['history']})
    
    # Check if the result is a valid JSON
    if is_valid_json(result["answer"]):              
        data = json.loads(result["answer"])
    else:
        data = json.loads('{"answered":"false", "response":"Hmm... Something is not right. I\'m experiencing technical difficulties. Try asking your question again or ask another question about Ajitesh\'s professional background and qualifications. Thank you for your understanding.", "questions":["What is Ajitesh\'s professional experience?","What projects has Ajitesh worked on?","What are Ajitesh\'s career goals?"]}')
    
    answered = data.get("answered")
    response = data.get("response")
    questions = data.get("questions")

    full_response="--"

    # Append user query and bot response to chat history
    st.session_state['history'].append((query, response))
    
    # Process the response based on the answer status
    if ('I am tuned to only answer questions' in response) or (response == ""):
        full_response = """Unfortunately, I can't answer this question. My capabilities are limited to providing information about Ajitesh's professional background and qualifications. If you have other inquiries, I recommend reaching out to Ajitesh on [LinkedIn](https://www.linkedin.com/in/ajitesh-goswami/). I can answer questions like: \n - What is Ajitesh's educational background? \n - Can you list Ajitesh's professional experience? \n - What skills does Ajitesh possess? \n"""
        store_conversation(st.session_state["uuid"], query, full_response, answered)
    else: 
        markdown_list = ""
        for item in questions:
            markdown_list += f"- {item}\n"
        full_response = response + "\n\n What else would you like to know about Ajitesh? You can ask me: \n" + markdown_list
        store_conversation(st.session_state["uuid"], query, full_response, answered)
    return(full_response)

# Initialize session variables if not already present
if "uuid" not in st.session_state:
    st.session_state["uuid"] = str(uuid.uuid4())

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        welcome_message = """
            Welcome! I'm **Resume Bot**, a virtual assistant designed to provide comprehensive insights into Ajitesh's impressive background and qualifications. I have in-depth knowledge of his academic achievements, professional experiences, technical skills, and career aspirations. 

            Feel free to inquire about any aspect of Ajitesh's profile, such as his educational journey, internships, professional projects, areas of expertise in data science and AI, or his future goals. I can elaborate on topics like:

                - His Master's in Business Analytics with a focus on Data Science from UTD
                - His hands-on experience developing AI solutions like Generative models and applying techniques like regularized linear modeling
                - His proven track record in roles at companies like Daifuku, Flipkart, and Walmart
                - His proficiency in programming languages, ML frameworks, data visualization, and cloud platforms
                - His passion for leveraging transformative technologies to drive innovation and positive societal impact

            I'm here to provide you with a comprehensive understanding of Ajitesh's unique qualifications and capabilities. What would you like to know first? I'm ready to answer your questions in detail.
            """
        message_placeholder.markdown(welcome_message)

if 'history' not in st.session_state:
    st.session_state['history'] = []

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Process user input and display bot response
if prompt := st.chat_input("Ask me about Ajitesh"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        user_input=prompt
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        full_response = conversational_chat(user_input)
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
