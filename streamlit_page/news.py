import streamlit as st
import os
from datetime import datetime, timedelta
import finnhub
import pandas as pd

path = '/'.join(os.path.dirname(__file__).split('/')[:-1])
from dotenv import load_dotenv
load_dotenv(os.path.join(path,".env"))


def get_dateframe_news(news):
    # Four columm: Date, Headline, Summary, URL
    df = {'Date': [], 'title': [], 'summary': [], 'source': [],'url': []}
    for new in news:
        if new['headline'] != '' and new['summary'] != '':
            new['datetime'] = datetime.fromtimestamp(new['datetime']).strftime('%Y-%m-%d %H:%M:%S')
            df['Date'].append(new['datetime'])
            df['title'].append(new['headline'])
            df['summary'].append(new['summary'])
            df['url'].append(new['url'])
            df['source'].append(new['source'])
            
    df = pd.DataFrame(df)
    
    # Sort revese by Date
    df = df.sort_values(by='Date', ascending=False)
    return df



# Sidebar
st.sidebar.title("Market Configuration")
symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "FB", "TSLA"]
selected_symbol = st.sidebar.selectbox("Select a symbol", symbols) 


st.title("📰 Finance Today: Breaking News and Market Analysis")
# Get 1 week news
toDate = datetime.now().strftime("%Y-%m-%d")
fromDate = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
finnhub_client = finnhub.Client(api_key=os.getenv("FINNHUB_API_KEY"))
news = finnhub_client.company_news(selected_symbol, _from=fromDate, to=toDate)
df = get_dateframe_news(news)


for _,article in df.iloc[:10,:].iterrows():
    st.markdown(f"### Title: {article['title']}")
    st.write(f"Published Date: {article['Date']}")
    st.write(f"Summary: {article['summary']}")
    st.markdown(f"Source {article['source']}: [Click here]({article['url']})")
    st.divider()
