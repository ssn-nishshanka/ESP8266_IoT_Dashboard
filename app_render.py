## iot based dashboard

# Import libraries
import dash  # Dash framework for building interactive web apps
from dash import dcc, html  # Dash components for graphs and HTML elements
from dash.dependencies import Input, Output  # For creating callbacks
import plotly.graph_objs as go  # For creating interactive Plotly graphs
# import serial  # Removed for Render
import threading  # For running background tasks
import time  # For timestamps and delays
import pandas as pd  # For data storage and manipulation
import os  # To check if CSV exists
import numpy as np  # For predictive trend calculations

# Persistent logging setup
CSV_FILE = "sensor_log.csv"

# Create an empty DataFrame to store sensor readings or load existing CSV
if os.path.exists(CSV_FILE):
    data = pd.read_csv(CSV_FILE)
else:
    data = pd.DataFrame(columns=["Time", "Temperature", "Humidity", "Light"])


# Skip serial read on Render
def read_serial():
    """Render environment — no serial port. This function does nothing."""
    print("Serial reading skipped — running on Render with CSV data only.")
    while True:
        time.sleep(5)


# On Render, skip launching serial thread
if os.environ.get("RENDER", "true") == "true":
    print("Running on Render environment — skipping serial port thread.")
else:
    thread = threading.Thread(target=read_serial)
    thread.daemon = True
    thread.start()

# Setup Dash App Layout
app = dash.Dash(__name__)
server = app.server

# Layout of the dashboard
app.layout = html.Div([
    html.H2("Smart Classroom Environment Tracker",
            style={'textAlign': 'center', 'color': '#003366', 'margin-bottom': '20px'}),

    # Cards for alerts and summary metrics
    html.Div([
        html.Div([
            html.H4("Alert", style={'color': '#ff3333'}),
            html.Div(id='alert', style={'fontWeight': 'bold', 'color': 'red', 'fontSize': '16px'})
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '15px',
                  'border': '1px solid #ccc', 'border-radius': '12px', 'box-shadow': '3px 3px 10px #ddd',
                  'backgroundColor': '#fff'}),

        html.Div([
            html.H4("Summary", style={'color': '#003366'}),
            html.Label("Select Summary Period:", style={'font-weight': 'bold'}),
            dcc.Dropdown(
                id='summary-period',
                options=[
                    {'label': 'All', 'value': 'all'},
                    {'label': 'Day', 'value': 'day'},
                    {'label': 'Week', 'value': 'week'},
                    {'label': 'Month', 'value': 'month'},
                    {'label': 'Year', 'value': 'year'}
                ],
                value='all',
                clearable=False,
                style={'width': '50%'}
            ),
            html.Div(id='summary-cards', style={'padding': '10px'})
        ], style={'width': '65%', 'display': 'inline-block', 'padding': '15px',
                  'border': '1px solid #ccc', 'border-radius': '12px', 'box-shadow': '3px 3px 10px #ddd',
                  'margin-left': '2%', 'backgroundColor': '#f9f9f9'})
    ], style={'display': 'flex', 'justify-content': 'space-between', 'margin-bottom': '25px'}),

    # Settings for graphs (only sensor selection and data slider)
    html.Div([
        html.Label("Select Sensor to Display:", style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id='sensor-dropdown',
            options=[
                {'label': 'Temperature', 'value': 'Temperature'},
                {'label': 'Humidity', 'value': 'Humidity'}
            ],
            value=['Temperature', 'Humidity'],
            multi=True
        ),
        html.Label("Number of Data Points:", style={'font-weight': 'bold', 'margin-top': '10px'}),
        dcc.Slider(id='data-slider', min=5, max=50, step=1, value=20)
    ], style={'padding': '10px', 'margin-bottom': '20px', 'border': '1px solid #ddd',
              'border-radius': '10px', 'box-shadow': '2px 2px 8px #ddd', 'backgroundColor': '#fafafa'}),

    # Graphs section
    html.Div([
        html.Div([
            dcc.Graph(id='line-graph', style={'height': '400px', 'width': '75%', 'display': 'inline-block'}),
            html.Div([
                html.Label("Historical Trends:", style={'font-weight': 'bold'}),
                dcc.Checklist(
                    id='line-historical-check',
                    options=[{'label': 'Show Historical Trends', 'value': 'show'}],
                    value=[]
                ),
                html.Div([
                    html.Label("Select Day for Historical View:", style={'font-weight': 'bold'}),
                    dcc.Dropdown(
                        id='historical-day-dropdown',
                        options=[],
                        placeholder="Select a day",
                        clearable=True
                    )
                ], id='historical-day-container')
            ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '23%', 'margin-left': '2%'}),
        ], style={'display': 'flex', 'justify-content': 'space-between'}),

        html.Div([  # Gauge charts for temperature and humidity
            dcc.Graph(id='gauge-graph', style={'height': '300px', 'display': 'inline-block', 'width': '48%'}),
            dcc.Graph(id='humidity-gauge',
                      style={'height': '300px', 'display': 'inline-block', 'width': '48%', 'margin-left': '4%'}),
        ]),
        html.Div([
            dcc.Graph(id='light-bar', style={'height': '300px', 'display': 'inline-block', 'width': '60%'}),
            html.Div([
                html.Label("Select Day for Light Chart:", style={'font-weight': 'bold'}),
                dcc.Dropdown(id='day-dropdown', options=[], placeholder="Select a day", clearable=True),
                html.Label("Light Chart Period:", style={'font-weight': 'bold', 'margin-top': '10px'}),
                dcc.RadioItems(
                    id='light-period',
                    options=[
                        {'label': 'Day', 'value': 'day'},
                        {'label': 'Week', 'value': 'week'},
                        {'label': 'Month', 'value': 'month'}
                    ],
                    value='day',
                    labelStyle={'display': 'inline-block', 'margin-right': '10px'}
                )
            ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '35%', 'margin-left': '3%'}),
        ])
    ]),

    dcc.Interval(id='interval', interval=2000, n_intervals=0)
])


# Main Dashboard Callback
@app.callback(
    [Output('line-graph', 'figure'),
     Output('gauge-graph', 'figure'),
     Output('humidity-gauge', 'figure'),
     Output('light-bar', 'figure'),
     Output('alert', 'children'),
     Output('summary-cards', 'children')],
    [Input('interval', 'n_intervals'),
     Input('sensor-dropdown', 'value'),
     Input('data-slider', 'value'),
     Input('line-historical-check', 'value'),
     Input('historical-day-dropdown', 'value'),
     Input('day-dropdown', 'value'),
     Input('light-period', 'value'),
     Input('summary-period', 'value')]
)
def update_dashboard(n, sensors, n_points, line_hist_check, selected_hist_day, selected_day, light_period, summary_period):
    global data
    if len(data) == 0:
        empty_fig = go.Figure()
        return empty_fig, empty_fig, empty_fig, empty_fig, "", ""

    df = data.copy()
    df['DateTime'] = pd.to_datetime(df['Time'], format="%Y-%m-%d %H:%M:%S")
    df['Date'] = df['DateTime'].dt.date

    # Historical or Current Day Filtering for Line Chart
    df_line = df.copy()
    if 'show' in line_hist_check and selected_hist_day:
        df_line = df_line[df_line['Date'] == pd.to_datetime(selected_hist_day).date()]
    else:
        current_day = df['Date'].iloc[-1]
        df_line = df_line[df['Date'] == current_day]
        df_line = df_line.tail(n_points)  # Limit recent points for live/current day

    # Line Chart
    line_fig = go.Figure()
    if 'Temperature' in sensors:
        line_fig.add_trace(go.Scatter(
            x=df_line["Time"], y=df_line["Temperature"],
            name="Temperature (°C)", mode='lines+markers',
            line=dict(color='firebrick')
        ))
        ma_temp = df_line["Temperature"].rolling(3, min_periods=1).mean()
        line_fig.add_trace(go.Scatter(
            x=df_line["Time"], y=ma_temp,
            name="Temperature MA (forecast)", mode='lines',
            line=dict(dash='dot', color='red')
        ))
    if 'Humidity' in sensors:
        line_fig.add_trace(go.Scatter(
            x=df_line["Time"], y=df_line["Humidity"],
            name="Humidity (%)", mode='lines+markers',
            line=dict(color='royalblue')
        ))
        ma_hum = df_line["Humidity"].rolling(3, min_periods=1).mean()
        line_fig.add_trace(go.Scatter(
            x=df_line["Time"], y=ma_hum,
            name="Humidity MA (forecast)", mode='lines',
            line=dict(dash='dot', color='blue')
        ))
    line_fig.update_layout(
        title="Live Environment Line Chart",
        xaxis_title="Time", yaxis_title="Value",
        template="plotly_white", hovermode="x unified",
        plot_bgcolor='#fafafa', paper_bgcolor='#fafafa'
    )

    # Gauges
    latest_temp = df_line["Temperature"].iloc[-1]
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=latest_temp,
        title={'text': "Temperature Gauge (°C)"},
        gauge={'axis': {'range': [0, 50]},
               'bar': {'color': "red" if latest_temp > 35 else "limegreen"},
               'steps': [
                   {'range': [0, 25], 'color': '#90ee90'},
                   {'range': [25, 35], 'color': '#ffeb99'},
                   {'range': [35, 50], 'color': '#ff9999'}
               ]}
    ))
    gauge_fig.update_layout(template="plotly_white", paper_bgcolor='#fafafa')

    latest_hum = df_line["Humidity"].iloc[-1]
    hum_gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=latest_hum,
        title={'text': "Humidity Gauge (%)"},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "red" if latest_hum > 80 else "limegreen"},
               'steps': [
                   {'range': [0, 50], 'color': '#90ee90'},
                   {'range': [50, 80], 'color': '#ffeb99'},
                   {'range': [80, 100], 'color': '#ff9999'}
               ]}
    ))
    hum_gauge_fig.update_layout(template="plotly_white", paper_bgcolor='#fafafa')

    # Light Sensor Bar (percentage of readings)
    df_light = df.copy()
    if light_period == 'day' and selected_day:
        df_light = df_light[df_light['Date'] == pd.to_datetime(selected_day).date()]
    elif light_period == 'week':
        last_date = df_light['Date'].max()
        start_date = last_date - pd.Timedelta(days=6)
        df_light = df_light[df_light['Date'].between(start_date, last_date)]
    elif light_period == 'month':
        last_date = df_light['Date'].max()
        start_date = last_date - pd.Timedelta(days=29)
        df_light = df_light[df_light['Date'].between(start_date, last_date)]

    total = len(df_light)
    light_present_pct = 100 * (df_light['Light'] == "Light PRESENT").sum() / total if total > 0 else 0
    light_absent_pct = 100 - light_present_pct

    light_fig = go.Figure(go.Bar(
        x=["Light PRESENT", "No Light"],
        y=[light_present_pct, light_absent_pct],
        marker_color=['gold', 'lightgrey'],
        text=[f"{light_present_pct:.1f}%", f"{light_absent_pct:.1f}%"],
        textposition='auto'
    ))
    light_fig.update_layout(
        title="Percentage of Light Presence vs Absence",
        xaxis_title="Light Status",
        yaxis_title="Percentage (%)",
        template="plotly_white",
        plot_bgcolor='#fafafa',
        paper_bgcolor='#fafafa',
        yaxis=dict(range=[0, 100])
    )

    # Alert Message
    alert_msg = ""
    if latest_temp > 35:
        alert_msg += f"⚠ High Temperature! {latest_temp}°C. "
    if latest_hum > 80:
        alert_msg += f"⚠ High Humidity! {latest_hum}%."
    if 'Light PRESENT' in df["Light"].iloc[-1]:
        alert_msg += " 💡 Light Detected!"

    # Summary Cards based on period
    df_summary = df.copy()
    today = df_summary['Date'].max()
    if summary_period == 'day':
        df_summary = df_summary[df_summary['Date'] == today]
    elif summary_period == 'week':
        df_summary = df_summary[df_summary['Date'] >= today - pd.Timedelta(days=6)]
    elif summary_period == 'month':
        df_summary = df_summary[df_summary['Date'] >= today - pd.Timedelta(days=29)]
    elif summary_period == 'year':
        df_summary = df_summary[df_summary['Date'] >= today - pd.Timedelta(days=364)]
    # 'all' shows entire df

    max_temp = df_summary["Temperature"].max()
    min_temp = df_summary["Temperature"].min()
    max_hum = df_summary["Humidity"].max()
    min_hum = df_summary["Humidity"].min()
    light_on_pct = 100 * (df_summary["Light"] == "Light PRESENT").sum() / len(df_summary) if len(df_summary) > 0 else 0

    summary = html.Div([
        html.Div(f"Max Temp: {max_temp}°C | Min Temp: {min_temp}°C",
                 style={'padding': '8px', 'font-weight': 'bold'}),
        html.Div(f"Max Humidity: {max_hum}% | Min Humidity: {min_hum}%",
                 style={'padding': '8px', 'font-weight': 'bold'}),
        html.Div(f"Light ON: {light_on_pct:.1f}%",
                 style={'padding': '8px', 'font-weight': 'bold'})
    ], style={'display': 'flex', 'justify-content': 'space-around',
              'backgroundColor': '#f9f9f9', 'padding': '15px', 'border-radius': '12px',
              'box-shadow': '2px 2px 6px #ddd', 'color': '#333'})

    return line_fig, gauge_fig, hum_gauge_fig, light_fig, alert_msg, summary


# Dropdown for Light Chart
@app.callback(
    Output('day-dropdown', 'options'),
    [Input('interval', 'n_intervals')]
)
def update_day_options(n):
    if len(data) == 0:
        return []
    df_days = data.copy()
    df_days['Date'] = pd.to_datetime(df_days['Time'], format="%Y-%m-%d %H:%M:%S").dt.date
    days = df_days['Date'].unique()
    return [{'label': str(day), 'value': str(day)} for day in days]


# Dropdown for Historical Trends (Line Chart)
@app.callback(
    Output('historical-day-dropdown', 'options'),
    [Input('interval', 'n_intervals')]
)
def update_hist_day_options(n):
    if len(data) == 0:
        return []
    df_days = data.copy()
    df_days['Date'] = pd.to_datetime(df_days['Time'], format="%Y-%m-%d %H:%M:%S").dt.date
    days = df_days['Date'].unique()
    return [{'label': str(day), 'value': str(day)} for day in days]


# Show/Hide Dropdown depending on Checkbox
@app.callback(
    Output('historical-day-container', 'style'),
    [Input('line-historical-check', 'value')]
)
def toggle_hist_dropdown_visibility(value):
    if 'show' in value:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


# Disable Slider when Historical Trends selected
@app.callback(
    Output('data-slider', 'disabled'),
    [Input('line-historical-check', 'value')]
)
def disable_slider(value):
    return 'show' in value


# Run the Dash server
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=10000, debug=False)
