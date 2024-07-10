import streamlit as st
import os
import base64
from logo import add_logo

# Streamlit configuration icon
st.set_page_config(layout="wide")
add_logo()


# homepage = st.Page('home.py', title="", icon="🏠", default=True)
qa = st.Page('market_qa.py', title="Finance Strategy Insights", icon="📈")
news = st.Page('news.py', title="News", icon="📰")


pg = st.navigation([qa, news])


pg.run()