import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timezone
import pytz

# ----------------------------
# Config
# ----------------------------
BASE_URL = "https://app.ticketmaster.com/discovery/v2/events.json"

CAPITALS = [
    {"city": "London", "countryCode": "GB", "tz": "Europe/London"},
    {"city": "Paris", "countryCode": "FR", "tz": "Europe/Paris"},
    {"city": "New York", "countryCode": "US", "tz": "America/New_York"},
    {"city": "Tokyo", "countryCode": "JP", "tz": "Asia/Tokyo"},
    {"city": "Sydney", "countryCode": "AU", "tz": "Australia/Sydney"},
]

# ----------------------------
# API + Data shaping
# ----------------------------
def fetch_events(api_key: str, city: str, country_code: str, size: int = 100) -> dict:
    params = {
        "apikey": api_key,
        "city": city,
        "countryCode": country_code,
        "classificationName": "music",
        "size": size,
        "sort": "date,asc",
    }
    r = requests.get(BASE_URL, params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def build_df_from_events(events: list[dict]) -> pd.DataFrame:
    # event-level flatten
    events_df = pd.json_normalize(events, sep=".")

    # optional fields
    events_df["genre"] = events_df.get("classifications.0.genre.name")
    events_df["segment"] = events_df.get("classifications.0.segment.name")
    events_df["price_min"] = pd.to_numeric(events_df.get("priceRanges.0.min"), errors="coerce")
    events_df["price_max"] = pd.to_numeric(events_df.get("priceRanges.0.max"), errors="coerce")

    # venue[0] extraction (venues remain a list column otherwise)
    v0 = events_df.get("_embedded.venues")
    if v0 is None:
        # No venue info at all
        venue_df = pd.DataFrame(columns=["venue_name","venue_city","venue_country","lat","lon"])
    else:
        v0 = v0.map(lambda v: v[0] if v else {})
        venue_df = pd.DataFrame({
            "venue_name": v0.map(lambda d: d.get("name")),
            "venue_city": v0.map(lambda d: (d.get("city") or {}).get("name")),
            "venue_country": v0.map(lambda d: (d.get("country") or {}).get("name")),
            "lat": pd.to_numeric(v0.map(lambda d: (d.get("location") or {}).get("latitude")), errors="coerce"),
            "lon": pd.to_numeric(v0.map(lambda d: (d.get("location") or {}).get("longitude")), errors="coerce"),
        })

    df = events_df.join(venue_df)

    # Clean event datetime basics (local date+time as a single string)
    df["local_date"] = df.get("dates.start.localDate")
    df["local_time"] = df.get("dates.start.localTime").fillna("00:00:00")
    df["timezone"] = df.get("dates.timezone")

    # Create a "start_hour" for histogram
    dt = pd.to_datetime(df["local_date"].astype(str) + " " + df["local_time"].astype(str), errors="coerce")
    df["start_hour"] = dt.dt.hour

    # Nice label for city/country
    df["city"] = df["venue_city"]
    df["country"] = df["venue_country"]

    # Keep only what we use (prevents huge df)
    keep = [
        "name", "genre", "segment",
        "price_min", "price_max",
        "local_date", "local_time", "timezone", "start_hour",
        "venue_name", "city", "country", "lat", "lon",
        "url"
    ]
    return df.reindex(columns=keep)

@st.cache_data(ttl=300)
def load_capitals_dataset(api_key: str, size_each: int = 80) -> pd.DataFrame:
    all_events = []
    for c in CAPITALS:
        data = fetch_events(api_key, c["city"], c["countryCode"], size=size_each)
        events = data.get("_embedded", {}).get("events", [])
        all_events.extend(events)

    df = build_df_from_events(all_events)
    # Drop rows with no city (very rare, but keep things clean)
    df = df.dropna(subset=["city"])
    return df

# ----------------------------
# UI helpers
# ----------------------------
def local_time_str(tz_name: str) -> str:
    tz = pytz.timezone(tz_name)
    return datetime.now(tz).strftime("%H:%M")

def count_happening_soon(df: pd.DataFrame, city: str, tz_name: str, window_hours: int = 2) -> int:
    """Count events in [now, now+window_hours] in that city's local time (rough)."""
    tz = pytz.timezone(tz_name)
    now_local = datetime.now(tz)

    # Parse local datetime from df (best effort)
    dt = pd.to_datetime(df["local_date"].astype(str) + " " + df["local_time"].astype(str), errors="coerce")
    # dt is naive; treat as local time in that city for a quick project
    # Filter by city first
    dcity = df[df["city"].str.lower() == city.lower()].copy()
    dt_city = pd.to_datetime(dcity["local_date"].astype(str) + " " + dcity["local_time"].astype(str), errors="coerce")

    # Compare naive datetimes by converting now_local to naive
    now_naive = now_local.replace(tzinfo=None)
    end_naive = (now_local + pd.Timedelta(hours=window_hours)).replace(tzinfo=None)

    return int(((dt_city >= now_naive) & (dt_city <= end_naive)).sum())

# ----------------------------
# Streamlit app
# ----------------------------
st.set_page_config(page_title="International Concert Facts", layout="wide")
st.title("🎟️ Interesting Facts About International Concert Tickets")
st.caption("Data source: Ticketmaster Discovery API (Music events). This is a small sample across 5 capitals.")

api_key = st.secrets["TICKETMASTER_API_KEY"]

df = load_capitals_dataset(api_key)

# -------- Section A: "happening now" + clocks
st.subheader("1) What concerts are happening now?")
cols = st.columns(5)
for i, cap in enumerate(CAPITALS):
    with cols[i]:
        st.metric(label=f"🕒 {cap['city']}", value=local_time_str(cap["tz"]))
        n = count_happening_soon(df, cap["city"], cap["tz"], window_hours=2)
        st.write(f"Events starting in next 2h: **{n}**")

st.divider()

# -------- Section B: price comparison for a band
st.subheader("2) Price comparison for a selected band (across capitals)")
band = st.text_input("Band / artist name (example: Metallica)", value="Metallica")

band_df = df[df["name"].fillna("").str.contains(band, case=False, na=False)].copy()
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

# -------- Section C: map by selected genre
st.subheader("3) Map: hot concerts by your selected genre")
genres = sorted([g for g in df["genre"].dropna().unique().tolist()]) or ["(no genres found)"]
genre_choice = st.selectbox("Choose a genre", genres)

map_df = df.copy()
if genre_choice != "(no genres found)":
    map_df = map_df[map_df["genre"] == genre_choice]

map_df = map_df.dropna(subset=["lat", "lon"]).copy()

if map_df.empty:
    st.info("No mappable events for this selection (missing lat/lon is common). Try another genre.")
else:
    st.map(map_df.rename(columns={"lat": "latitude", "lon": "longitude"})[["latitude", "longitude"]])

st.divider()

# -------- Extra 1: Top cities
st.subheader("4) Top cities with the most events (in our sample)")
top = df.groupby("city").size().sort_values(ascending=False).head(10).reset_index(name="events")
st.plotly_chart(
    __import__("plotly.express").express.bar(top, x="city", y="events"),
    use_container_width=True
)

# -------- Extra 2: Hour distribution
st.subheader("5) When do concerts start? (hour distribution)")
hour_df = df.dropna(subset=["start_hour"]).copy()
if hour_df.empty:
    st.info("No event start times found.")
else:
    st.plotly_chart(
        __import__("plotly.express").express.histogram(hour_df, x="start_hour", nbins=24),
        use_container_width=True
    )

# -------- Optional: show raw table (for debugging/demo)
with st.expander("Show raw dataset (sample)"):
    st.dataframe(df.head(50))
