from langflow.load import run_flow_from_json
TWEAKS = {
  "ChatInput-SwYLi": {},
  "CSVAgent-8XYIT": {},
  "OpenAIModel-Fouot": {},
  "ChatOutput-X7ZfJ": {},
  "CSVAgent-LnypR": {}
}

result = run_flow_from_json(flow="Doorsharp AI Agent (CSV) (1).json",
                            input_value="message",
                            session_id="", # provide a session id if you want to use session state
                            fallback_to_env_vars=True, # False by default
                            tweaks=TWEAKS)
