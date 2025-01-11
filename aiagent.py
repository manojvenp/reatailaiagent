import streamlit as st
import json
import requests
import warnings
from typing import Optional

try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow provides a function to help you upload files to the flow. Please install langflow to use it.")
    upload_file = None

# Constants
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "0796338d-92cd-42ee-bb7f-16374bf023a1"
FLOW_ID = "64da80f1-f6b7-4fb0-9ecc-6375e25a2f26"
APPLICATION_TOKEN = "<YOUR_APPLICATION_TOKEN>"  # Replace with your actual token
ENDPOINT = ""  # Can set a specific endpoint name in flow settings

# Default tweaks
TWEAKS = {
    "ChatInput-MzRi4": {},
    "CSVAgent-2XO10": {},
    "OpenAIModel-lcA7a": {},
    "ChatOutput-t7BA3": {},
    "CSVAgent-E5Cj5": {},
}


def run_flow(
    message: str,
    endpoint: str,
    output_type: str = "chat",
    input_type: str = "chat",
    tweaks: Optional[dict] = None,
    application_token: Optional[str] = None,
) -> dict:
    """
    Run a flow with a given message and optional tweaks.
    """
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"
    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if application_token:
        headers = {"Authorization": "Bearer " + application_token, "Content-Type": "application/json"}

    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()


# Streamlit App
st.title("LangFlow Streamlit Integration")

# Inputs
message = st.text_area("Enter your message:", "")
endpoint = st.text_input("Endpoint (ID or name):", value=ENDPOINT or FLOW_ID)
application_token = st.text_input("Application Token:", value=APPLICATION_TOKEN, type="password")
output_type = st.selectbox("Output Type:", ["chat", "text", "json"], index=0)
input_type = st.selectbox("Input Type:", ["chat", "text", "json"], index=0)

# Tweaks input
tweaks_input = st.text_area("Enter tweaks (JSON format):", json.dumps(TWEAKS))
try:
    tweaks = json.loads(t
