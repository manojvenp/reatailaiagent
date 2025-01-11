import streamlit as st
import json
import requests
import warnings
from typing import Optional

# Optional dependency for uploading files
try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow is not installed. Install it to use the `upload_file` function.")
    upload_file = None

# Constants
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "0796338d-92cd-42ee-bb7f-16374bf023a1"
FLOW_ID = "92baaca1-5991-49ba-a756-e15232ca8777"
APPLICATION_TOKEN = "sk-E08clM5IRxL-rPZ8amnd_axtSf2TIt5nUg9j_aMp144"
ENDPOINT = "https://3b0dfb4d-199d-4ec9-893d-515833aa113f-westus3.apps.astra.datastax.com"

# Default tweaks
TWEAKS = {
    "ChatInput-cmtYv": {},
    "CSVAgent-2w2T1": {},
    "OpenAIModel-Cyo9k": {},
    "ChatOutput-AFgrz": {},
    "CSVAgent-OPFGv": {},
}

# Function to run the flow
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

# Input widgets for user interaction
message = st.text_input("Enter your query:", placeholder="Type your question here...")
custom_tweaks = st.text_area(
    "Optional Tweaks (JSON format):",
    value=json.dumps(TWEAKS, indent=2),
)
run_query = st.button("Run Query")

# Main logic to handle query submission
if run_query:
    if not message.strip():
        st.error("Please enter a query before running.")
    else:
        try:
            # Parse custom tweaks
            tweaks = json.loads(custom_tweaks) if custom_tweaks else TWEAKS

            # Run the API flow
            response = run_flow(
                message=message,
                endpoint=ENDPOINT,
                tweaks=tweaks,
                application_token=APPLICATION_TOKEN,
            )

            # Extract AI message from the response
            ai_message = response.get("output", {}).get("response", "No response received.")
            
            # Display the response in a chat-like interface
            st.subheader("Chat")
            st.markdown(f"**You:** {message}")
            st.markdown(f"**AI:** {ai_message}")

        except Exception as e:
            st.error(f"An error occurred: {e}")
