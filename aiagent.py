import streamlit as st
import json
import requests
from typing import Optional
import warnings

# Optional dependency for uploading files
try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow is not installed. Install it to use the `upload_file` function.")
    upload_file = None

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "0796338d-92cd-42ee-bb7f-16374bf023a1"
FLOW_ID = "ebbc7577-5d82-46b0-86a2-d09ed87f5899"
APPLICATION_TOKEN = "AstraCS:ccwhFzZJoQbwKEhbUOfUAOpS:87a102c2427e13b2e47bda8d3cef3e64560c4805886be5f100af165fb468bc91"
ENDPOINT = "https://3b0dfb4d-199d-4ec9-893d-515833aa113f-westus3.apps.astra.datastax.com"

TWEAKS = {
    "Prompt-m9oac": {},
    "ChatInput-7oqin": {},
    "ChatOutput-fFbtg": {},
    "Prompt-yPzh9": {},
    "TavilyAISearch-Otsxw": {},
    "OpenAIModel-mQvNb": {},
    "OpenAIModel-qyNbj": {},
    "Agent-Nj0pH": {},
    "Prompt-ntUg4": {},
    "Prompt-aQnEf": {},
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
        headers = {
            "Authorization": "Bearer " + application_token,
            "Content-Type": "application/json",
        }
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()


# Streamlit App
st.title("🎈 Doorsharp Retail AI Agent")
st.write(
    "Query the current product ranges to find insights from brands such as Ralph Lauren, Jimmy Choo, Michael Kors, and Nordstrom Rack."
)

# Input widgets
message = st.text_input("Enter your query:")
custom_tweaks = st.text_area(
    "Optional Tweaks (JSON format):",
    value=json.dumps(TWEAKS, indent=2),
)
run_query = st.button("Run Query")

if run_query:
    try:
        tweaks = json.loads(custom_tweaks) if custom_tweaks else TWEAKS
        response = run_flow(
            message=message,
            endpoint=ENDPOINT,
            tweaks=tweaks,
            application_token=APPLICATION_TOKEN,
        )

        # Extract AI message from the response
        ai_message = response.get("output", {}).get("response", "No response received.")
        
        # Display the AI response in a chat-like interface
        st.subheader("Chat")
        st.markdown(f"**You:** {message}")
        st.markdown(f"**AI:** {ai_message}")

    except Exception as e:
        st.error(f"An error occurred: {e}")
