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

        # Improved query to handle hourly data correctly
        query = f"""
        SELECT
            DATE(timestamp) as date,
            HOUR(timestamp) as hour,
            timestamp,
            energyProduced as hourly_energy,
            avgVoltage as avg_voltage,
            maxVoltage as max_voltage,
            minVoltage as min_voltage,
            avgCurrent as avg_current,
            maxCurrent as max_current
        FROM hourSummarySolar
        WHERE timestamp >= '{start}' AND timestamp <= '{end}'
        ORDER BY date, hour
        """

        df = helpers.fetch_chart_data(query)

        chart_html = None
        isEmpty = False

        if df.empty:
            isEmpty = True
        else:
            # Daily energy production chart - sum hourly values to get daily totals
            daily_df = df.groupby('date').agg({'hourly_energy': 'sum'}).reset_index()
            fig = px.bar(daily_df, x='date', y='hourly_energy', title="Daily Solar Energy Production (kWh)")
            fig.update_layout(xaxis_title="Date", yaxis_title="Energy (kWh)")
            energy_chart_html = fig.to_html(full_html=False)

            # Add hourly energy breakdown for selected days
            # Show first 3 days with data as an example
            unique_days = df['date'].unique()[:3]
            hourly_subset = df[df['date'].isin(unique_days)]
            fig = px.line(hourly_subset, x='timestamp', y='hourly_energy',
                         color='date', title="Hourly Energy Production (Selected Days)")
            fig.update_layout(xaxis_title="Hour", yaxis_title="Energy (kWh)")
            hourly_energy_html = fig.to_html(full_html=False)

            # Voltage chart with daily min/max range
            voltage_df = df.groupby('date').agg({
                'avg_voltage': 'mean',
                'min_voltage': 'min',
                'max_voltage': 'max'
            }).reset_index()
            fig = px.line(voltage_df, x='date',
                         y=['min_voltage', 'avg_voltage', 'max_voltage'],
                         title="Voltage Range by Day",
                         labels={'value': 'Voltage (V)', 'variable': 'Measurement'})
            fig.update_layout(xaxis_title="Date", yaxis_title="Voltage (V)")
            voltage_html = fig.to_html(full_html=False)

            # Update chart dictionary with new visualizations
            chart_html = {
                "daily_energy": energy_chart_html,
                "hourly_energy": hourly_energy_html,
                "voltage": voltage_html,
            }

        # Render the template with the chart and timestamps
        return render_template('production.html', chart=chart_html, isEmpty=isEmpty, times={"start": start, "end": end})
