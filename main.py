import threading

if not hasattr(threading.Thread, "isAlive"):
    threading.Thread.isAlive = threading.Thread.is_alive

from src.ticket_request import TicketRequest
from src.data_analyser import DataAnalyser
from src.constants import Constants

BASE_URL = "https://app.ticketmaster.com/discovery/v2/events.json"


def main():
    city_events = TicketRequest(BASE_URL).load_events_dataset(size_each=200)
    da = DataAnalyser(city_events)
    capitals_df = da.build_df_from_events()
    print(capitals_df.head())
    for i, cap in enumerate(Constants.CITIES):
        n = da.count_happening_soon(capitals_df, cap["city"], cap["tz"], window_hours=24)

    # bands across cities
    band = da.bands_with_multiple_cities_list(capitals_df)[0]

    band_df = capitals_df[capitals_df["performer"] == band]
    print("pre")
    print(band_df.head())

    map_df = capitals_df.dropna(subset=["lat", "lon"]).copy()
    ########
    filtered = (
        capitals_df
        .loc[capitals_df["genre"].isin(["Jazz"])]
        .dropna(subset=["genre"]))
    map_df = da.city_event_counts(filtered).copy()
    map_df['size'] = map_df["n_events"] ** 5
    if not map_df.empty:
        map_df[["city", "n_events"]].sort_values("n_events", ascending=False)

if __name__ == '__main__':
    main()
