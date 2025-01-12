import streamlit as st
import json
import requests
import warnings
from typing import Optional

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "0796338d-92cd-42ee-bb7f-16374bf023a1"
FLOW_ID = "749ae8cd-5da3-48a6-898d-f8176efccde3"
APPLICATION_TOKEN = "AstraCS:tZSxGCDKMCQPcywroyFqtPYf:cc6d4a7eec6eb9cd6e2e5448135639bca018efb4b56a122c9dc9d486ce0e81a4"
ENDPOINT = ""

TWEAKS = {
    "ChatInput-dF1W6": {},
    "CSVAgent-j14bM": {},
    "OpenAIModel-jJgAC": {},
    "ChatOutput-WIoTA": {}
}

def run_flow(message: str, endpoint: str, output_type: str = "chat", input_type: str = "chat",
             tweaks: Optional[dict] = None, application_token: Optional[str] = None) -> dict:
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"
    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = {"Authorization": "Bearer " + application_token, "Content-Type": "application/json"} if application_token else None
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def parse_openai_response(response: dict) -> str:
    if not isinstance(response, dict):
        return "Response is not a valid dictionary."

    if "error" in response:
        return f"Error: {response['error']}"

    chat_response = response.get("response", {})
    st.write("Chat Response:", chat_response)  # Debugging
    chat_messages = chat_response.get("messages", [])
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

    message = st.text_area("You:", "Enter your message here")
    endpoint = st.text_input("Endpoint", ENDPOINT or FLOW_ID)
    output_type = st.selectbox("Output Type", ["chat", "text", "json"], index=0)
    input_type = st.selectbox("Input Type", ["chat", "text", "json"], index=0)

    tweaks_input = st.text_area("Tweaks (JSON format)", json.dumps(TWEAKS, indent=2))
    application_token = st.text_input("Application Token", APPLICATION_TOKEN, type="password")

    try:
        tweaks = json.loads(tweaks_input)
    except json.JSONDecodeError:
        st.error("Invalid tweaks JSON format. Please correct it.")
        return

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
                st.write("Raw Response:", response)  # Debugging
                formatted_conversation = parse_openai_response(response)
                st.markdown(formatted_conversation)
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                st.write("Debug Info:", e)

if __name__ == "__main__":
    main()
