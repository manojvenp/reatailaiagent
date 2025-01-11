import streamlit as st
import requests
import json
import warnings
from typing import Optional

# Importing the upload_file function if Langflow is installed
try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow is not installed. Please install it to use it.")
    upload_file = None

# Constants
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "0796338d-92cd-42ee-bb7f-16374bf023a1"
FLOW_ID = "92baaca1-5991-49ba-a756-e15232ca8777"
APPLICATION_TOKEN = "AstraCS:xCRzxHhsdwLhnHtETRlryFzq:a50b4deb021d429a76a00974145ded90b9deaf5a62b90d81d6d1b6af42535ff6"

# Default tweaks (hidden in UI)
TWEAKS = {
    "ChatInput-cmtYv": {},
    "CSVAgent-2w2T1": {},
    "OpenAIModel-Cyo9k": {},
    "ChatOutput-AFgrz": {},
    "CSVAgent-OPFGv": {}
}

# Function to run the flow
def run_flow(message: str,
             endpoint: str,
             application_token: Optional[str] = None) -> str:
    """
    Run a flow with a given message.
    :param message: The message to send to the flow
    :param endpoint: The ID or the endpoint name of the flow
    :param application_token: Optional application token for authentication
    :return: The AI message response
    """
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"

    payload = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat",
        "tweaks": TWEAKS
    }
    headers = {"Authorization": "Bearer " + application_token, "Content-Type": "application/json"}
    
    response = requests.post(api_url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        ai_message = data.get("message", "No response message found.")
        return ai_message
    else:
        return f"Error: {response.status_code}, {response.text}"

# Streamlit interface
st.title("Doorsharp Retail AI Agent")
st.write("Ask about the latest collections or insights from brands like Ralph Lauren, Jimmy Choo, Michael Kors, and Nordstrom Rack.")

# User input
message = st.text_area("Enter your query:", "Tell me about Ralph Lauren's latest collection.")

# Run query button
if st.button("Run Query"):
    with st.spinner("Querying the AI..."):
        try:
            ai_message_response = run_flow(message=message, endpoint=FLOW_ID, application_token=APPLICATION_TOKEN)
            st.success("Response received!")
            st.write("**AI Response:**")
            st.write(ai_message_response)
        except Exception as e:
            st.error(f"An error occurred: {e}")
