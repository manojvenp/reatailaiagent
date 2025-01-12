from langflow.load import run_flow_from_json
TWEAKS = {
  "ChatInput-MzRi4": {},
  "CSVAgent-2XO10": {},
  "OpenAIModel-lcA7a": {},
  "ChatOutput-t7BA3": {},
  "CSVAgent-E5Cj5": {}
}

result = run_flow_from_json(flow="Doorsharp AI Agent (CSV) (2).json",
                            input_value="message",
                            session_id="", # provide a session id if you want to use session state
                            fallback_to_env_vars=True, # False by default
                            tweaks=TWEAKS)
