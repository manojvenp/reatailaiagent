import argparse
import json
from argparse import RawTextHelpFormatter
import requests
from typing import Optional
import warnings
import streamlit as st  # Added Streamlit import

try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow provides a function to help you upload files to the flow. Please install langflow to use it.")
    upload_file = None

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "0796338d-92cd-42ee-bb7f-16374bf023a1"
FLOW_ID = "749ae8cd-5da3-48a6-898d-f8176efccde3"
APPLICATION_TOKEN = "AstraCS:MNEidKrDroEMefsSRAWoopgS:f9104401ced7f74f684264cea0ce5577afb5f242bb39efbb4515d4f6d8864257"
ENDPOINT = ""  # Optional custom endpoint

TWEAKS = {
    "ChatInput-dF1W6": {},
    "CSVAgent-j14bM": {},
    "OpenAIModel-jJgAC": {},
    "ChatOutput-WIoTA": {}
}


def run_flow(
    message: str,
    endpoint: str = FLOW_ID,
    output_type: str = "chat",
    input_type: str = "chat",
    tweaks: Optional[dict] = None,
    application_token: Optional[str] = None
) -> dict:
    """
    Run a flow with a given message and optional tweaks.

    :param message: The message to send to the flow
    :param endpoint: The ID or the endpoint name of the flow
    :param tweaks: Optional tweaks to customize the flow
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

    headers = {"Authorization": "Bearer " + application_token, "Content-Type": "application/json"} if application_token else None
    response = requests.post(api_url, json=payload, headers=headers)

    if response.status_code != 200:
        raise ValueError(f"Error: {response.status_code}, {response.text}")
    return response.json()


def cli_interface():
    parser = argparse.ArgumentParser(
        description="""Run a flow with a given message and optional tweaks.
Run it like: python <your_file>.py "your message here" --endpoint "your_endpoint" --tweaks '{"key": "value"}'""",
        formatter_class=RawTextHelpFormatter
    )
    parser.add_argument("message", type=str, help="The message to send to the flow")
    parser.add_argument("--endpoint", type=str, default=ENDPOINT or FLOW_ID, help="The ID or the endpoint name of the flow")
    parser.add_argument("--tweaks", type=str, help="JSON string representing the tweaks to customize the flow", default=json.dumps(TWEAKS))
    parser.add_argument("--application_token", type=str, default=APPLICATION_TOKEN, help="Application Token for authentication")
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
        tweaks = upload_file(
            file_path=args.upload_file,
            host=BASE_API_URL,
            flow_id=args.endpoint,
            components=args.components,
            tweaks=tweaks
        )

    response = run_flow(
        message=args.message,
        endpoint=args.endpoint,
        tweaks=tweaks,
        application_token=args.application_token
    )
    print(json.dumps(response, indent=2))


def streamlit_interface():
    st.title("Chat Interface")
    message = st.text_area("Message", placeholder="Ask something...")

    if st.button("Run Flow"):
        if not message.strip():
            st.error("Please enter a message")
            return

        try:
            with st.spinner("Running flow..."):
                response = run_flow(
                    message=message,
                    endpoint=ENDPOINT or FLOW_ID,
                    application_token=APPLICATION_TOKEN,
                    tweaks=TWEAKS
                )
            response_text = response.get("outputs", [{}])[0].get("outputs", [{}])[0].get("results", {}).get("message", {}).get("text", "No response")
            st.markdown(response_text)
        except Exception as e:
            st.error(str(e))


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        cli_interface()
    else:
        streamlit_interface()
