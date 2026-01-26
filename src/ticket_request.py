import requests
import toml
#from pydantic import BaseModel # Helps define classes
from pathlib import Path

class TicketRequest:

    def __init__(self, url):
        self.api_key = self.get_secret()
        self.url = url


    def call_api(self):
        response = requests.get(self.url, params={"apikey": self.api_key})
        return response.json()


    @staticmethod
    def get_secret():
        try:
            project_root = Path(__file__).resolve().parents[1]
            secrets_path = project_root / ".streamlit" / "secrets.toml"
            secrets = toml.load(secrets_path)
            return secrets["TICKETMASTER_API_KEY"]

        except FileNotFoundError:
            raise RuntimeError("secrets.toml not found")

        except KeyError:
            raise RuntimeError("API key missing in secrets.toml")
