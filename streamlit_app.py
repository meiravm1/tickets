import streamlit as st

from src.ticket_request import TicketRequest
from src.data_analyser import DataAnalyser
from src.displayer import Displayer
BASE_URL = "https://app.ticketmaster.com/discovery/v2/events.json"



# ----------------------------
# Streamlit app
# ----------------------------
st.set_page_config(page_title="International Concert Facts", layout="wide")
st.title("🎟️ Interesting Facts About International Concert Tickets")
st.caption("Data source: Ticketmaster Discovery API (Music events). This is a small sample across 5 capitals.")

capital_events = TicketRequest(BASE_URL).load_capitals_dataset(size_each=80)
da = DataAnalyser(capital_events)
capitals_df = da.build_df_from_events()
ds = Displayer()
ds.show_row_dataset(capitals_df)

# -------- Section A: "happening now" + clocks
st.subheader("1) What concerts are happening now?")
WINDOW_HOURS = 24
cols = st.columns(5)
for i, cap in enumerate(DataAnalyser.CAPITALS):
    with cols[i]:
        st.metric(label=f"🕒 {cap['city']}", value=da.local_time_str(cap["tz"]))
        n = da.count_happening_soon(capitals_df, cap["city"], cap["tz"], window_hours=WINDOW_HOURS)
        st.write(f"Events starting in next {WINDOW_HOURS}: **{n}**")
        st.dataframe(capitals_df[capitals_df.city == cap['city']]['name'].head(5))
st.divider()


# -------- Section B: price comparison for a band
st.subheader("2) Price comparison for a selected band (across capitals)")
band = st.text_input("Band / artist name (example: Metallica)", value="Metallica")

band_df = capitals_df[capitals_df["name"] == band]
band_df = band_df.dropna(subset=["price_min", "city"])

if band_df.empty:
    st.info("No priced events found for that band in this small sample (priceRanges is often missing). Try another artist or increase sample size.")
else:
    # simple “catplot-like” comparison (box plot)
    st.write("Showing **min ticket price** by city for matched events.")
    st.plotly_chart(
        band_df[["city", "price_min", "genre"]].dropna().sort_values("city")
            .pipe(lambda d: __import__("plotly.express").express.box(d, x="city", y="price_min", points="all")),
        use_container_width=True
    )

st.divider()
