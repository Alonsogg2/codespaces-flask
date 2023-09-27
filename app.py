import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

from dash import Dash, dcc, html, Input, Output, callback
import os

KEY_PATH = 'cloudthon-397217-83ae8ab10906.json'

credentials = service_account.Credentials.from_service_account_file(
    KEY_PATH, scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

client = bigquery.Client(credentials=credentials, project=credentials.project_id,)

QUERY =  (
    """SELECT * 
       FROM `cloudthon-397217.my_dataset.avocado` 
       ORDER BY Date desc 
       LIMIT 1000""")

df = client.query(QUERY).to_dataframe()


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div(
    children =[
        html.H1('Avocado Analytics'),
        html.P(
            children=(
                "Analyze the behavior of avocado prices and the number"
                "of avocados sold in the US between 2015 and 2018"
            ),
        ),
        dcc.Dropdown(df['region'].unique(),
        'Albany',
        id='dropdown'
        ),
        html.Div(id='display-value'),
        dcc.Graph(id='graph_avg_price_avocados'),
        dcc.Graph(id='graph_sold_avocados'),
    ]
)

@callback(Output('graph_avg_price_avocados', 'figure'), Input('dropdown', 'value'))
def display_graph_avg_price_avocados(value):
    data_price_avocados = (
    df
    .query(f"type == 'conventional' and region == '{value}'")
    .assign(Date=lambda data: pd.to_datetime(data['Date'], format="%Y-%m-%d"))
    .sort_values(by="Date")
    )

    figure={
                "data": [
                    {
                        "x": data_price_avocados["Date"],
                        "y": data_price_avocados["AveragePrice"],
                        "type": "lines",
                    },
                ],
                "layout": {"title": "Average Price of Avocados"}
    }
    return figure

@callback(Output('graph_sold_avocados', 'figure'), Input('dropdown', 'value'))
def display_graph_sold_avocados(value):
    data_sold_avocados = (
    df
    .query(f"type == 'conventional' and region == '{value}'")
    .assign(Date=lambda data: pd.to_datetime(data['Date'], format="%Y-%m-%d"))
    .sort_values(by="Date")
    )

    figure = {
                "data" : [
                    {
                        "x": data_sold_avocados["Date"],
                        "y": data_sold_avocados["Total_Volume"],
                        "type": "lines",
                    },
                ],
                "layout": {"title": "Sold Avocados"}
            }
    return figure

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True, port=8080)