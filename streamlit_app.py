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

events = TicketRequest(BASE_URL).load_capitals_dataset(size_each=200)
da = DataAnalyser(events)
events_df = da.build_df_from_events()
ds = Displayer()
ds.show_row_dataset(events_df)

# -------- Section A: "happening now" + clocks
WINDOW_HOURS = 24
st.subheader(f"1) What concerts are happening on the next {WINDOW_HOURS} hours?")

cols = st.columns(len(Constants.CAPITALS))
for i, cap in enumerate(Constants.CAPITALS):
    with cols[i]:
        st.metric(label=f"🕒 {cap['city']}", value=da.local_time_str(cap["tz"]))
        n = da.count_happening_soon(events_df, cap["city"], cap["tz"], window_hours=WINDOW_HOURS)
        st.write(f"Events starting in next {WINDOW_HOURS} hours: **{n}**")
        st.dataframe(events_df[events_df.city == cap['city']]['name'].head(5))
st.divider()


# -------- Section B: price comparison for a band
st.subheader("2) Price comparison for a selected band (across cities)")
performer_options = da.bands_with_multiple_cities(events_df)
#st.write("performer_options:", performer_options[:10], "…", len(performer_options))


if not performer_options:
    st.warning("No performers with priced events across multiple cities in this sample. Try increasing sample size or switching cities to US/CA/AU.")
    st.stop()

band = st.selectbox("Choose a performer touring multiple cities", performer_options)

band_df = events_df[events_df["performer"] == band].dropna(subset=["price_min", "city"])

if band_df.empty:
    st.info("No priced events found for that band in this small sample (priceRanges is often missing). Try another artist or increase sample size.")
else:
    # simple “catplot-like” comparison (box plot)
    st.write("Showing **min ticket price** by city for matched events.")
    fig, ax = plt.subplots()
    sns.scatterplot(data=band_df, x='performer', y='price_min', hue='city')
    st.pyplot(fig)

    # st.plotly_chart(
    #     band_df[["city", "price_min", "genre"]].dropna().sort_values("city")
    #         .pipe(lambda d: __import__("plotly.express").express.box(d, x="city", y="price_min", points="all")),
    #     use_container_width=True
    # )

st.divider()
