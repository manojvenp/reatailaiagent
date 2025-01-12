import streamlit as st
import json
import requests
from typing import Optional
import warnings

try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow provides a function to help you upload files to the flow. Please install langflow to use it.")
    upload_file = None

# Constants
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "0796338d-92cd-42ee-bb7f-16374bf023a1"
FLOW_ID = "64da80f1-f6b7-4fb0-9ecc-6375e25a2f26"
APPLICATION_TOKEN = "AstraCS:nwgnGlLevedmscQRsGshCtBo:1f12ca247aa4dd200b476f5d10ec5a316baf43841a1a6768fff41602225af265"
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
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if application_token:
        headers = {"Authorization": "Bearer " + application_token, "Content-Type": "application/json"}
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

# Streamlit app
def main():
    st.set_page_config(page_title="Conversational Retrieval QA Chatbot", page_icon=":speech_balloon:")

    st.title("Conversational Retrieval QA Chatbot")

    # Sidebar inputs
    st.sidebar.header("Flow Configuration")
    endpoint = st.sidebar.text_input("Endpoint Name/ID", ENDPOINT or FLOW_ID)
    application_token = st.sidebar.text_input("Application Token", APPLICATION_TOKEN, type="password")

    tweaks_input = st.sidebar.text_area("Tweaks (JSON Format)", json.dumps(TWEAKS, indent=2))
    try:
        tweaks = json.loads(tweaks_input)
    except json.JSONDecodeError:
        st.sidebar.error("Invalid tweaks JSON format.")
        tweaks = None

    # Chat interface
    st.write("### Chat Interface")
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            st.write(f"**You:** {msg['content']}")
        else:
            st.write(f"**Bot:** {msg['content']}")

    # Input box
    user_input = st.text_input("Your message:", "", key="user_input")
    if st.button("Send") and user_input.strip():
        st.session_state["messages"].append({"role": "user", "content": user_input})

        try:
            response = run_flow(
                message=user_input,
                endpoint=endpoint,
                tweaks=tweaks,
                application_token=application_token
            )

            bot_response = response.get("result", "Sorry, no response available.")
            st.session_state["messages"].append({"role": "bot", "content": bot_response})

        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
