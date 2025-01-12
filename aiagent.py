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

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "0796338d-92cd-42ee-bb7f-16374bf023a1"
FLOW_ID = "749ae8cd-5da3-48a6-898d-f8176efccde3"
APPLICATION_TOKEN = "AstraCS:tZSxGCDKMCQPcywroyFqtPYf:cc6d4a7eec6eb9cd6e2e5448135639bca018efb4b56a122c9dc9d486ce0e81a4"
ENDPOINT = ""  # You can set a specific endpoint name in the flow settings

TWEAKS = {
    "ChatInput-dF1W6": {},
    "CSVAgent-j14bM": {},
    "OpenAIModel-jJgAC": {},
    "ChatOutput-WIoTA": {}
}

def run_flow(message: str, endpoint: str, output_type: str = "chat", input_type: str = "chat",
             tweaks: Optional[dict] = None, application_token: Optional[str] = None) -> dict:
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

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def parse_openai_response(response: dict) -> str:
    """
    Parse OpenAI chat response format to extract and format the content.

    :param response: The response dictionary from the OpenAI model
    :return: A formatted string of the conversation
    """
    if not isinstance(response, dict):
        return "Response is not a valid dictionary."

    if "error" in response:
        return f"Error: {response['error']}"

    chat_messages = response.get("response", {}).get("messages", [])
    if not isinstance(chat_messages, list):
        return "No valid chat messages found in the response."

    formatted_conversation = ""
    for message in chat_messages:
        role = message.get("role", "unknown").capitalize()
        content = message.get("content", "No content provided.")
        formatted_conversation += f"**{role}:** {content}\n\n"
    return formatted_conversation.strip()

def main():
    st.title("Langflow Chatbot Agent")

    # Input fields for the Streamlit app
    message = st.text_area("You:", "Enter your message here")
    endpoint = st.text_input("Endpoint", ENDPOINT or FLOW_ID)
    output_type = st.selectbox("Output Type", ["chat", "text", "json"], index=0)
    input_type = st.selectbox("Input Type", ["chat", "text", "json"], index=0)

    tweaks_input = st.text_area("Tweaks (JSON format)", json.dumps(TWEAKS, indent=2))
    application_token = st.text_input("Application Token", APPLICATION_TOKEN, type="password")

    upload_file_path = st.file_uploader("Upload File", type=["csv", "txt", "json", "xlsx"])
    components = st.text_input("Components (if uploading a file)")

    # Parse tweaks input
    try:
        tweaks = json.loads(tweaks_input)
    except json.JSONDecodeError:
        st.error("Invalid tweaks JSON format. Please correct it.")
        return

    # Handle file upload if applicable
    if upload_file_path and upload_file:
        if not components:
            st.error("You need to provide components to upload the file to.")
            return
        tweaks = upload_file(
            file_path=upload_file_path,
            host=BASE_API_URL,
            flow_id=ENDPOINT,
            components=components,
            tweaks=tweaks
        )

    if st.button("Send Message"):
        with st.spinner("Waiting for response..."):
            try:
                response = run_flow(
                    message=message,
                    endpoint=endpoint,
                    output_type=output_type,
                    input_type=input_type,
                    tweaks=tweaks,
                    application_token=application_token
                )

                st.success("Response received!")

                # Display chatbot-style conversation
                chat_container = st.container()
                with chat_container:
                    st.markdown(f"**You:** {message}")
                    
                    formatted_conversation = parse_openai_response(response)
                    st.markdown(formatted_conversation)

            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
