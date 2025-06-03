#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pandas", "matplotlib", "plotly", "reportlab", "kaleido"]
# ///

import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Image as ReportLabImage, Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
import os

# Load data
CSV_PATH = "/Users/greatmaster/Desktop/projects/content_creation/intro-to-vibe-scripting/assets/financial-data.csv"
df = pd.read_csv(CSV_PATH, parse_dates=["Date"])

# Calculate extra metrics
df["Daily Return (%)"] = df["Close"].pct_change() * 100
avg_volume = df["Volume"].mean()
avg_close = df["Close"].mean()
max_close = df["Close"].max()
min_close = df["Close"].min()

# Create plots and save them temporarily
temp_dir = tempfile.mkdtemp()

def save_plot(fig, filename):
    path = os.path.join(temp_dir, filename)
    fig.write_image(path)  # Requires kaleido
    return path

# Plot 1: Line chart of prices
price_fig = px.line(df, x="Date", y=["Open", "High", "Low", "Close"], title="Stock Prices Over Time")
price_path = save_plot(price_fig, "price_chart.png")

# Plot 2: Volume bar chart
volume_fig = px.bar(df, x="Date", y="Volume", title="Trading Volume Over Time")
volume_path = save_plot(volume_fig, "volume_chart.png")

# Plot 3: Daily returns
returns_fig = px.line(df, x="Date", y="Daily Return (%)", title="Daily Percentage Returns")
returns_path = save_plot(returns_fig, "returns_chart.png")

# Generate PDF report
pdf_path = "financial_report.pdf"
doc = SimpleDocTemplate(pdf_path, pagesize=letter)
styles = getSampleStyleSheet()
story = []

# Title
story.append(Paragraph("Financial Data Report", styles["Title"]))
story.append(Spacer(1, 20))

# Summary insights
insight_text = f"""
This report analyzes financial data over the observed period. Key highlights include:

- Average closing price: ${avg_close:.2f}
- Highest closing price: ${max_close:.2f}
- Lowest closing price: ${min_close:.2f}
- Average trading volume: {avg_volume:,.0f} shares
"""
story.append(Paragraph(insight_text, styles["Normal"]))
story.append(Spacer(1, 20))

# Charts
for chart_path, title in [
    (price_path, "Stock Prices Over Time"),
    (volume_path, "Trading Volume Over Time"),
    (returns_path, "Daily Percentage Returns")
]:
    story.append(Paragraph(title, styles["Heading2"]))
    story.append(Spacer(1, 10))
    story.append(ReportLabImage(chart_path, width=500, height=250))
    story.append(Spacer(1, 20))

# Build PDF
doc.build(story)
print(f"PDF report created at: {pdf_path}")
