# Note: Replace **<YOUR_APPLICATION_TOKEN>** with your actual Application token

import argparse
import json
import requests
import warnings
from argparse import RawTextHelpFormatter
from typing import Optional

try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow provides a function to help you upload files to the flow. Please install langflow to use it.")
    upload_file = None

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "0796338d-92cd-42ee-bb7f-16374bf023a1"
FLOW_ID = "64da80f1-f6b7-4fb0-9ecc-6375e25a2f26"
APPLICATION_TOKEN = "AstraCS:XZMZtCrqmsamDKgvLcIweqot:cd533b4dd371118bc3e07fc54f1255abd4c6a8935fe137d7f1133f6c361f74f9"  # Replace with your application token
ENDPOINT = ""  # You can set a specific endpoint name in the flow settings

# Default tweaks dictionary
TWEAKS = {
    "ChatInput-MzRi4": {},
    "CSVAgent-2XO10": {},
    "OpenAIModel-lcA7a": {},
    "ChatOutput-t7BA3": {},
    "CSVAgent-E5Cj5": {}
}

def run_flow(
    message: str,
    endpoint: str,
    output_type: str = "chat",
    input_type: str = "chat",
    tweaks: Optional[dict] = None,
    application_token: Optional[str] = None
) -> dict:
    """
    Run a flow with a given message and optional tweaks.

    :param message: The message to send to the flow
    :param endpoint: The ID or the endpoint name of the flow
    :param output_type: The output type (default is "chat")
    :param input_type: The input type (default is "chat")
    :param tweaks: Optional tweaks to customize the flow
    :param application_token: Application token for authentication
    :return: The JSON response from the flow
    """
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"
    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = {}
    if tweaks:
        payload["tweaks"] = tweaks
    if application_token:
        headers = {
            "Authorization": f"Bearer {application_token}",
            "Content-Type": "application/json"
        }
    response = requests.post(api_url, json=payload, headers=headers)
    response.raise_for_status()  # Raise an HTTPError for bad responses
    return response.json()

def main():
    parser = argparse.ArgumentParser(
        description="""Run a flow with a given message and optional tweaks.
Example usage:
    python <your_file>.py "your message here" --endpoint "your_endpoint" --tweaks '{"key": "value"}'
""",
        formatter_class=RawTextHelpFormatter
    )
    parser.add_argument("message", type=str, help="The message to send to the flow")
    parser.add_argument(
        "--endpoint",
        type=str,
        default=ENDPOINT or FLOW_ID,
        help="The ID or the endpoint name of the flow"
    )
    parser.add_argument(
        "--tweaks",
        type=str,
        help="JSON string representing the tweaks to customize the flow",
        default=json.dumps(TWEAKS)
    )
    parser.add_argument(
        "--application_token",
        type=str,
        default=APPLICATION_TOKEN,
        help="Application token for authentication"
    )
    parser.add_argument(
        "--output_type",
        type=str,
        default="chat",
        help="The output type (default: chat)"
    )
    parser.add_argument(
        "--input_type",
        type=str,
        default="chat",
        help="The input type (default: chat)"
    )
    parser.add_argument(
        "--upload_file",
        type=str,
        help="Path to the file to upload",
        default=None
    )
    parser.add_argument(
        "--components",
        type=str,
        help="Components to upload the file to",
        default=None
    )

    args = parser.parse_args()
    
    # Parse tweaks JSON string
    try:
        tweaks = json.loads(args.tweaks)
    except json.JSONDecodeError:
        raise ValueError("Invalid tweaks JSON string")

    # Handle file upload if specified
    if args.upload_file:
        if not upload_file:
            raise ImportError("Langflow is not installed. Please install it to use the upload_file function.")
        if not args.components:
            raise ValueError("You need to provide the components to upload the file to.")
        tweaks = upload_file(
            file_path=args.upload_file,
            host=BASE_API_URL,
            flow_id=FLOW_ID,
            components=args.components,
            tweaks=tweaks
        )

    # Run the flow and print the response
    try:
        response = run_flow(
            message=args.message,
            endpoint=args.endpoint,
            output_type=args.output_type,
            input_type=args.input_type,
            tweaks=tweaks,
            application_token=args.application_token
        )
        print(json.dumps(response, indent=2))
    except requests.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
