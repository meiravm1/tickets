import threading
if not hasattr(threading.Thread, "isAlive"):
    threading.Thread.isAlive = threading.Thread.is_alive
import requests
import toml
#from pydantic import BaseModel # Helps define classes
import streamlit as st
from pathlib import Path

CAPITALS = [
    {"city": "London", "countryCode": "GB", "tz": "Europe/London"},
    {"city": "Paris", "countryCode": "FR", "tz": "Europe/Paris"},
    {"city": "New York", "countryCode": "US", "tz": "America/New_York"},
    {"city": "Tokyo", "countryCode": "JP", "tz": "Asia/Tokyo"},
    {"city": "Sydney", "countryCode": "AU", "tz": "Australia/Sydney"},
]



class TicketRequest:

    def __init__(self, url):
        self.api_key = self.get_secret()
        self.url = url

    def fetch_events(self, city: str, country_code: str, size: int = 100) -> dict:
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

    def load_capitals_dataset(self,size_each: int = 80) -> list:
        all_events = []
        for c in CAPITALS:
            data = self.fetch_events(c["city"], c["countryCode"], size=size_each)
            events = data.get("_embedded", {}).get("events", [])
            all_events.extend(events)

        return all_events

    def load_bands_dataset(self,size_each: int = 80) -> list:
        all_events = []
        for c in CAPITALS:
            data = self.fetch_events(c["city"], c["countryCode"], size=size_each)
            events = data.get("_embedded", {}).get("events", [])
            all_events.extend(events)

        return all_events