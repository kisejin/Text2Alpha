import pandas as pd
from datetime import datetime

import phoenix as px
from openinference.instrumentation.dspy import DSPyInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

# Request and processing packages
import os
import requests
from bs4 import BeautifulSoup
import urllib.request as ulib
from typing import Union
from urllib.request import Request, urlopen

#  Tracing LLM inference
def setup_tracing_llm():
    px.launch_app()
    endpoint = "http://localhost:6006/v1/traces"
    resource = Resource(attributes={})
    tracer_provider = trace_sdk.TracerProvider(resource=resource)
    span_otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
    tracer_provider.add_span_processor(
        SimpleSpanProcessor(span_exporter=span_otlp_exporter)
    )
    trace_api.set_tracer_provider(tracer_provider=tracer_provider)
    DSPyInstrumentor().instrument()
    

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


def extract_text_from_article(url):
    """Extracts text content from div with class 'caas-body' in article request

    Args:
        url: URL which points to the article

    Returns:
        A string containing the extracted text.
    """
    # headers = {'user-agent': 'my-app'}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code

        soup = BeautifulSoup(response.content, 'html.parser')

        if soup:
            return soup
        else:
            raise ValueError('Not exist content!!!')
    except Exception as e:
        print(f"Could not fetch article: {e}")
        return ""



def get_symbol_price_status(symbol: str):

    url = f"https://finance.yahoo.com/quote/{symbol}/"
    terms = extract_text_from_article(url)
    
    section_symbol = terms.find_all('article')[0].find_all('section', class_="container yf-ezk9pj")[0]
    source_symbol = section_symbol.find_all("span", class_="exchange yf-1fo0o81")[0].text.strip()
    company_symbol = section_symbol.find_all("div", class_="left yf-ezk9pj wrap")[0].find_all("h1", class_="yf-3a2v0c")[0].text.strip()
    list_status = section_symbol.find_all("div", class_="yf-mgkamr")

    price_status = section_symbol.find_all('span', class_="yf-1dnpe7s")

    price_status = [ps.text for ps in price_status]

    if len(list_status) > 1:
        stock_price_close, after_trading_price  = list_status[0], list_status[1]
    else:
        stock_price_close, after_trading_price  = list_status[0], ""
        
    stock_price_close = stock_price_close.text.split()
    stock_price_close.append(price_status[0].strip())
    if after_trading_price:
        after_trading_price = after_trading_price.text.split()
        after_trading_price.append(price_status[1].strip())

    status = {
        "source_symbol": source_symbol,
        "company_name": company_symbol,
        "stock_price_at_close": stock_price_close,
        "after_hours_trading_price": after_trading_price
    }

    return status


def read_markdown_file(file_path):
    with open(file_path, "r") as file:
        return file.read()