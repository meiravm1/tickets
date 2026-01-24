import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
import pandas as pd


class DataAnalysis:
    def __init__(self, data):
        self.data = data

    def get_df(self):
        events = self.data["_embedded"]["events"]
        return pd.json_normalize(events)

    def clean_df(self, df):
        df_clean = df[[
            "name",
            "dates.start.localDate",
            "dates.start.localTime",
            "dates.timezone",
            "_embedded.venues.0.name",
            "_embedded.venues.0.city.name",
            "_embedded.venues.0.country.name",
            "_embedded.venues.0.location.latitude",
            "_embedded.venues.0.location.longitude"
        ]]
        return df_clean.rename(columns={"_embedded.venues.0.name": "venue"
                                            ,"_embedded.venues.0.city.name": "city",
                                            "_embedded.venues.0.country.name": "country",
                                            "_embedded.venues.0.location.latitude": "lat",
                                            "_embedded.venues.0.location.longitude": "lon", })

    def startup(self, df):

        st.title('My first app')

        plot_choice = st.radio('Choose you plot library:', ['Seaborn', 'Plotly'])

        if plot_choice == 'Seaborn':
            print("seaborn")
            fig, ax = plt.subplots()
            sns.scatterplot(data=df, x='flipper_length_mm', y='body_mass_g', hue='species')
            st.pyplot(fig)

        elif plot_choice == 'Plotly':
            print("Plotly")
            fig = px.scatter(df, x='flipper_length_mm', y='body_mass_g', color='species', title='Pegnguins')
            st.plotly_chart(fig)
