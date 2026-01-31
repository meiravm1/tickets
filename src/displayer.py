

import streamlit as st
import pandas as pd
from typing import Dict
import pytz

class Displayer():

    def show_row_dataset(self,df):
        with st.expander("Show raw dataset (sample)"):
            st.dataframe(df.head(50))

    # def happening_now(self,df:pd.DataFrame,capitals: list[Dict]):
    #     # -------- Section A: "happening now" + clocks
    #     st.subheader("1) What concerts are happening now?")
    #     cols = st.columns(5)
    #     for i, cap in enumerate(capitals):
    #         with cols[i]:
    #             st.metric(label=f"🕒 {cap['city']}", value=self.local_time_str(cap["tz"]))
    #             n = self.count_happening_soon(df, cap["city"], cap["tz"], window_hours=2)
    #             st.write(f"Events starting in next 2h: **{n}**")


