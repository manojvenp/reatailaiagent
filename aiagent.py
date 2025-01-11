import streamlit as st
import requests
import json
import warnings
from typing import Optional

try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow is not installed. Please install it to use it.")
    upload_file = None

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "0796338d-92cd-42ee-bb7f-16374bf023a1"
FLOW_ID = "92baaca1-5991-49ba-a756-e15232ca8777"
APPLICATION_TOKEN = "AstraCS:yXAXhwqWnlZgXlkKWROTGUjm:e4c45611600fdf70f58188e30846ca96a01dc60736f7202f1ba4e75509b52994"
ENDPOINT = "https://3b0dfb4d-199d-4ec9-893d-515833aa113f-westus3.apps.astra.datastax.com"

# Default tweaks
TWEAKS = {
    "ChatInput-cmtYv": {},
    "CSVAgent-2w2T1": {},
    "OpenAIModel-Cyo9k": {},
    "ChatOutput-AFgrz": {},
    "CSVAgent-OPFGv": {}
}

def run_flow(message: str,
  endpoint: str,
  output_type: str = "chat",
  input_type: str = "chat",
  tweaks: Optional[dict] = None,
  application_token: Optional[str] = None) -> str:
    """
    Run a flow with a given message and optional tweaks.
    :param message: The message to send to the flow
    :param endpoint: The ID or the endpoint name of the flow
    :param tweaks: Optional tweaks to customize the flow
    :return: The AI message response
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
    
    # Check if the response is successful and extract the AI response message
    if response.status_code == 200:
        data = response.json()
        # Assuming the message is under a key like 'message' or similar, you need to inspect the actual response structure.
        ai_message = data.get("message", "No response message found.")
        return ai_message
    else:
        return f"Error: {response.status_code}, {response.text}"

# Streamlit interface
st.title("🎈 Doorsharp Retail AI Agent")
st.write("You can query on the current product ranges to find interesting insights from brands such as Ralph Lauren, Jimmy Choo, Michael Kors, and Nordstrom Rack.")

# User input section for the Streamlit app
message = st.text_area("Enter your message:", "Tell me about Ralph Lauren's latest collection.")
output_type = st.selectbox("Select Output Type", ["chat", "json"])
input_type = st.selectbox("Select Input Type", ["chat", "text"])

# Allow customization of tweaks
tweaks_input = st.text_area("Enter any tweaks (JSON format):", json.dumps(TWEAKS))
tweaks = json.loads(tweaks_input)

# Allow submission
if st.button("Run Query"):
    # Optionally pass in a custom application token
    ai_message_response = run_flow(message=message, endpoint=FLOW_ID, output_type=output_type, input_type=input_type, tweaks=tweaks, application_token=APPLICATION_TOKEN)
    st.write("AI Message Response:")
    st.write(ai_message_response)
