# Python package
import json
import base64
import functools
import os
import sys
import matplotlib
matplotlib.use('Agg')
from datetime import datetime

path = '/'.join(os.path.dirname(__file__).split('/')[:-1])

sys.path.append(os.path.join(path, "src/my_dspy"))
sys.path.append(os.path.join(path, "utils"))

from dotenv import load_dotenv
load_dotenv(os.path.join(path,".env"))

# Backtrader package
import backtrader as bt
from backtrader import Indicator
import backtrader.analyzers as btanalyzers
from backtrader_cerebro import CelebroCreator
from data_loader import load_stock_data

import phoenix as px
import requests
from openinference.instrumentation.dspy import DSPyInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor


# DSPy package
import dspy
import dsp
from dspy.predict import Retry
from dspy.primitives.assertions import (
    assert_transform_module,
    backtrack_handler,
)
from dspy_module import GenerateCodeWithAssert


# My package
## Utils package
from file_text_handler import get_code_from_text, load_file
from prompt_template.base_strategy_improved import BaseStrategy

# Streamlit package
import streamlit as st


#  Tracing LLM inference
def setup_tracing_llm():
    px.launch_app()
    endpoint = "http://127.0.0.1:6006/v1/traces"
    resource = Resource(attributes={})
    tracer_provider = trace_sdk.TracerProvider(resource=resource)
    span_otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
    tracer_provider.add_span_processor(
        SimpleSpanProcessor(span_exporter=span_otlp_exporter)
    )
    trace_api.set_tracer_provider(tracer_provider=tracer_provider)
    DSPyInstrumentor().instrument()


# Get the answer from the DSPy program with assertion
def get_answer(user_question, data):
    generate_with_assert = assert_transform_module(
        GenerateCodeWithAssert(list_ohcl_data=data).map_named_predictors(Retry),
        functools.partial(backtrack_handler, max_backtracks=8),
    )

    few_shot_path = os.path.join(path, "src/module/new_code_generation_fewshot_v3.json")
    generate_with_assert.load(few_shot_path)

    return generate_with_assert(user_question)







# Setup tracing for LLM inference
setup_tracing_llm()



# Sidebar
st.sidebar.title("Market Configuration")
symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "FB", "TSLA"]
selected_symbol = st.sidebar.selectbox("Select a symbol", symbols) 

# start_date = st.sidebar.date_input("Start date", datetime.now() - timedelta(days=365))
# end_date = st.sidebar.date_input("End date", datetime.now())


period = st.sidebar.text_input("Period: (y (year), mo (month), d(day))", "1y")

with st.sidebar:
    st.write("Tracing LLM")
    st.link_button("Go to tracing", "http://localhost:6006")

# Load stock data
data = [
    bt.feeds.PandasData(
        dataname=load_stock_data(ticker=selected_symbol, period=period),
        datetime="Date",
        timeframe=bt.TimeFrame.Minutes,
    )
]

st.title("📈 Finance Strategy Insights: Informed Decisions")

# Input for user question
user_question = st.text_input("Enter your finance-related question 👇:")



# Setup tracing for LLM inference

# Configure LLM Anyscale endpoint
lm = dspy.Anyscale(
    model="meta-llama/Meta-Llama-3-70B-Instruct",
    max_tokens=2048,
    use_chat_api=True,
    temperature=0.0,
)
dspy.settings.configure(lm=lm, trace=[])

# Check if user question is provided
if user_question:
    
    response = None
    valid_input = True
    try:
        response = get_answer(user_question, data)
    except Exception as e:
        st.write("Error: Invalid Input! Please provide the complete finance question, and I'll be happy to help you with the answer")
        valid_input = False
    

    if valid_input:
        complete_status, still_errors_status = response.Complete, response.Still_Error[:-1]
        
        
        if complete_status:
            exec(get_code_from_text(response.answer), globals())
            strategy = CelebroCreator(BackTestStrategy,data)
            print(strategy.message)

            
        # Display results
        col1, col2 = st.columns(2)
        # col1, col2 = col1.empty(), col2.empty()

        with col1:
            container1 = st.container(border=True)
            container1_1 =   st.container(border=True)
            # st.subheader("Backtest Results")
            container1.markdown('<div class="placeholder-section"><h3>Backtest Results</h3>', unsafe_allow_html=True)
            
            if still_errors_status=='True':
                container1_1.write("Status: Unsuccessful strategy generation!!!")
                container1_1.write("Message: Unfortunately, we were unable to generate a suitable trading strategy based on your query. Please try another query or provide more detailed information about the indicators you would like to use. This can help our system better understand and create a strategy that meets your needs.")
            
            elif not complete_status:
                container1_1.write("Status: Incomplete Strategy Generation!!!")
                container1_1.write("Message: The generation of your trading strategy was incomplete due to insufficient information about the indicators or strategy. Please provide more detailed descriptions and formulas for the indicators or strategy you are using. This additional information will help our system generate a more accurate and complete strategy")
                
            else:
                results = strategy.return_analysis() 
                container1_1.write("Status: Successfully executed strategy!")
                container1_1.write(f"Starting Cash: ${results['StartingCash']}")
                container1_1.write(f"Final Portfolio Value: ${results['FinalPortfolioValue']:.2f}")
                container1_1.write(f"Sharpe Ratio: {results['SharpeRatio']:.2f}")
                container1_1.write(f"Total Return: {results['TotalReturn']:.2f}%")
            container1.markdown('</div>', unsafe_allow_html=True)

        with col2:
            # st.subheader(f"{selected_symbol} Trend")
            container2 = st.container(border=True) 
            container2.markdown(f'<div class="placeholder-section"><h3>{selected_symbol} Trends</h3>', unsafe_allow_html=True)
            # st.plotly_chart(cerebro.plot(), use_container_width=True)
            if complete_status:
                figure = strategy.show()[0][0]
                st.pyplot(figure)
            else:
                figure = CelebroCreator(strategy=None, list_of_data=data).show()[0][0]
                st.pyplot(figure)
            container2.markdown('</div>', unsafe_allow_html=True)

else:
    pass



