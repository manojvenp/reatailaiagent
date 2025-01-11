# Note: Replace **<YOUR_APPLICATION_TOKEN>** with your actual Application token

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
APPLICATION_TOKEN = "AstraCS:XZMZtCrqmsamDKgvLcIweqot:cd533b4dd371118bc3e07fc54f1255abd4c6a8935fe137d7f1133f6c361f74f9"  # Replace with your application token
ENDPOINT = ""  # Default to FLOW_ID if not set

# Default tweaks
TWEAKS = {
    "ChatInput-MzRi4": {},
    "CSVAgent-2XO10": {},
    "OpenAIModel-lcA7a": {},
    "ChatOutput-t7BA3": {},
    "CSVAgent-E5Cj5": {}
}

# Helper Function
def run_flow(
    message: str,
    endpoint: str,
    output_type: str = "chat",
    input_type: str = "chat",
    tweaks: Optional[dict] = None,
    application_token: Optional[str] = None
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
    headers = {}
    if tweaks:
        payload["tweaks"] = tweaks
    if application_token:
        headers = {
            "Authorization": f"Bearer {application_token}",
            "Content-Type": "application/json"
        }
    response = requests.post(api_url, json=payload, headers=headers)
    response.raise_for_status()  # Raise an HTTPError for bad responses
    return response.json()

# Streamlit Chatbot App
def main():
    st.title("Langflow Chatbot")
    st.sidebar.title("Settings")

    # Sidebar inputs
    application_token = st.sidebar.text_input("Application Token", APPLICATION_TOKEN, type="password")
    endpoint = st.sidebar.text_input("Endpoint", ENDPOINT or FLOW_ID)
    tweaks_input = st.sidebar.text_area("Tweaks (JSON)", json.dumps(TWEAKS, indent=2))
    
    uploaded_file = st.sidebar.file_uploader("Upload File (optional)")
    components = st.sidebar.text_input("Components for File Upload (comma-separated)")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Display chat history
    for message in st.session_state["messages"]:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        elif message["role"] == "assistant":
            st.markdown(f"**Assistant:** {message['content']}")

    # Input form
    with st.form("chat_form", clear_on_submit=True):
        user_message = st.text_area("Your message:", key="input_message", placeholder="Type your message here...")
        submit_button = st.form_submit_button("Send")

    if submit_button and user_message.strip():
        # Add user's message to the chat history
        st.session_state["messages"].append({"role": "user", "content": user_message})

        try:
            # Parse tweaks
            tweaks = json.loads(tweaks_input)

            # Handle file upload if applicable
            if uploaded_file:
                if not upload_file:
                    st.error("Langflow is not installed. Please install it to use the upload_file function.")
                    return
                if not components:
                    st.error("You need to provide components to upload the file.")
                    return
                tweaks = upload_file(
                    file_path=uploaded_file,
                    host=BASE_API_URL,
                    flow_id=FLOW_ID,
                    components=components.split(","),
                    tweaks=tweaks
                )

            # Run flow
            response = run_flow(
                message=user_message,
                endpoint=endpoint,
                output_type="chat",
                input_type="chat",
                tweaks=tweaks,
                application_token=application_token
            )

            # Extract assistant's message from the response
            assistant_message = response.get("response", "Sorry, I couldn't process your request.")
            st.session_state["messages"].append({"role": "assistant", "content": assistant_message})

        except requests.HTTPError as e:
            st.error(f"HTTP error occurred: {e}")
        except json.JSONDecodeError:
            st.error("Invalid JSON format in Tweaks.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

    st.write("---")
    st.caption("Powered by Langflow")

if __name__ == "__main__":
    main()
