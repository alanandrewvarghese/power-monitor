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

        # Simplified query using direct columns without aggregation
        query = f"""
        SELECT
            DATE(timestamp) as date,
            energyProduced as daily_energy,
            avgVoltage as avg_voltage,
            avgCurrent as avg_current
        FROM hourSummarySolar
        WHERE timestamp >= '{start}' AND timestamp <= '{end}'
        ORDER BY date
        """

        df = helpers.fetch_chart_data(query)

        chart_html = None
        isEmpty = False

        if df.empty:
            isEmpty = True
        else:
            # Daily energy production chart
            daily_df = df.groupby('date').agg({'daily_energy': 'sum'}).reset_index()
            fig = px.bar(daily_df, x='date', y='daily_energy', title="Daily Solar Energy Production (kWh)")
            fig.update_layout(xaxis_title="Date", yaxis_title="Energy (kWh)")
            energy_chart_html = fig.to_html(full_html=False)

            # Average voltage chart
            voltage_df = df.groupby('date').agg({'avg_voltage': 'mean'}).reset_index()
            fig = px.line(voltage_df, x='date', y='avg_voltage', title="Average Voltage by Day")
            fig.update_layout(xaxis_title="Date", yaxis_title="Voltage (V)")
            avg_voltage_html = fig.to_html(full_html=False)

            # Average current chart
            current_df = df.groupby('date').agg({'avg_current': 'mean'}).reset_index()
            fig = px.line(current_df, x='date', y='avg_current', title="Average Current by Day")
            fig.update_layout(xaxis_title="Date", yaxis_title="Current (A)")
            avg_current_html = fig.to_html(full_html=False)

            # Calculate power based on voltage and current (P = V * I)
            df['calculated_power'] = df['avg_voltage'] * df['avg_current']
            power_df = df.groupby('date').agg({'calculated_power': 'mean'}).reset_index()
            fig = px.line(power_df, x='date', y='calculated_power', title="Estimated Average Power by Day")
            fig.update_layout(xaxis_title="Date", yaxis_title="Power (W)")
            power_html = fig.to_html(full_html=False)

            # Cumulative energy chart
            daily_df['cumulative_energy'] = daily_df['daily_energy'].cumsum()
            fig = px.line(daily_df, x='date', y='cumulative_energy', title="Cumulative Solar Energy Production")
            fig.update_layout(xaxis_title="Date", yaxis_title="Total Energy (kWh)")
            cumulative_energy_html = fig.to_html(full_html=False)

            chart_html = {
                "daily_energy": energy_chart_html,
                "avg_voltage": avg_voltage_html,
                "avg_current": avg_current_html,
                "calculated_power": power_html,
                "cumulative_energy": cumulative_energy_html
            }

        # Render the template with the chart and timestamps
        return render_template('production.html', chart=chart_html, isEmpty=isEmpty, times={"start": start, "end": end})
