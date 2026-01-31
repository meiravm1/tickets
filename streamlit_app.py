import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from src.ticket_request import TicketRequest
from src.data_analyser import DataAnalyser
from src.displayer import Displayer
from src.constants import Constants

BASE_URL = "https://app.ticketmaster.com/discovery/v2/events.json"

# ----------------------------
# Streamlit app
# ----------------------------
st.set_page_config(page_title="International Concert Facts", layout="wide")
st.title("🎟️ Interesting Facts About International Concert Tickets")
st.caption("Data source: Ticketmaster Discovery API (Music events). This is a small sample across cities.")

events = TicketRequest(BASE_URL).load_events_dataset(size_each=200)
da = DataAnalyser(events)
events_df = da.build_df_from_events()
ds = Displayer()
ds.show_row_dataset(events_df)

# -------- Section A: "happening now" + clocks
WINDOW_HOURS = 24
st.subheader(f"1) What concerts are happening on the next {WINDOW_HOURS} hours?")

cols = st.columns(len(Constants.CITIES))
for i, cap in enumerate(Constants.CITIES):
    with cols[i]:
        st.metric(label=f"{cap['city']}", value=da.local_time_str(cap["tz"]))
        n = da.count_happening_soon(events_df, cap["city"], cap["tz"], window_hours=WINDOW_HOURS)
        st.write(f"Events starting in next {WINDOW_HOURS} hours: **{n}**")
        st.dataframe(events_df[events_df.city == cap["city"]]["name"].head(5))
st.divider()

# -------- Section B: price comparison for a band
st.subheader("2) Price comparison for selected bands (across cities)")

ds.cities_price_comparison(events_df)
st.divider()

st.subheader("3) Map: hot concert cities")

ds.city_event_counts(events_df)

st.divider()
# -------- Extra 2: Hour distribution
st.subheader("4) When do concerts start? (hour distribution)")

ds.hours_per_city(events_df)

st.divider()

st.subheader("6) Genre distribution by city (using sns.catplot)")
ds.genres_per_city(events_df)
