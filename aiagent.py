import streamlit as st
import json
import requests
from typing import Optional

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "0796338d-92cd-42ee-bb7f-16374bf023a1"
FLOW_ID = "ebbc7577-5d82-46b0-86a2-d09ed87f5899"
APPLICATION_TOKEN = "AstraCS:ccwhFzZJoQbwKEhbUOfUAOpS:87a102c2427e13b2e47bda8d3cef3e64560c4805886be5f100af165fb468bc91"
ENDPOINT = "https://3b0dfb4d-199d-4ec9-893d-515833aa113f-westus3.apps.astra.datastax.com"  # You can set a specific endpoint name in the flow settings

# Tweaks (custom flow settings)
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

def run_flow(message: str,
  endpoint: str,
  output_type: str = "chat",
  input_type: str = "chat",
  tweaks: Optional[dict] = None,
  application_token: Optional[str] = None) -> dict:
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
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if application_token:
        headers = {"Authorization": "Bearer " + application_token, "Content-Type": "application/json"}
    
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

# Streamlit UI
def main():
    st.title("🎈 Doorsharp Retail AI Agent")
    st.write(
        "You can query on the current product ranges to find interesting insights from brands such as Ralph Lauren, Jimmy Choo, MichaelKors, and Nordstrom Rack."
    )

    # Input for the message (query)
    user_message = st.text_area("Enter your query", "Tell me about the latest products from Ralph Lauren")

    # Button to run the query
    if st.button("Get Insights"):
        response = run_flow(
            message=user_message,
            endpoint=ENDPOINT,
            output_type="chat",
            input_type="chat",
            tweaks=TWEAKS,
            application_token=APPLICATION_TOKEN
        )
        st.write("AI Response:")
        st.json(response)  # Display the AI response in JSON format

if __name__ == "__main__":
    main()
