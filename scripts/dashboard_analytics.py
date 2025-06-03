#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pandas", "plotly", "dash"]
# ///

import pandas as pd
from dash import Dash, dcc, html
import plotly.express as px

# Load the CSV data
CSV_PATH = "/Users/greatmaster/Desktop/projects/content_creation/intro-to-vibe-scripting/assets/financial-data.csv"
df = pd.read_csv(CSV_PATH, parse_dates=["Date"])

# Create the Dash app
app = Dash(__name__)
app.title = "Financial Analytics Dashboard"

# Create figures
price_fig = px.line(
    df,
    x="Date",
    y=["Open", "High", "Low", "Close"],
    title="Stock Prices Over Time",
    labels={"value": "Price", "variable": "Metric"},
)

volume_fig = px.bar(
    df,
    x="Date",
    y="Volume",
    title="Trading Volume Over Time",
)

price_change = df["Close"].pct_change() * 100
df["Daily Return (%)"] = price_change

returns_fig = px.line(
    df,
    x="Date",
    y="Daily Return (%)",
    title="Daily Percentage Returns",
)

# Layout
app.layout = html.Div(children=[
    html.H1("Financial Data Dashboard"),
    dcc.Graph(figure=price_fig),
    dcc.Graph(figure=volume_fig),
    dcc.Graph(figure=returns_fig),
])

if __name__ == "__main__":
    app.run(debug=True)
