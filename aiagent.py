import streamlit as st
from langflow.load import run_flow_from_json

# Define the tweaks
TWEAKS = {
    "ChatInput-SwYLi": {},
    "CSVAgent-8XYIT": {},
    "OpenAIModel-Fouot": {},
    "ChatOutput-X7ZfJ": {},
    "CSVAgent-LnypR": {}
}

# Streamlit App Title
st.title("LangFlow CSV AI Agent")

# File Uploader for JSON file
uploaded_file = st.file_uploader("Upload the LangFlow JSON configuration file:", type=["json"])

# Text Input for message
input_message = st.text_input("Enter your input message:")

# Session ID Input (Optional)
session_id = st.text_input("Enter a session ID (optional):", value="")

# Fallback to Env Vars Checkbox
fallback_to_env_vars = st.checkbox("Fallback to environment variables", value=True)

# Run Button
if st.button("Run Flow"):
    if uploaded_file and input_message:
        # Read the JSON content
        flow = uploaded_file.read()

        try:
            # Run the flow
            result = run_flow_from_json(
                flow=flow,
                input_value=input_message,
                session_id=session_id,
                fallback_to_env_vars=fallback_to_env_vars,
                tweaks=TWEAKS
            )
            # Display the result
            st.success("Flow executed successfully!")
            st.json(result)
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please upload a JSON configuration file and enter a message.")
