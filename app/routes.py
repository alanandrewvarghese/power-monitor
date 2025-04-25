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

        query = f"SELECT timestamp, power, voltage, power_factor, current FROM energyConsumption_raw WHERE timestamp > '{start}' AND timestamp < '{end}' LIMIT 86400;"
        df = helpers.fetch_chart_data(query)

        chart_html = None
        isEmpty = False

        if df.empty:
            isEmpty = True
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
        return render_template('index.html', chart=chart_html, isEmpty=isEmpty, times={"start": start, "end": end})

    @app.route('/hourly_reports', methods=["GET", "POST"])
    def hourly_reports():
        if request.method == "POST":
            start = request.form.get("timestamp_start")
            end = request.form.get("timestamp_end")
        else:
            start,end = None, None

        start, end = helpers.parse_timestamps(start, end, 24, True)

        query = f"select * from hourSummary WHERE timestamp >= '{start}' AND timestamp <= '{end}' LIMIT 86400;"
        df = helpers.fetch_chart_data(query)

        chart_html = None
        isEmpty = False

        if df.empty:
            isEmpty = True
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
        return render_template('hourly_report.html', chart=chart_html, isEmpty=isEmpty, times={"start": start, "end": end})

    @app.route('/production', methods=["GET", "POST"])
    def production_reports():
        if request.method == "POST":
            start = request.form.get("timestamp_start")
            end = request.form.get("timestamp_end")
        else:
            start, end = None, None

        # Default to last 7 days for production reports
        start, end = helpers.parse_timestamps(start, end, 168, True)  # 168 hours = 7 days

        # Query to get daily production data
        query = f"""
        SELECT
            DATE(timestamp) as date,
            MAX(energy) - MIN(energy) as daily_energy,
            AVG(power) as avg_power,
            MAX(power) as max_power,
            AVG(voltage) as avg_voltage,
            AVG(current) as avg_current
        FROM measurements
        WHERE timestamp >= '{start}' AND timestamp <= '{end}'
        GROUP BY DATE(timestamp)
        ORDER BY date
        """

        df = helpers.fetch_chart_data(query)

        chart_html = None
        isEmpty = False

        if df.empty:
            isEmpty = True
        else:
            # Daily energy production chart
            fig = px.bar(df, x='date', y='daily_energy', title="Daily Energy Production (kWh)")
            fig.update_layout(xaxis_title="Date", yaxis_title="Energy (kWh)")
            energy_chart_html = fig.to_html(full_html=False)

            # Average power chart
            fig = px.line(df, x='date', y='avg_power', title="Average Power by Day")
            fig.update_layout(xaxis_title="Date", yaxis_title="Power (W)")
            avg_power_chart_html = fig.to_html(full_html=False)

            # Max power chart
            fig = px.line(df, x='date', y='max_power', title="Peak Power by Day")
            fig.update_layout(xaxis_title="Date", yaxis_title="Power (W)")
            max_power_chart_html = fig.to_html(full_html=False)

            # Cumulative energy chart
            df['cumulative_energy'] = df['daily_energy'].cumsum()
            fig = px.line(df, x='date', y='cumulative_energy', title="Cumulative Energy Production")
            fig.update_layout(xaxis_title="Date", yaxis_title="Total Energy (kWh)")
            cumulative_energy_html = fig.to_html(full_html=False)

            # Average voltage chart
            fig = px.line(df, x='date', y='avg_voltage', title="Average Voltage by Day")
            fig.update_layout(xaxis_title="Date", yaxis_title="Voltage (V)")
            avg_voltage_html = fig.to_html(full_html=False)

            chart_html = {
                "daily_energy": energy_chart_html,
                "avg_power": avg_power_chart_html,
                "max_power": max_power_chart_html,
                "cumulative_energy": cumulative_energy_html,
                "avg_voltage": avg_voltage_html
            }

        # Render the template with the chart and timestamps
        return render_template('production.html', chart=chart_html, isEmpty=isEmpty, times={"start": start, "end": end})
