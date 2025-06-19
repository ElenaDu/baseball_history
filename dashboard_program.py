import sqlite3
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output

# Initialize Dash app
app = Dash(__name__)
server = app.server

# Function to fetch data with error handling
def load_batting_leaders():
    try:
        with sqlite3.connect('./db/baseball_stats.db') as conn:
            query = '''
                SELECT t.name AS team, COUNT(*) AS leaders
                FROM batting_stats b
                JOIN teams t ON b.team_id = t.id
                GROUP BY t.name
                ORDER BY leaders DESC
                LIMIT 10
            '''
            return pd.read_sql_query(query, conn)
    except Exception as e:
        print(f"Database error (batting leaders): {e}")
        return pd.DataFrame(columns=["team", "leaders"])

# Function to fetch pitching leaders
def load_pitching_leaders():
    try:
        with sqlite3.connect('./db/baseball_stats.db') as conn:
            query = '''
                SELECT t.name AS team, COUNT(*) AS leaders
                FROM pitching_stats p
                JOIN teams t ON p.team_id = t.id
                GROUP BY t.name
                ORDER BY leaders DESC
                LIMIT 10
            '''
            return pd.read_sql_query(query, conn)
    except Exception as e:
        print(f"Database error (pitching leaders): {e}")
        return pd.DataFrame(columns=["team", "leaders"])

# Stat options mapping (label: (table, stat))
stat_options = {
    "1. Home Runs (Batting)": ("batting_stats", "Home Runs"),
    "2. Base on Balls (Batting)": ("batting_stats", "Base on Balls"),
    "3. Wins (Pitching)": ("pitching_stats", "Wins"),
    "4. ERA (Pitching)": ("pitching_stats", "ERA")
}

# Load static data
batting_df = load_batting_leaders()
pitching_df = load_pitching_leaders()

# App layout
app.layout = html.Div([
    html.H2("Baseball Stats Dashboard", style={'textAlign': 'center'}),
    
    dcc.Graph(
        id='batting-leaders-chart',
        figure=px.bar(
            batting_df, x="team", y="leaders", 
            title="Top 10 Teams with Most Batting Leaders",
            labels={"team": "Team", "leaders": "Number of Leaders"},
            color_discrete_sequence=["royalblue"]
        )
    ),
    
    dcc.Graph(
        id='pitching-leaders-chart',
        figure=px.bar(
            pitching_df, x="team", y="leaders",
            title="Top 10 Teams with Most Pitching Leaders",
            labels={"team": "Team", "leaders": "Number of Leaders"},
            color_discrete_sequence=["crimson"]
        )
    ),

    html.Hr(),

    dcc.Dropdown(
        id='stat-dropdown',
        options=[{"label": label, "value": label} for label in stat_options],
        value="1. Home Runs (Batting)"
    ),
    dcc.Graph(id='top-players-chart'),

    html.Hr(),

    
    dcc.Graph(id='trend-chart')
])

# Callback to update top players chart based on dropdown
@app.callback(
    Output('top-players-chart', 'figure'),
    Input('stat-dropdown', 'value')
)
def update_top_players(selected_label):
    table, stat = stat_options[selected_label]
    try:
        with sqlite3.connect('./db/baseball_stats.db') as conn:
            query = f'''
                SELECT
                    name,
                    MAX(value) AS max_value
                FROM {table}
                WHERE stat = ?
                GROUP BY name
                ORDER BY max_value DESC
                LIMIT 5
            '''
            df = pd.read_sql_query(query, conn, params=(stat,))
            fig = px.bar(
                df,
                x="name",
                y="max_value",
                title=f"Top 5 Players by '{stat}'",
                labels={"max_value": stat, "name": "Player"},
                color="name"
            )
            return fig
    except Exception as e:
        print(f"Error loading top players chart: {e}")
        return px.bar(title="Error loading data")

# Callback to update yearly trend chart based on same dropdown
@app.callback(
    Output('trend-chart', 'figure'),
    Input('stat-dropdown', 'value')
)
def update_trend_chart(selected_label):
    table, stat = stat_options[selected_label]
    try:
        with sqlite3.connect('./db/baseball_stats.db') as conn:
            query = f'''
                SELECT year, value
                FROM {table}
                WHERE stat = ?
                ORDER BY year
            '''
            df = pd.read_sql_query(query, conn, params=(stat,))
            if df.empty:
                return px.line(title=f"No data for {stat}")
            fig = px.line(
                df,
                x='year',
                y='value',
                title=f"Yearly Top '{stat}' Value",
                labels={'year': 'Year', 'value': stat},
                markers=True
            )
            return fig
    except Exception as e:
        print(f"Error loading trend chart: {e}")
        return px.line(title="Error loading data")

if __name__ == "__main__":
    app.run(debug=True)
