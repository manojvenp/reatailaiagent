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
FLOW_ID = "5ba09942-3a83-4595-a664-14ade12f8134"
APPLICATION_TOKEN = "AstraCS:ZUXAWTcFXYdodnMdIYcsjZMC:266882672274485e1a046b741297a6c6f55949c520793ff9941d029732414e46"  # Replace with your actual token
ENDPOINT = FLOW_ID  # Default endpoint to FLOW_ID

# Default tweaks
TWEAKS = {
    "ChatInput-SwYLi": {},
    "CSVAgent-8XYIT": {},
    "OpenAIModel-Fouot": {},
    "ChatOutput-X7ZfJ": {},
    "CSVAgent-LnypR": {},
}

# Function to run the flow
def run_flow(
    message: str,
    endpoint: str,
    output_type: str = "chat",
    input_type: str = "chat",
    tweaks: Optional[dict] = None,
    application_token: Optional[str] = None,
) -> str:
    """
    Run a flow with a given message and optional tweaks.
    Returns only the AI response message.
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

    # Parse the response to extract the AI message
    response_data = response.json()
    ai_message = response_data.get("output", {}).get("response", "No AI response received.")
    return ai_message

# Streamlit App
st.title("🎈 Doorsharp Retail AI Agent")
st.write(
    "Query the current product ranges to find insights from brands such as Ralph Lauren, Jimmy Choo, Michael Kors, and more."
)

# Input widgets for user interaction
application_token = st.text_input(
    "Enter your Application Token:", 
    placeholder="Replace with your application token...",
    value=APPLICATION_TOKEN,
)
message = st.text_input("Enter your query:", placeholder="Type your question here...")
custom_tweaks = st.text_area(
    "Optional Tweaks (JSON format):",
    value=json.dumps(TWEAKS, indent=2),
)
endpoint = st.text_input("Flow Endpoint (optional):", value=ENDPOINT)
run_query = st.button("Run Query")

# Main logic to handle query submission
if run_query:
    if not application_token.strip():
        st.error("Please enter a valid application token.")
    elif not message.strip():
        st.error("Please enter a query.")
    else:
        try:
            # Parse custom tweaks
            tweaks = json.loads(custom_tweaks) if custom_tweaks else TWEAKS

            # Run the API flow and get the AI response
            ai_response = run_flow(
                message=message,
                endpoint=endpoint,
                tweaks=tweaks,
                application_token=application_token.strip(),
            )

            # Display the AI response
            st.subheader("AI Response")
            st.markdown(f"**AI:** {ai_response}")

        except Exception as e:
            st.error(f"An error occurred: {e}")
