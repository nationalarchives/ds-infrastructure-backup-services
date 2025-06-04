import ssl
import certifi
from slack_sdk import WebClient


class Reporter:
    def __init__(self, connection_creds: dict):
        self.channel = connection_creds['slack_channel']
        self.user = connection_creds['user_name']
        self.token = connection_creds['slack_token']

    def send_message(self, message: str):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        client = WebClient(token=self.token, ssl=ssl_context)
        try:
            response = client.chat_postMessage(
                channel=self.channel,
                text=message,
                username=self.user,
            )
            return response
        except Exception as e:
            print(f"Error sending message: {e}")
            return None
