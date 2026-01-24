import streamlit as st

from src.ticket_request import TicketRequest
from src.data_analysis import DataAnalysis
url = "https://app.ticketmaster.com/discovery/v2/events.json"

tr = TicketRequest(url).call_api()


st.title('Your Ticket Master App')

name = st.text_input('Enter your name', '')
if name:
    st.write(f'Hello {name}, welcome to the custom ticket master app!')
    da = DataAnalysis(tr).startup()