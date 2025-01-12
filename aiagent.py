# Requirements: pip install streamlit streamlit_chat -Uq
 
import logging
import sys
import time
from typing import Optional
import requests
import streamlit as st
from streamlit_chat import message
 
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=log_format, stream=sys.stdout, level=logging.INFO)
 
# Constants
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "0796338d-92cd-42ee-bb7f-16374bf023a1"
FLOW_ID = "64da80f1-f6b7-4fb0-9ecc-6375e25a2f26"
APPLICATION_TOKEN = "AstraCS:XZMZtCrqmsamDKgvLcIweqot:cd533b4dd371118bc3e07fc54f1255abd4c6a8935fe137d7f1133f6c361f74f9"  # Replace with your application token
ENDPOINT = ""  # Default to FLOW_ID if not set
# You can tweak the flow by adding a tweaks dictionary
# e.g {"OpenAI-XXXXX": {"model_name": "gpt-4"}}
TWEAKS = {
  "OpenAIEmbeddings-3OTU2": {},
  "Chroma-elGpI": {},
  "ChatOpenAI-38h1l": {"model_name": "gpt-4"},
  "ConversationalRetrievalChain-4FTbi": {},
  "ConversationBufferMemory-YTFcZ": {}
}
BASE_AVATAR_URL = (
"https://raw.githubusercontent.com/garystafford-aws/static-assets/main/static"
)
 
 
def main():
    st.set_page_config(page_title="Virtual Bartender")
 
    st.markdown("##### Welcome to the Virtual Bartender")
 
    if "messages" not in st.session_state:
        st.session_state.messages = []
 
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=message["avatar"]):
            st.write(message["content"])
 
    if prompt := st.chat_input("I'm your virtual bartender, how may I help you?"):
        # Add user message to chat history
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
                "avatar": f"{BASE_AVATAR_URL}/people-64px.png",
            }
        )
        # Display user message in chat message container
        with st.chat_message(
            "user",
            avatar=f"{BASE_AVATAR_URL}/people-64px.png",
        ):
            st.write(prompt)
 
        # Display assistant response in chat message container
        with st.chat_message(
            "assistant",
            avatar=f"{BASE_AVATAR_URL}/bartender-64px.png",
        ):
            message_placeholder = st.empty()
            with st.spinner(text="Thinking..."):
                assistant_response = generate_response(prompt)
                message_placeholder.write(assistant_response)
        # Add assistant response to chat history
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": assistant_response,
                "avatar": f"{BASE_AVATAR_URL}/bartender-64px.png",
            }
        )
 
 
def run_flow(inputs: dict, flow_id: str, tweaks: Optional[dict] = None) -> dict:
    api_url = f"{BASE_API_URL}/{flow_id}"
 
    payload = {"inputs": inputs}
 
    if tweaks:
        payload["tweaks"] = tweaks
 
response = requests.post(api_url, json=payload)
    return response.json()
 
 
def generate_response(prompt):
logging.info(f"question: {prompt}")
    inputs = {"question": prompt}
    response = run_flow(inputs, flow_id=FLOW_ID, tweaks=TWEAKS)
    try:
logging.info(f"answer: {response['result']['answer']}")
        return response["result"]["answer"]
    except Exception as exc:
        logging.error(f"error: {response}")
        return "Sorry, there was a problem finding an answer for you."
 
 
if __name__ == "__main__":
    main()
has context menu
