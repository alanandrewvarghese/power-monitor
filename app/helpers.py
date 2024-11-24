import pandas as pd
from app import mysql
from datetime import datetime, timezone, timedelta
import pandas as pd
import pytz

def fetch_chart_data(query):
    try:
        cur = mysql.connection.cursor()
        cur.execute(query)
        chart_data = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        df = pd.DataFrame(chart_data, columns=columns)
        return df
    except Exception as e:
        print(f"Database error: {e}")
        return pd.DataFrame()

def parse_timestamps(start, end, default_hours=6):
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.now(timezone.utc)

    if start:
        start = datetime.strptime(start, '%Y-%m-%dT%H:%M').astimezone(IST)
    else:
        start = (now - timedelta(hours=default_hours)).astimezone(IST)

    if end:
        end = datetime.strptime(end, '%Y-%m-%dT%H:%M').astimezone(IST)
    else:
        end = now.astimezone(IST)

    return start.strftime('%Y-%m-%dT%H:%M'), end.strftime('%Y-%m-%dT%H:%M')
