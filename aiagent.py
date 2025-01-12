def main():
    st.title("Langflow Chatbot Agent")

    # Input fields for the Streamlit app
    message = st.text_area("You:", "Enter your message here")
    endpoint = st.text_input("Endpoint", ENDPOINT or FLOW_ID)
    output_type = st.selectbox("Output Type", ["chat", "text", "json"], index=0)
    input_type = st.selectbox("Input Type", ["chat", "text", "json"], index=0)

    tweaks_input = st.text_area("Tweaks (JSON format)", json.dumps(TWEAKS, indent=2))
    application_token = st.text_input("Application Token", APPLICATION_TOKEN, type="password")

    upload_file_path = st.file_uploader("Upload File", type=["csv", "txt", "json", "xlsx"])
    components = st.text_input("Components (if uploading a file)")

    # Parse tweaks input
    try:
        tweaks = json.loads(tweaks_input)
    except json.JSONDecodeError:
        st.error("Invalid tweaks JSON format. Please correct it.")
        return

    # Handle file upload if applicable
    if upload_file_path and upload_file:
        if not components:
            st.error("You need to provide components to upload the file to.")
            return
        tweaks = upload_file(
            file_path=upload_file_path,
            host=BASE_API_URL,
            flow_id=ENDPOINT,
            components=components,
            tweaks=tweaks
        )

    if st.button("Send Message"):
        with st.spinner("Waiting for response..."):
            try:
                response = run_flow(
                    message=message,
                    endpoint=endpoint,
                    output_type=output_type,
                    input_type=input_type,
                    tweaks=tweaks,
                    application_token=application_token
                )

                st.success("Response received!")
                
                # Display chatbot-style conversation
                chat_container = st.container()
                with chat_container:
                    st.markdown(f"**You:** {message}")
                    
                    # Ensure the response is in the correct format
                    if isinstance(response, dict) and "response" in response:
                        if isinstance(response["response"], dict):
                            agent_name = response["response"].get("agent_name", "Agent")
                            agent_message = response["response"].get("message", "No message returned by the agent.")
                            st.markdown(f"**{agent_name}:** {agent_message}")
                        else:
                            st.markdown("**Agent:** Response is not in the expected format.")
                            st.json(response)
                    else:
                        st.markdown("**Agent:** Unexpected response format.")
                        st.json(response)

            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
