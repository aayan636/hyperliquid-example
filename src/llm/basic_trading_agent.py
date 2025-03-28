
import requests
import pickle
import json

from constants.constants import BASIC_TRADING_AGENT_PROMPT, LLM_HISTORY_FILE
from trade.data_model import Strategy
from utils import config_reader

class BasicTradingAgent:
    def __init__(self, llm_url: str = f"https://generativelanguage.googleapis.com/v1beta/models/{config_reader.read_config()['model']}:generateContent?key={config_reader.read_config()['gemini_api_key']}"):
        self.llm_url = llm_url
        self.message_history = []
        try:
            with open(LLM_HISTORY_FILE, "rb") as f:
                data = pickle.load(f)
                if not data:
                    raise Exception
                self.message_history = data
        except Exception as e:
            self.message_history = [{
                "role": "user",
                "parts": [{"text": BASIC_TRADING_AGENT_PROMPT[0]}],
            }, {
                "role": "model",
                "parts": [{"text": BASIC_TRADING_AGENT_PROMPT[1]}],
            }]

    def chat(self, new_chat_message: str) -> Strategy:
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        new_message = {
            "role": "user",
            "parts": [{"text": new_chat_message}]
        }
        self.message_history.append(new_message)
        response = requests.post(self.llm_url, headers=headers, json={
            "contents": self.message_history
        })
        if response.status_code == 200:
            latest_response_message = response.json()
        new_assistant_message = latest_response_message["candidates"][0]['content']
        self.message_history.append(new_assistant_message)
        with open(LLM_HISTORY_FILE, "wb") as f:
            pickle.dump(self.message_history, f)
        
        new_strategy = json.loads(new_assistant_message['parts'][0]['text'].strip('```').strip('json'))
        return Strategy.model_validate(new_strategy)
