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