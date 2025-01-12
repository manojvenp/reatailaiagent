# Requirements: pip install streamlit streamlit_chat requests langflow -Uq
import streamlit as st
import requests
import json
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
APPLICATION_TOKEN = "AstraCS:nwgnGlLevedmscQRsGshCtBo:1f12ca247aa4dd200b476f5d10ec5a316baf43841a1a6768fff41602225af265"
ENDPOINT = ""  # You can set a specific endpoint name in the flow settings

# Tweaks Dictionary
TWEAKS = {
    "ChatInput-MzRi4": {},
    "CSVAgent-2XO10": {},
    "OpenAIModel-lcA7a": {},
    "ChatOutput-t7BA3": {},
    "CSVAgent-E5Cj5": {}
}

# Helper function to run flow
def run_flow(message: str,
             endpoint: str,
             output_type: str = "chat",
             input_type: str = "chat",
             tweaks: Optional[dict] = None,
             application_token: Optional[str] = None) -> dict:
    """
    Run a flow with a given message and optional tweaks.
    """
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"
    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = {"Authorization": f"Bearer {application_token}", "Content-Type": "application/json"} if application_token else None
    if tweaks:
        payload["tweaks"] = tweaks
    response = requests.post(api_url, json=payload, headers=headers)
    if response.status_code != 200:
        return {"error": f"Failed to connect to the API: {response.text}"}
    return response.json()

# Streamlit App
def streamlit_app():
    st.title("Langflow Streamlit App")
    st.markdown("Run your Langflow with customized inputs and tweaks.")

    # User Inputs
    message = st.text_area("Input Message", placeholder="Enter your message here...")
    endpoint = st.text_input("Flow Endpoint", value=ENDPOINT or FLOW_ID)
    tweaks = st.text_area("Flow Tweaks (JSON)", value=json.dumps(TWEAKS, indent=2))
    output_type = st.selectbox("Output Type", options=["chat", "text", "json"], index=0)
    input_type = st.selectbox("Input Type", options=["chat", "text"], index=0)
    upload_path = st.file_uploader("Upload File (Optional)", type=["csv", "txt", "json"])
    components = st.text_input("Components to Upload File To (Optional)")

    # Run Button
    if st.button("Run Flow"):
        try:
            parsed_tweaks = json.loads(tweaks)
        except json.JSONDecodeError:
            st.error("Invalid JSON in Tweaks field.")
            return

        if upload_path:
            if not upload_file:
                st.error("Langflow is not installed. Please install it to use the upload_file function.")
                return
            elif not components:
                st.error("Please provide components to upload the file.")
                return
            parsed_tweaks = upload_file(file_path=upload_path, host=BASE_API_URL, flow_id=endpoint, components=components, tweaks=parsed_tweaks)

        response = run_flow(
            message=message,
            endpoint=endpoint,
            output_type=output_type,
            input_type=input_type,
            tweaks=parsed_tweaks,
            application_token=APPLICATION_TOKEN
        )

        st.json(response)

# Entry Point
if __name__ == "__main__":
    streamlit_app()
