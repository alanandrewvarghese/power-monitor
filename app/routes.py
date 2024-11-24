from flask import render_template, current_app, request
from app import create_app  # Import the create_app function
from app import mysql
from datetime import datetime, timezone, timedelta
import pandas as pd
import plotly.express as px
import pytz

def init_routes(app):

    IST = pytz.timezone('Asia/Kolkata')

    @app.route('/')
    def index():

        timestamp_start = datetime.now(timezone.utc) - timedelta(hours=6)
        timestamp_start = timestamp_start.astimezone(IST)
        timestamp_end = datetime.now(timezone.utc)
        timestamp_end = timestamp_end.astimezone(IST)
        fmt_timestamp_start=timestamp_start.strftime('%Y-%m-%dT%H:%M')
        fmt_timestamp_end=timestamp_end.strftime('%Y-%m-%dT%H:%M')
        query = f"select * from measurements where timestamp > '{timestamp_start}' and timestamp < '{timestamp_end}' limit 86400;"
        
        default_times={
            "start":fmt_timestamp_start,
            "end":fmt_timestamp_end
        }
        
        try:
            cur = mysql.connection.cursor()
            cur.execute(query)
            chart_data = cur.fetchall()
        except Exception as e:
            print(e)

        columns = [desc[0] for desc in cur.description]
        df = pd.DataFrame(chart_data, columns=columns)
        
        fig = px.line(df, x="timestamp", y="power", title="Power Usage Over Time")
        chart_html = fig.to_html(full_html=False)  # Convert Plotly chart to HTML
    
        return render_template('index.html', chart=chart_html, df=df, times=default_times)
    
    @app.route("/update_graph",methods=["POST"])
    def update_graph():
        timestamp_start = request.form.get("timestamp_start")
        timestamp_end = request.form.get("timestamp_end")

        if not timestamp_start:
            timestamp_start = datetime.now(timezone.utc) - timedelta(hours=6)
            timestamp_start = timestamp_start.astimezone(IST)

        if not timestamp_end:
            timestamp_end = datetime.now(timezone.utc)  # Get the current time in UTC and make it timezone-aware
            timestamp_end = timestamp_end.astimezone(IST)

        query = f"select * from measurements where timestamp > '{timestamp_start}' and timestamp < '{timestamp_end}' limit 86400;"

        try:
            cur = mysql.connection.cursor()
            cur.execute(query)
            chart_data = cur.fetchall()
        except Exception as e:
            print(e)

        columns = [desc[0] for desc in cur.description]
        df = pd.DataFrame(chart_data, columns=columns)
        
        fig = px.line(df, x="timestamp", y="power", title="Power Usage Over Time")
        chart_html = fig.to_html(full_html=False)  # Convert Plotly chart to HTML
    
        return render_template('index.html', chart=chart_html, df=df)