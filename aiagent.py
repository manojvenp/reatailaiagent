import json
import requests
import streamlit as st
import warnings
from typing import Optional

try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow provides a function to help you upload files to the flow. Please install langflow to use it.")
    upload_file = None

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "0796338d-92cd-42ee-bb7f-16374bf023a1"
FLOW_ID = "5ba09942-3a83-4595-a664-14ade12f8134"
APPLICATION_TOKEN = "AstraCS:UInhwxyOxGURqKPjlLsQlbNn:b9f539abeda1ca9e8bcf294bddb7c6b1bc38c6cd9488b6bf182841adc8e28f1d"
ENDPOINT = ""  # You can set a specific endpoint name in the flow settings

TWEAKS = {
    "ChatInput-SwYLi": {},
    "CSVAgent-8XYIT": {},
    "OpenAIModel-Fouot": {},
    "ChatOutput-X7ZfJ": {},
    "CSVAgent-LnypR": {}
}


def run_flow(message: str, endpoint: str, output_type: str = "chat", input_type: str = "chat",
             tweaks: Optional[dict] = None, application_token: Optional[str] = None) -> dict:
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
        headers = {"Authorization": "Bearer " + application_token, "Content-Type": "application/json"}

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error during API call: {e}")
        return {"error": str(e)}
    except json.JSONDecodeError:
        st.error("Invalid JSON response received from API.")
        return {"error": "Invalid JSON response"}


def main():
    st.title("LangFlow API Runner")
    
    # User input for message and endpoint
    message = st.text_input("Enter your message:")
    endpoint = st.text_input("Enter the endpoint (Flow ID or Endpoint name):", value=ENDPOINT or FLOW_ID)

    # File upload for tweaks or additional data
    uploaded_file = st.file_uploader("Upload a file (optional):")
    tweaks_input = st.text_area("Enter Tweaks (JSON format):", value=json.dumps(TWEAKS))

    # Parse tweaks
    try:
        tweaks = json.loads(tweaks_input)
    except json.JSONDecodeError:
        st.error("Invalid tweaks JSON string")
        tweaks = {}

    if uploaded_file:
        if not upload_file:
            st.error("Langflow is not installed. Please install it to use the upload_file function.")
        else:
            tweaks = upload_file(
                file_path=uploaded_file.name,
                host=BASE_API_URL,
                flow_id=endpoint,
                components=None,  # Update if you want to provide specific components
                tweaks=tweaks
            )

    # Run the flow
    if st.button("Run Flow"):
        if message and endpoint:
            response = run_flow(
                message=message,
                endpoint=endpoint,
                tweaks=tweaks,
                application_token=APPLICATION_TOKEN
            )
            st.json(response)
        else:
            st.error("Please provide both a message and an endpoint.")


if __name__ == "__main__":
    main()
