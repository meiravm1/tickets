import threading
if not hasattr(threading.Thread, "isAlive"):
    threading.Thread.isAlive = threading.Thread.is_alive
import requests
import toml
#from pydantic import BaseModel # Helps define classes
import streamlit as st
from src.constants import Constants


class TicketRequest:

    def __init__(self, url):
        self.api_key = self.get_secret()
        self.url = url

    def fetch_city_events(self, city: str, country_code: str, size: int = 100) -> dict:
        params = {
            "apikey": self.api_key,
            "city": city,
            "countryCode": country_code,
            "classificationName": "music",
            "size": size,
            "sort": "date,asc",
        }
        r = requests.get(self.url, params=params, timeout=20)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def get_secret():
        try:
            return st.secrets["TICKETMASTER_API_KEY"]

        except FileNotFoundError:
            raise RuntimeError("secrets.toml not found")

        except KeyError:
            raise RuntimeError("API key missing in secrets.toml")

    def load_events_dataset(self, size_each: int = 80) -> list:
        all_events = []
        for c in Constants.CITIES:
            data = self.fetch_city_events(c["city"], c["countryCode"], size=size_each)
            events = data.get("_embedded", {}).get("events", [])
            all_events.extend(events)

        return all_events


