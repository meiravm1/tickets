import threading
if not hasattr(threading.Thread, "isAlive"):
    threading.Thread.isAlive = threading.Thread.is_alive

from src.ticket_request import TicketRequest
from src.data_analyser import DataAnalyser
BASE_URL = "https://app.ticketmaster.com/discovery/v2/events.json"
def main():
    capital_events = TicketRequest(BASE_URL).load_capitals_dataset(size_each=200)
    ds = DataAnalyser(capital_events)
    capitals_df = ds.build_df_from_events()
    print(capitals_df.head())
    for i, cap in enumerate(DataAnalyser.CAPITALS):
        n = ds.count_happening_soon(capitals_df, cap["city"], cap["tz"], window_hours=24)
        print(cap,n)

    print(capitals_df)
    band_across_cities = capitals_df[capitals_df.groupby("performer")["city"].transform("nunique") > 1]


    print(band_across_cities)



if __name__ == '__main__':
    main()