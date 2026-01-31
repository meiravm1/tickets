import threading

if not hasattr(threading.Thread, "isAlive"):
    threading.Thread.isAlive = threading.Thread.is_alive


import pandas as pd
import pytz
import datetime

class DataAnalyser:


    def __init__(self, data):
        self.data = data


    def build_df_from_events(self):
        # events = self.data["_embedded"]["events"]
        events_df = pd.json_normalize(self.data)
        # Prices
        events_df["price_min"] = pd.to_numeric(
            events_df.get("priceRanges.0.min"),
            errors="coerce"
        )

        events_df["price_max"] = pd.to_numeric(
            events_df.get("priceRanges.0.max"),
            errors="coerce"
        )
        # Genre
        events_df["genre"] = events_df.get("classifications.0.genre.name")
        # Venue
        venue_0 = events_df["_embedded.venues"].map(lambda v: v[0] if v else {})
        venue_df = pd.DataFrame({
            "venue_name": venue_0.map(lambda d: d.get("name")),
            "venue_city": venue_0.map(lambda d: (d.get("city") or {}).get("name")),
            "venue_country": venue_0.map(lambda d: (d.get("country") or {}).get("name")),
            "venue_latitude": pd.to_numeric(venue_0.map(lambda d: (d.get("location") or {}).get("latitude")),
                                            errors="coerce"),
            "venue_longitude": pd.to_numeric(venue_0.map(lambda d: (d.get("location") or {}).get("longitude")),
                                             errors="coerce"),
        })
        df = events_df.join(venue_df, lsuffix="_event", rsuffix="_venue")

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

        df = df.dropna(subset=["city"])

        a0 = df["_embedded.attractions"].map(
            lambda a: a[0] if isinstance(a, list) and len(a) > 0 else {}
        )

        df["performer"] = a0.map(lambda d: d.get("name"))

        # Keep only what we use (prevents huge df)
        keep = [
            "name", "genre", "segment",
            "price_min", "price_max",
            "local_date", "local_time", "timezone", "start_hour",
            "venue_name", "city", "country", "lat", "lon",
            "url","performer"
        ]

        return df.reindex(columns=keep)


    @staticmethod
    def local_time(timezone: str):
       tz = pytz.timezone(timezone)
       return datetime.datetime.now(tz)

    def local_time_str(self,timezone:str):
        return self.local_time(timezone).strftime("%H:%M:%S")

    def count_happening_soon(self,df: pd.DataFrame, city: str, tz_name: str, window_hours: int = 2) -> int:
        start_time = self.local_time(tz_name)
        end_time = self.local_time(tz_name) + datetime.timedelta(hours=window_hours)
        df['event_date_time'] = pd.to_datetime(df['local_date'].astype(str) +" "+ df['local_time'].astype(str),errors="coerce")
        df['event_date_time'] = df['event_date_time'].dt.tz_localize(tz_name, nonexistent="NaT", ambiguous="NaT")

        filtered_df = df[
            (df.city.str.lower() == city.lower()) &
            (df.event_date_time > start_time) &
            (df.event_date_time < end_time)
            ]

        return len(filtered_df)

    # def display(self):
    #
    #     st.title('My first app')
    #
    #     plot_choice = st.radio('Choose you plot library:', ['Seaborn', 'Plotly'])
    #
    #     if plot_choice == 'Seaborn':
    #         print("seaborn")
    #         fig, ax = plt.subplots()
    #         sns.scatterplot(data=self.df, x='venue_city_name', y='venue_latitude', hue='venue_country')
    #         st.pyplot(fig)
    #
    #     elif plot_choice == 'Plotly':
    #         print("Plotly")
    #         fig = px.scatter(self.df, x='venue_city_name', y='venue_latitude', color='venue_country', title='countries')
    #         st.plotly_chart(fig)
    #     # TODO classification


    def bands_with_multiple_cities(self,df: pd.DataFrame):
        # drop rows with empty min ,max price for this graph
        bands_with_prices = df.dropna(subset=['price_min','price_max'],how='any')
        return  bands_with_prices[bands_with_prices.groupby("performer")["city"].transform("nunique") > 1]["performer"]


