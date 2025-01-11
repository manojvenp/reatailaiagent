import json
import requests
import streamlit as st
from typing import Optional
import warnings

try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow provides a function to help you upload files to the flow. Please install langflow to use it.")
    upload_file = None

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "0796338d-92cd-42ee-bb7f-16374bf023a1"
FLOW_ID = "64da80f1-f6b7-4fb0-9ecc-6375e25a2f26"
APPLICATION_TOKEN = "AstraCS:XZMZtCrqmsamDKgvLcIweqot:cd533b4dd371118bc3e07fc54f1255abd4c6a8935fe137d7f1133f6c361f74f9"
ENDPOINT = ""  # You can set a specific endpoint name in the flow settings

TWEAKS = {
    "ChatInput-MzRi4": {},
    "CSVAgent-2XO10": {},
    "OpenAIModel-lcA7a": {},
    "ChatOutput-t7BA3": {},
    "CSVAgent-E5Cj5": {}
}

def run_flow(message: str,
             endpoint: str,
             output_type: str = "chat",
             input_type: str = "chat",
             tweaks: Optional[dict] = None,
             application_token: Optional[str] = None) -> dict:
    """
    Run a flow with a given message and optional tweaks.

    :param message: The message to send to the flow
    :param endpoint: The ID or the endpoint name of the flow
    :param tweaks: Optional tweaks to customize the flow
    :return: The JSON response from the flow
    """
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    if tweaks:
        payload["tweaks"] = tweaks

    headers = None
    if application_token:
        headers = {"Authorization": "Bearer " + application_token, "Content-Type": "application/json"}

    response = requests.post(api_url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}

st.set_page_config(page_title="LangFlow Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 LangFlow Chatbot")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def display_chat_history():
    for entry in st.session_state.chat_history:
        if entry["sender"] == "user":
            st.markdown(f"**You:** {entry['message']}")
        else:
            st.markdown(f"**Bot:** {entry['message']}")

user_input = st.text_input("Enter your message:", "")
if st.button("Send") and user_input.strip():
    st.session_state.chat_history.append({"sender": "user", "message": user_input})

    response = run_flow(
        message=user_input,
        endpoint=ENDPOINT or FLOW_ID,
        tweaks=TWEAKS,
        application_token=APPLICATION_TOKEN
    )

    if "error" in response:
        bot_reply = f"Error: {response['error']}"
    else:
        bot_reply = response.get("output_value", "No response from the flow.")

    st.session_state.chat_history.append({"sender": "bot", "message": bot_reply})

display_chat_history()
