import requests
import toml
#from pydantic import BaseModel # Helps define classes
import streamlit as st
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
            secret = st.secrets["TICKETMASTER_API_KEY"]
            return secret

        except FileNotFoundError:
            raise RuntimeError("secrets.toml not found")

        except KeyError:
            raise RuntimeError("API key missing in secrets.toml")
