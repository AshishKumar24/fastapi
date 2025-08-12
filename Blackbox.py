import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
import datacompy
import duckdb
import uuid
import os
import base64
import io
import json
from flask import request

# Initialize the Dash app with Material theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MATERIA])
app.title = "DataComPy Dashboard with DuckDB"

# Generate unique session ID
def get_session_id():
    if not hasattr(dash.callback_context, 'session_id'):
        dash.callback_context.session_id = str(uuid.uuid4())
    return dash.callback_context.session_id

# Initialize DuckDB connection for the session
def get_db_connection():
    session_id = get_session_id()
    conn = duckdb.connect(f'session_{session_id}.db')
    return conn

# Clean up DuckDB file when session ends
@app.server.before_request
def cleanup_old_sessions():
    # Cleanup logic would go here - in practice you'd want to implement
    # proper session management with actual timeout detection
    pass

# App layout
app.layout = dbc.Container(
    fluid=True,
    children=[
        # Header
        dbc.Row(
            dbc.Col(
                html.H1("DataComPy Data Comparison Dashboard", className="text-center my-4"),
                width=12
            )
        ),
        
        # Session status indicator
        html.Div(id='session-status', style={'display': 'none'}),
        dcc.Store(id='session-id', data=get_session_id()),
        
        # Main content
        dbc.Row([
            # Sidebar for inputs
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Data Input Configuration"),
                    dbc.CardBody([
                        dcc.Tabs(id="input-tabs", active_tab="csv-tab", children=[
                            dcc.Tab(label="CSV Upload", value="csv-tab", children=[
                                html.H5("Upload CSV Files"),
                                dcc.Upload(
                                    id='upload-df1',
                                    children=html.Div([
                                        'Drag and Drop or ',
                                        html.A('Select File 1')
                                    ]),
                                    multiple=False,
                                    className="mb-3"
                                ),
                                dcc.Upload(
                                    id='upload-df2',
                                    children=html.Div([
                                        'Drag and Drop or ',
                                        html.A('Select File 2')
                                    ]),
                                    multiple=False
                                ),
                            ]),
                            dcc.Tab(label="SQL Query", value="sql-tab", children=[
                                html.H5("Enter SQL Queries"),
                                dbc.Textarea(
                                    id='sql-query1',
                                    placeholder='SELECT * FROM table1...',
                                    className="mb-3"
                                ),
                                dbc.Textarea(
                                    id='sql-query2',
                                    placeholder='SELECT * FROM table2...'
                                ),
                                dbc.Button("Execute Queries", id="execute-sql", color="primary", className="mt-2")
                            ])
                        ]),
                        
                        html.Hr(),
                        
                        html.H5("Join Configuration"),
                        dbc.Row([
                            dbc.Col([
                                dcc.Dropdown(
                                    id='join-columns1',
                                    placeholder='Select join columns from DF1',
                                    multi=True
                                )
                            ]),
                            dbc.Col([
                                dcc.Dropdown(
                                    id='join-columns2',
                                    placeholder='Select join columns from DF2',
                                    multi=True
                                )
                            ])
                        ], className="mb-3"),
                        
                        html.Hr(),
                        
                        dbc.Button(
                            "Select Compare Columns",
                            id="select-columns-btn",
                            color="primary",
                            disabled=True,
                            className="mb-3"
                        ),
                        
                        dbc.Button(
                            "Run Comparison",
                            id="run-comparison",
                            color="success",
                            disabled=True,
                            className="w-100"
                        )
                    ])
                ], className="mb-4"),
                
                # Comparison results summary cards
                dbc.Card(id="summary-cards", className="mb-4"),
                
                # Data preview
                dbc.Card([
                    dbc.CardHeader("Data Preview"),
                    dbc.CardBody([
                        dcc.Tabs(id="preview-tabs", children=[
                            dcc.Tab(label="DF1 Preview", value="df1-tab", children=[
                                html.Div(id='df1-preview')
                            ]),
                            dcc.Tab(label="DF2 Preview", value="df2-tab", children=[
                                html.Div(id='df2-preview')
                            ])
                        ])
                    ])
                ])
            ], md=4),
            
            # Main results area
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Comparison Results"),
                    dbc.CardBody([
                        dcc.Tabs(id="results-tabs", active_tab="overview-tab", children=[
                            dcc.Tab(label="Overview", value="overview-tab", children=[
                                html.Div(id="overview-results")
                            ]),
                            dcc.Tab(label="Row Analysis", value="row-tab", children=[
                                html.Div(id="row-analysis")
                            ]),
                            dcc.Tab(label="Column Analysis", value="column-tab", children=[
                                html.Div(id="column-analysis")
                            ]),
                            dcc.Tab(label="Mismatch Details", value="mismatch-tab", children=[
                                html.Div(id="mismatch-details")
                            ])
                        ])
                    ])
                ])
            ], md=8)
        ]),
        
        # Modal for selecting compare columns
        dbc.Modal([
            dbc.ModalHeader("Select Columns to Compare"),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col([
                        html.H5("DF1 Columns"),
                        dbc.Checklist(
                            id="all-columns-df1",
                            options=[],
                            value=[],
                            labelStyle={"display": "block"}
                        )
                    ]),
                    dbc.Col([
                        html.H5("DF2 Columns"),
                        dbbc.Checklist(
                            id="all-columns-df2",
                            options=[],
                            value=[],
                            labelStyle={"display": "block"}
                        )
                    ])
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Input(id="column-search-df1", placeholder="Search DF1 columns...", className="mb-2"),
                        dbc.Button("Select All DF1", id="select-all-df1", color="primary", outline=True, size="sm")
                    ]),
                    dbc.Col([
                        dbc.Input(id="column-search-df2", placeholder="Search DF2 columns...", className="mb-2"),
                        dbc.Button("Select All DF2", id="select-all-df2", color="primary", outline=True, size="sm")
                    ])
                ])
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="cancel-columns", color="secondary", className="mr-2"),
                dbc.Button("Apply", id="apply-columns", color="primary")
            ])
        ], id="columns-modal", size="lg"),
        
        # Store session data in DuckDB
        dcc.Store(id='session-state'),
        
        # Interval for periodic cleanup checks
        dcc.Interval(id='cleanup-interval', interval=60*1000, n_intervals=0)
    ],
    className="dbc",
    style={"padding": "20px"}
)

# Callbacks for handling file uploads and storing in DuckDB
@callback(
    Output('join-columns1', 'options'),
    Output('session-state', 'data'),
    Input('upload-df1', 'contents'),
    State('session-id', 'data'),
    prevent_initial_call=True
)
def parse_and_store_df1(contents, session_id):
    if contents is None:
        return dash.no_update, dash.no_update
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    try:
        conn = get_db_connection()
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        
        # Create temporary table name with session ID
        table_name = f"df1_{session_id}"
        
        # Register the DataFrame with DuckDB
        conn.register(table_name, df)
        
        # Store metadata in session state
        session_data = {
            'df1_table': table_name,
            'df1_columns': df.columns.tolist()
        }
        
        options = [{'label': col, 'value': col} for col in df.columns]
        return options, session_data
    except Exception as e:
        print(e)
        return [], None

@callback(
    Output('join-columns2', 'options'),
    Output('session-state', 'data', allow_duplicate=True),
    Input('upload-df2', 'contents'),
    State('session-id', 'data'),
    State('session-state', 'data'),
    prevent_initial_call=True
)
def parse_and_store_df2(contents, session_id, session_data):
    if contents is None:
        return dash.no_update, dash.no_update
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    try:
        conn = get_db_connection()
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        
        # Create temporary table name with session ID
        table_name = f"df2_{session_id}"
        
        # Register the DataFrame with DuckDB
        conn.register(table_name, df)
        
        # Update session data
        if session_data is None:
            session_data = {}
            
        session_data.update({
            'df2_table': table_name,
            'df2_columns': df.columns.tolist()
        })
        
        options = [{'label': col, 'value': col} for col in df.columns]
        return options, session_data
    except Exception as e:
        print(e)
        return [], session_data

# SQL query execution
@callback(
    Output('session-state', 'data', allow_duplicate=True),
    Input('execute-sql', 'n_clicks'),
    State('sql-query1', 'value'),
    State('sql-query2', 'value'),
    State('session-id', 'data'),
    State('session-state', 'data'),
    prevent_initial_call=True
)
def execute_sql_queries(n_clicks, query1, query2, session_id, session_data):
    if n_clicks is None:
        return dash.no_update
    
    try:
        conn = get_db_connection()
        session_data = session_data or {}
        
        # Execute queries and store results
        if query1:
            table_name1 = f"sql_df1_{session_id}"
            conn.execute(f"CREATE TABLE {table_name1} AS {query1}")
            cols1 = conn.execute(f"SELECT * FROM {table_name1} LIMIT 0").description
            session_data.update({
                'df1_table': table_name1,
                'df1_columns': [col[0] for col in cols1]
            })
            
        if query2:
            table_name2 = f"sql_df2_{session_id}"
            conn.execute(f"CREATE TABLE {table_name2} AS {query2}")
            cols2 = conn.execute(f"SELECT * FROM {table_name2} LIMIT 0").description
            session_data.update({
                'df2_table': table_name2,
                'df2_columns': [col[0] for col in cols2]
            })
            
        return session_data
    except Exception as e:
        print(f"SQL Error: {e}")
        return dash.no_update

# Run DataComPy comparison using DuckDB data
@callback(
    Output('summary-cards', 'children'),
    Input('run-comparison', 'n_clicks'),
    State('session-state', 'data'),
    State('join-columns1', 'value'),
    State('join-columns2', 'value'),
    State('all-columns-df1', 'value'),
    State('all-columns-df2', 'value'),
    prevent_initial_call=True
)
def run_comparison(n_clicks, session_data, join_cols1, join_cols2, compare_cols1, compare_cols2):
    if n_clicks is None or not session_data:
        return dash.no_update
    
    try:
        conn = get_db_connection()
        
        # Get data from DuckDB
        df1 = conn.execute(f"SELECT * FROM {session_data['df1_table']}").df()
        df2 = conn.execute(f"SELECT * FROM {session_data['df2_table']}").df()
        
        # Run comparison
        compare = datacompy.Compare(
            df1, 
            df2, 
            join_columns=dict(zip(join_cols1, join_cols2)),
            df1_name='Dataset1', 
            df2_name='Dataset2'
        )
        
        # Store report in DuckDB
        report_table = f"report_{get_session_id()}"
        report_df = pd.DataFrame([{'report': compare.report()}])
        conn.register(report_table, report_df)
        
        # Create summary cards
        cards = dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Total Rows"),
                dbc.CardBody([
                    html.H4(f"{compare.all_rows_cnt:,}", className="card-title")
                ])
            ]), md=3),
            
            dbc.Col(dbc.Card([
                dbc.CardHeader("Matching Rows"),
                dbc.CardBody([
                    html.H4(f"{compare.all_rows_cnt - (compare.df1_unq_rows + compare.df2_unq_rows):,}", className="card-title")
                ])
            ]), md=3),
            
            dbc.Col(dbc.Card([
                dbc.CardHeader("Unique in DF1"),
                dbc.CardBody([
                    html.H4(f"{compare.df1_unq_rows:,}", className="card-title")
                ])
            ]), md=3),
            
            dbc.Col(dbc.Card([
                dbc.CardHeader("Unique in DF2"),
                dbc.CardBody([
                    html.H4(f"{compare.df2_unq_rows:,}", className="card-title")
                ])
            ]), md=3)
        ], className="mb-4")
        
        return cards
    except Exception as e:
        print(f"Comparison error: {e}")
        return html.Div("Error running comparison", className="alert alert-danger")

# Session cleanup
@callback(
    Output('session-status', 'children'),
    Input('cleanup-interval', 'n_intervals'),
    State('session-id', 'data'),
    prevent_initial_call=True
)
def cleanup_sessions(n_intervals, current_session_id):
    # In a production environment, you'd implement proper session tracking
    # and cleanup of old session DB files. This is a simplified version.
    
    # List all session DB files
    db_files = [f for f in os.listdir() if f.startswith('session_') and f.endswith('.db')]
    
    # For demo purposes, we just check if current session's DB exists
    current_db = f'session_{current_session_id}.db'
    if not os.path.exists(current_db):
        return "Session DB not found"
    
    return "Session active"

# When the app is closed, clean up the DuckDB file
@app.server.before_first_request
def setup_cleanup():
    def cleanup_on_exit():
        session_id = get_session_id()
        db_file = f'session_{session_id}.db'
        if os.path.exists(db_file):
            os.remove(db_file)
    
    import atexit
    atexit.register(cleanup_on_exit)

if __name__ == '__main__':
    app.run_server(debug=True)
