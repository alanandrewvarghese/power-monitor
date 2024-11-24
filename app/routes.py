from flask import render_template, current_app, request
from app import create_app  # Import the create_app function
import plotly.express as px
from . import helpers


def init_routes(app):
    @app.route('/', methods=["GET", "POST"])
    def index():
        if request.method == "POST":
            start = request.form.get("timestamp_start")
            end = request.form.get("timestamp_end")
        else:
            start,end = None, None
        
        start, end = helpers.parse_timestamps(start, end)  # Default last 6 hours

        query = f"SELECT timestamp, power, voltage, power_factor, current FROM measurements WHERE timestamp > '{start}' AND timestamp < '{end}' LIMIT 86400;"
        df = helpers.fetch_chart_data(query)
        
        chart_html = None

        if df.empty:
            chart_html = "<p class='text-center text-red-500 p-8'>No data available for the selected time range.</p>"
        else:
            fig = px.line(df, x="timestamp", y="power", title="Power Over Time")
            power_chart_html = fig.to_html(full_html=False)

            fig = px.line(df, x="timestamp", y="voltage", title="Voltage Over Time")
            voltage_chart_html = fig.to_html(full_html=False)
            
            fig = px.line(df, x="timestamp", y="current", title="Current Over Time")
            current_chart_html = fig.to_html(full_html=False)
            
            fig = px.line(df, x="timestamp", y="power_factor", title="Power Factor Over Time")
            power_factor_chart_html = fig.to_html(full_html=False)

            chart_html = {
                "power":power_chart_html,
                "voltage":voltage_chart_html,
                "current":current_chart_html,
                "power_factor":power_factor_chart_html
            }

        # Render the template with the chart and timestamps
        return render_template('index.html', chart=chart_html, df=df, times={"start": start, "end": end})
    
    @app.route('/hourly_reports', methods=["GET", "POST"])
    def hourly_reports():
        if request.method == "POST":
            start = request.form.get("timestamp_start")
            end = request.form.get("timestamp_end")
        else:
            start,end = None, None
        
        start, end = helpers.parse_timestamps(start, end, 24)  # Default last 6 hours

        query = f"select * from hourSummary"
        df = helpers.fetch_chart_data(query)
        
        chart_html = None

        if df.empty:
            chart_html = "<p class='text-center text-red-500 p-8'>No data available for the selected time range.</p>"
        else:
            fig = px.bar(df, x='timestamp', y='avgVoltage', title="Voltage (Hourly)")
            voltage_chart_html = fig.to_html(full_html=False)

            fig = px.bar(df, x="timestamp", y="avgPower", title="Power (Hourly)")
            power_chart_html = fig.to_html(full_html=False)
            
            fig = px.bar(df, x="timestamp", y="avgCurrent", title="Current (Hourly)")
            current_chart_html = fig.to_html(full_html=False)
            
            fig = px.bar(df, x="timestamp", y="avgPF", title="Power Factor (Hourly)")
            power_factor_chart_html = fig.to_html(full_html=False)

            fig = px.bar(df, x="timestamp", y="energyConsumption", title="Energy Consumption (Hourly)")
            energy_consumption_chart_html = fig.to_html(full_html=False)

            fig = px.bar(df, x="timestamp", y="avgFrequency", title="Frequency (Hourly)")
            frequency_chart_html = fig.to_html(full_html=False)

            chart_html = {
                "power":power_chart_html,
                "voltage":voltage_chart_html,
                "current":current_chart_html,
                "power_factor":power_factor_chart_html,
                "energy_consumption":energy_consumption_chart_html,
                "frequency":frequency_chart_html
            }

        # Render the template with the chart and timestamps
        return render_template('hourly_report.html', chart=chart_html, times={"start": start, "end": end})

