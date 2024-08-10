# Python package
import base64
import functools
import json
import os
import sys
import time
from datetime import datetime, timedelta

import finnhub
import matplotlib
import requests

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), "src/my_dspy"))
sys.path.append(os.path.join(os.path.dirname(__file__), "utils"))

sys.path.append(os.path.join(os.path.dirname(__file__), "streamlit_tools"))


from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Backtrader package
import backtrader as bt
import backtrader.analyzers as btanalyzers
import dsp

# DSPy package
import dspy

# Streamlit package
import streamlit as st
from backtrader import Indicator
from dspy.predict import Retry
from dspy.primitives.assertions import (
    assert_transform_module,
    backtrack_handler,
)
from streamlit_autorefresh import st_autorefresh

from src.my_dspy.dspy_module import GenerateCodeWithAssert
from streamlit_tools.tools import (
    get_dateframe_news,
    get_symbol_price_status,
    read_markdown_file,
    setup_tracing_llm,
)
from utils.backtrader_cerebro import CelebroCreator
from utils.data_loader import load_stock_data

# My package
## Utils package
from utils.file_text_handler import get_code_from_text, load_file
from utils.prompt_template.base_strategy_improved import BaseStrategy


# Get the answer from the DSPy program with assertion
def get_answer(user_question, data):
    generate_with_assert = assert_transform_module(
        GenerateCodeWithAssert(
            list_ohcl_data=data, max_retry=5
        ).map_named_predictors(Retry),
        functools.partial(backtrack_handler, max_backtracks=5),
    )

    few_shot_path = os.path.join(
        os.path.dirname(__file__),
        "src/module/new_code_generation_fewshot_v3.json",
    )
    generate_with_assert.load(few_shot_path)

    return generate_with_assert(user_question)


# # Setup tracing for LLM inference
# setup_tracing_llm()


def main():

    # Streamlit configuration
    st.set_page_config(layout="wide")
    # Streamlit configuration themes and layout
    st.markdown(
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">',
        unsafe_allow_html=True,
    )

    # Streamlit configuration icon
    icon_path = os.path.join(
        os.path.dirname(__file__), "image/Text2Alpha_icon.png"
    )
    icon_html = f"""
    <div style="text-align: center;">
        <a href="" target="_blank">
            <img src="data:image/png;base64,{base64.b64encode(open(icon_path, "rb").read()).decode()}" style="width: 150px;">
        </a>
    </div>
    """
    st.markdown(icon_html, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.title("Market Configuration")
    symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    selected_symbol = st.sidebar.selectbox("Select a symbol", symbols)

    # start_date = st.sidebar.date_input("Start date", datetime.now() - timedelta(days=365))
    # end_date = st.sidebar.date_input("End date", datetime.now())

    period = st.sidebar.text_input(
        "Period: (y (year), mo (month), d(day))", "1y"
    )

    # Get the date range
    toDate = datetime.now().strftime("%Y-%m-%d")
    fromDate = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    # Load stock data
    data = [
        bt.feeds.PandasData(
            dataname=load_stock_data(ticker=selected_symbol, period=period),
            datetime="Date",
            timeframe=bt.TimeFrame.Minutes,
        )
    ]

    # Setting Multiple tabs in streamlit
    tabs = ["Home", "Finance Strategy Insights", "News"]
    list_tab = st.tabs(tabs)

    with list_tab[0]:
        md_content = read_markdown_file("homepage.md")
        st.markdown(md_content, unsafe_allow_html=True)

    with list_tab[1]:
        st.title("📈 Finance Strategy Insights: Informed Decisions")

        # Input for user question
        user_question = st.text_area("Enter your finance-related question 👇:")

        # Submit button
        submit_button = st.button("Submit")

        st.markdown(
            """<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """,
            unsafe_allow_html=True,
        )

        # Configure LLM Anyscale endpoint
        # model="meta-llama/Meta-Llama-3-70B-Instruct",
        model = "meta-llama/Meta-Llama-3.1-70B-Instruct"
        # model = "meta-llama/Meta-Llama-3.1-405B-Instruct"
        lm = dspy.Anyscale(
            model=model,
            max_tokens=2048,
            use_chat_api=True,
            temperature=0.0,
        )
        dspy.settings.configure(lm=lm, trace=[])

        # Check if user question is provided
        if submit_button:
            if user_question:

                response = None
                valid_input = True
                try:
                    response = get_answer(user_question, data)
                except Exception as e:
                    st.write(
                        "Error: Invalid Input! Please provide the complete finance question, and I'll be happy to help you with the answer"
                    )
                    valid_input = False

                if valid_input:
                    complete_status, still_errors_status = (
                        response.Complete,
                        response.Still_Error[:-1],
                    )

                    if complete_status:
                        exec(get_code_from_text(response.answer), globals())
                        strategy = CelebroCreator(BackTestStrategy, data)

                    # Display results
                    col1, col2 = st.columns(2)
                    # col1, col2 = col1.empty(), col2.empty()

                    with col1:
                        container1 = st.container(border=True)
                        container1_1 = st.container(border=True)
                        # st.subheader("Backtest Results")
                        container1.markdown(
                            '<div class="placeholder-section"><h3>Backtest Results</h3>',
                            unsafe_allow_html=True,
                        )

                        if still_errors_status == "True" or not complete_status:
                            container1_1.write(
                                "Status: Unsuccessful strategy generation!!!"
                            )
                            container1_1.write(
                                "Message: Unfortunately, we were unable to generate a suitable trading strategy based on your query. Please try another strategy query or provide more detailed information about the indicators you would like to use. This can help our system better understand and create a strategy that meets your needs."
                            )

                        # elif not complete_status:
                        #     container1_1.write("Status: Incomplete strategy generation!!!")
                        #     container1_1.write("Message: The generation of your trading strategy was incomplete due to insufficient information about the indicators or strategy. Please provide more detailed descriptions and formulas for the indicators or strategy you are using. This additional information will help our system generate a more accurate and complete strategy")

                        else:
                            results = strategy.return_analysis()
                            container1_1.write(
                                "Status: Strategy executed successfully!!!"
                            )
                            container1_1.write(
                                f"Starting Cash: ${results['StartingCash']}"
                            )
                            container1_1.write(
                                f"Final Portfolio Value: ${results['FinalPortfolioValue']:.2f}"
                            )
                            container1_1.write(
                                f"Sharpe Ratio: {results['SharpeRatio']:.2f}"
                            )
                            container1_1.write(
                                f"Total Return: {results['TotalReturn']:.2f}%"
                            )
                        container1.markdown("</div>", unsafe_allow_html=True)

                    with col2:
                        # st.subheader(f"{selected_symbol} Trend")
                        container2 = st.container(border=True)
                        container2.markdown(
                            f'<div class="placeholder-section"><h3>{selected_symbol} Trends</h3>',
                            unsafe_allow_html=True,
                        )
                        # st.plotly_chart(cerebro.plot(), use_container_width=True)
                        if complete_status:
                            figure = strategy.show()[0][0]
                            st.pyplot(figure)
                        else:
                            figure = CelebroCreator(
                                strategy=None, list_of_data=data
                            ).show()[0][0]
                            st.pyplot(figure)
                        container2.markdown("</div>", unsafe_allow_html=True)

            else:
                pass

    with list_tab[2]:

        # Update every 5 mins
        st_autorefresh(interval=5 * 60 * 1000, key="newsrefresh")

        status = get_symbol_price_status(symbol=selected_symbol)
        finnhub_client = finnhub.Client(api_key=os.getenv("FINNHUB_API_KEY"))
        news = finnhub_client.company_news(
            selected_symbol, _from=fromDate, to=toDate
        )
        df = get_dateframe_news(news)

        st.title("📰 Finance Today: Breaking News and Market Analysis")

        container = st.container(border=True)

        with container:
            st.markdown(status["source_symbol"])
            # Title and ticker
            st.title(status["company_name"])

            # Create two columns for the layout
            col1, col2 = st.columns(2)

            # Stock price at close
            with col1:
                sprice_close = status["stock_price_at_close"]
                st.metric(
                    label=sprice_close[-1],
                    value=sprice_close[0],
                    delta=" ".join(sprice_close[1:-1]),
                )
            if status["after_hours_trading_price"]:
                # Stock price after hours
                with col2:
                    after_price = status["after_hours_trading_price"]
                    st.metric(
                        label=after_price[-1],
                        value=after_price[0],
                        delta=" ".join(after_price[1:-1]),
                    )

        st.markdown(
            """<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """,
            unsafe_allow_html=True,
        )

        for _, article in df.iloc[:10, :].iterrows():
            st.markdown(f"### {article['title']}")
            st.write(f"Published Date: {article['Date']}")
            st.write(f"Summary: {article['summary']}")
            st.markdown(
                f"Source {article['source']}: [Click here]({article['url']})"
            )
            st.markdown(
                """<hr style="height:3.5px;border:none;color:#333;background-color:#333;" /> """,
                unsafe_allow_html=True,
            )

    # with list_tab[3]:
    #     # st.write("Coming soon...")
    #     iframe_src = "http://localhost:6006"
    #     st.components.v1.iframe(iframe_src, height=2000)


if __name__ == "__main__":
    main()
