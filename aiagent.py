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

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "0796338d-92cd-42ee-bb7f-16374bf023a1"
FLOW_ID = "64da80f1-f6b7-4fb0-9ecc-6375e25a2f26"
APPLICATION_TOKEN = "AstraCS:XZMZtCrqmsamDKgvLcIweqot:cd533b4dd371118bc3e07fc54f1255abd4c6a8935fe137d7f1133f6c361f74f9"
ENDPOINT = ""  # You can set a specific endpoint name in the flow settings

# You can tweak the flow by adding a tweaks dictionary
# e.g {"OpenAI-XXXXX": {"model_name": "gpt-4"}}
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
    if response.status_code == 200:
        return response.json()
    else:
        return {"output_value": "Error: Unable to process your request. Please check the configuration or try again later."}

def main():
    st.title("LangFlow Chatbot Agent")

    # Sidebar inputs
    st.sidebar.header("Settings")
    endpoint = st.sidebar.text_input("Flow Endpoint", value=ENDPOINT or FLOW_ID)
    application_token = st.sidebar.text_input("Application Token", value=APPLICATION_TOKEN, type="password")
    tweaks_input = st.sidebar.text_area("Tweaks (JSON format)", value=json.dumps(TWEAKS))

    try:
        tweaks = json.loads(tweaks_input)
    except json.JSONDecodeError:
        st.sidebar.error("Invalid tweaks JSON string")
        tweaks = TWEAKS

    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.form("chat_form"):
        user_message = st.text_input("Your message:", key="user_message")
        submitted = st.form_submit_button("Send")

    if submitted and user_message:
        st.session_state.messages.append({"role": "user", "content": user_message})

        # Send user message to the API
        response = run_flow(
            message=user_message,
            endpoint=endpoint,
            output_type="chat",
            input_type="chat",
            tweaks=tweaks,
            application_token=application_token
        )

        # Extract chatbot response
        bot_message = response.get("output_value", "Error: Unable to generate a response.")
        st.session_state.messages.append({"role": "bot", "content": bot_message})

    # Display conversation
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**Bot:** {message['content']}")

if __name__ == "__main__":
    main()
