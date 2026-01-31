

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from src.data_analyser import DataAnalyser

class Displayer():

    @staticmethod
    def show_row_dataset(df):
        with st.expander("Show raw dataset (sample)"):
            st.dataframe(df.head(50))
    @staticmethod
    def genres_per_city(events_df: pd.DataFrame):
        genre_city_df = events_df.dropna(subset=["city", "genre"]).copy()
        if genre_city_df.empty:
            st.info("No genre data found for events in any city.")
        else:
            # Use sns.catplot to show genre distribution across cities
            g = sns.catplot(data=genre_city_df, hue="genre", x="genre", col="city", kind="count", col_wrap=3,
                            palette="viridis", sharex=False)
            g.set_xticklabels(rotation=45, ha='right')
            g.set_axis_labels("Genre", "Number of Events")
            g.set_titles("City: {col_name}")
            plt.tight_layout()
            st.pyplot(g.fig)

    @staticmethod
    def cities_price_comparison(events_df: pd.DataFrame):
        da = DataAnalyser(events_df)
        performer_options = da.bands_with_multiple_cities_list(events_df)
        if not performer_options:
            st.warning(
                "No performers with priced events across multiple cities in this sample. Try increasing sample size or switching cities to US/CA/AU.")
            st.stop()
        selected_performers = st.multiselect("Choose performers touring multiple cities", performer_options)
        filtered = (
            events_df
            .loc[events_df["performer"].isin(selected_performers)]
            .dropna(subset=["price_min", "city"])
        )
        if filtered.empty:
            st.info("No priced events found for the selected performers.")
        else:
            st.write("Showing **min ticket price by city** for selected performers.")

            g = sns.catplot(
                data=filtered,
                x="city",
                y="price_min",
                col="performer",  # 👈 one chart per performer
                kind="strip",  # scatter-like (good for few points)
                col_wrap=3,
                height=3,
                aspect=1.1,
                sharey=False  # optional: independent y-axis
            )

            for ax in g.axes.flat:
                ax.tick_params(axis="x", rotation=45)

            st.pyplot(g.fig)

    @staticmethod
    def city_event_counts(events_df: pd.DataFrame):

        da = DataAnalyser(events_df)
        genre_options = da.genre_list(events_df)
        if not genre_options:
            st.warning("No Genres")
            st.stop()
        selected_genres = st.multiselect("Choose genres", genre_options)
        filtered = (
            events_df
            .loc[events_df["genre"].isin(selected_genres)]
            .dropna(subset=["genre"]))
        map_df = da.city_event_counts(filtered).copy()
        if not map_df.empty:
            st.map(map_df[["latitude", "longitude"]], size="n_events")
            st.dataframe(map_df.sort_values("n_events", ascending=False))

    @staticmethod
    def hours_per_city(events_df: pd.DataFrame):
        hour_df = events_df.dropna(subset=["start_hour"]).copy()
        if hour_df.empty:
            st.info("No event start times found.")
        else:
            g = sns.catplot(data=hour_df, x="start_hour", col="city", kind="count", col_wrap=3)
            st.pyplot(g.figure, use_container_width=True)