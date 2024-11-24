from flask import render_template, current_app
from app import create_app  # Import the create_app function
from app import mysql
import pandas as pd
import plotly.express as px

def init_routes(app):
    @app.route('/')
    def index():

        try:
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM power_readings')
            chart_data = cur.fetchall()
            print(chart_data)
        except Exception as e:
            print(e)

        columns = [desc[0] for desc in cur.description]
        df = pd.DataFrame(chart_data, columns=columns)
        
        fig = px.line(df, x="date", y="power_usage", title="Power Usage Over Time")
        chart_html = fig.to_html(full_html=False)  # Convert Plotly chart to HTML
    
        return render_template('index.html', chart=chart_html, df=df)