# Note: Replace **<YOUR_APPLICATION_TOKEN>** with your actual Application token

import argparse
import json
from argparse import RawTextHelpFormatter
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
FLOW_ID = "5ba09942-3a83-4595-a664-14ade12f8134"
APPLICATION_TOKEN = "AstraCS:ZUXAWTcFXYdodnMdIYcsjZMC:266882672274485e1a046b741297a6c6f55949c520793ff9941d029732414e46"
ENDPOINT = ""  # You can set a specific endpoint name in the flow settings

# Default tweaks
TWEAKS = {
    "ChatInput-SwYLi": {},
    "CSVAgent-8XYIT": {},
    "OpenAIModel-Fouot": {},
    "ChatOutput-X7ZfJ": {},
    "CSVAgent-LnypR": {},
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

    :param message: The message to send to the flow
    :param endpoint: The ID or the endpoint name of the flow
    :param output_type: The output type (default is 'chat')
    :param input_type: The input type (default is 'chat')
    :param tweaks: Optional tweaks to customize the flow
    :param application_token: Application Token for authentication
    :return: The JSON response from the flow
    """
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    if tweaks:
        payload["tweaks"] = tweaks

    headers = {"Authorization": f"Bearer {application_token}", "Content-Type": "application/json"} if application_token else None

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Request failed: {e}")

    try:
        return response.json()
    except json.JSONDecodeError:
        raise ValueError("Failed to decode JSON response from the API")

def main():
    parser = argparse.ArgumentParser(
        description="""Run a flow with a given message and optional tweaks.
Run it like: python <your file>.py "your message here" --endpoint "your_endpoint" --tweaks '{"key": "value"}'""",
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument("message", type=str, help="The message to send to the flow")
    parser.add_argument("--endpoint", type=str, default=ENDPOINT or FLOW_ID, help="The ID or the endpoint name of the flow")
    parser.add_argument("--tweaks", type=str, help="JSON string representing the tweaks to customize the flow", default=json.dumps(TWEAKS))
    parser.add_argument("--application_token", type=str, default=APPLICATION_TOKEN, help="Application Token for authentication")
    parser.add_argument("--output_type", type=str, default="chat", help="The output type")
    parser.add_argument("--input_type", type=str, default="chat", help="The input type")
    parser.add_argument("--upload_file", type=str, help="Path to the file to upload", default=None)
    parser.add_argument("--components", type=str, help="Components to upload the file to", default=None)

    args = parser.parse_args()

    # Parse tweaks JSON
    try:
        tweaks = json.loads(args.tweaks)
    except json.JSONDecodeError:
        raise ValueError("Invalid tweaks JSON string")

    # Handle file upload
    if args.upload_file:
        if not upload_file:
            raise ImportError("Langflow is not installed. Please install it to use the upload_file function.")
        if not args.components:
            raise ValueError("You need to provide the components to upload the file to.")
        tweaks = upload_file(file_path=args.upload_file, host=BASE_API_URL, flow_id=args.endpoint, components=args.components, tweaks=tweaks)

    # Run the flow
    try:
        response = run_flow(
            message=args.message,
            endpoint=args.endpoint,
            output_type=args.output_type,
            input_type=args.input_type,
            tweaks=tweaks,
            application_token=args.application_token,
        )
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
