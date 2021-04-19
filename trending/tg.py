import requests


class Telegram:
    def __init__(self, token: str) -> None:
        self.token = token

    def send_message(self, to: int, message: str) -> None:
        print("Sending message to TG:", message, sep="\n")
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {"chat_id": to, "text": message, "parse_mode": "MarkdownV2"}
        resp = requests.post(url, data=data)
        print(resp.json())
        resp.raise_for_status()
