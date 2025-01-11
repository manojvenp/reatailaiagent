import argparse
import json
from argparse import RawTextHelpFormatter
import requests
from typing import Optional
import warnings
import streamlit as st

try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow provides a function to help you upload files to the flow. Please install langflow to use it.")
    upload_file = None

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "0796338d-92cd-42ee-bb7f-16374bf023a1"
FLOW_ID = "ebbc7577-5d82-46b0-86a2-d09ed87f5899"
APPLICATION_TOKEN = "AstraCS:gbzyvOzjIpXlbIHvNiKKDIlp:066213377115e33c8ee29d5bba99a3dbe8f3d55ed1f5b4d505d651df4c8cba14"  # Replace with actual token
ENDPOINT = ""  # Optionally set a specific endpoint

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
    "Prompt-aQnEf": {}
}

def run_flow(message: str, endpoint: str, output_type: str = "chat", input_type: str = "chat", 
             tweaks: Optional[dict] = None, application_token: Optional[str] = None) -> dict:
    """
    Run a flow with a given message and optional tweaks.
    """
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint or FLOW_ID}"
    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    if tweaks:
        payload["tweaks"] = tweaks
    headers = {"Authorization": f"Bearer {application_token}", "Content-Type": "application/json"} if application_token else None
    
    response = requests.post(api_url, json=payload, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"API call failed with status code {response.status_code}: {response.text}")
    return response.json()

def main():
    parser = argparse.ArgumentParser(description="""Run a flow with a given message and optional tweaks.
    Example:
        python <your_file>.py "your message here" --endpoint "your_endpoint" --tweaks '{"key": "value"}'
    """, formatter_class=RawTextHelpFormatter)
    
    parser.add_argument("message", type=str, help="The message to send to the flow")
    parser.add_argument("--endpoint", type=str, default=ENDPOINT or FLOW_ID, help="The ID or the endpoint name of the flow")
    parser.add_argument("--tweaks", type=str, help="JSON string representing the tweaks to customize the flow", default=json.dumps(TWEAKS))
    parser.add_argument("--application_token", type=str, default=APPLICATION_TOKEN, help="Application Token for authentication")
    parser.add_argument("--output_type", type=str, default="chat", help="The output type (default: chat)")
    parser.add_argument("--input_type", type=str, default="chat", help="The input type (default: chat)")
    parser.add_argument("--upload_file", type=str, help="Path to the file to upload", default=None)
    parser.add_argument("--components", type=str, help="Components to upload the file to", default=None)
    
    args = parser.parse_args()
    try:
        tweaks = json.loads(args.tweaks)
    except json.JSONDecodeError:
        raise ValueError("Invalid tweaks JSON string")
    
    if args.upload_file:
        if not upload_file:
            raise ImportError("Langflow is not installed. Please install it to use the upload_file function.")
        if not args.components:
            raise ValueError("You need to provide the components to upload the file to.")
        tweaks = upload_file(file_path=args.upload_file, host=BASE_API_URL, flow_id=FLOW_ID, components=args.components, tweaks=tweaks)
    
    response = run_flow(
        message=args.message,
        endpoint=args.endpoint,
        output_type=args.output_type,
        input_type=args.input_type,
        tweaks=tweaks,
        application_token=args.application_token
    )
    
    print(json.dumps(response, indent=2))

if __name__ == "__main__":
    main()
