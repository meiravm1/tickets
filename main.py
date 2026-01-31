import threading
if not hasattr(threading.Thread, "isAlive"):
    threading.Thread.isAlive = threading.Thread.is_alive

from src.ticket_request import TicketRequest
from src.data_analyser import DataAnalyser
from src.constants import Constants
BASE_URL = "https://app.ticketmaster.com/discovery/v2/events.json"
def main():
    capital_events = TicketRequest(BASE_URL).load_capitals_dataset(size_each=200)
    da = DataAnalyser(capital_events)
    capitals_df = da.build_df_from_events()
    print(capitals_df.head())
    for i, cap in enumerate(Constants.CAPITALS):
        n = da.count_happening_soon(capitals_df, cap["city"], cap["tz"], window_hours=24)
        print(cap,n)

    # bands across cities
    print(capitals_df)
    band = da.bands_with_multiple_cities(capitals_df)
    band_df = capitals_df[capitals_df["name"] == band]







if __name__ == '__main__':
    main()