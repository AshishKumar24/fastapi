import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
import datacompy
import base64
import io
import json

# Initialize the Dash app with Material theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MATERIA])
app.title = "DataComPy Dashboard"

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
                        dbc.Checklist(
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
                        dbbc.Button("Select All DF2", id="select-all-df2", color="primary", outline=True, size="sm")
                    ])
                ])
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="cancel-columns", color="secondary", className="mr-2"),
                dbc.Button("Apply", id="apply-columns", color="primary")
            ])
        ], id="columns-modal", size="lg"),
        
        # Store for the dataframes and comparison results
        dcc.Store(id='stored-df1'),
        dcc.Store(id='stored-df2'),
        dcc.Store(id='stored-compare')
    ],
    className="dbc",
    style={"padding": "20px"}
)

# Callbacks for handling file uploads
@callback(
    Output('stored-df1', 'data'),
    Output('join-columns1', 'options'),
    Input('upload-df1', 'contents'),
    prevent_initial_call=True
)
def parse_df1(contents):
    if contents is None:
        return dash.no_update, dash.no_update
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    try:
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        options = [{'label': col, 'value': col} for col in df.columns]
        return df.to_json(date_format='iso', orient='split'), options
    except Exception as e:
        print(e)
        return None, []

@callback(
    Output('stored-df2', 'data'),
    Output('join-columns2', 'options'),
    Input('upload-df2', 'contents'),
    prevent_initial_call=True
)
def parse_df2(contents):
    if contents is None:
        return dash.no_update, dash.no_update
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    try:
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        options = [{'label': col, 'value': col} for col in df.columns]
        return df.to_json(date_format='iso', orient='split'), options
    except Exception as e:
        print(e)
        return None, []

# Update column selection dropdowns when data changes
@callback(
    Output('all-columns-df1', 'options'),
    Output('all-columns-df1', 'value'),
    Input('stored-df1', 'data'),
)
def update_columns_df1(json_data):
    if json_data is None:
        return [], []
    
    df = pd.read_json(json_data, orient='split')
    options = [{'label': col, 'value': col} for col in df.columns]
    return options, df.columns.tolist()

@callback(
    Output('all-columns-df2', 'options'),
    Output('all-columns-df2', 'value'),
    Input('stored-df2', 'data'),
)
def update_columns_df2(json_data):
    if json_data is None:
        return [], []
    
    df = pd.read_json(json_data, orient='split')
    options = [{'label': col, 'value': col} for col in df.columns]
    return options, df.columns.tolist()

# Enable/disable buttons based on selection state
@callback(
    Output('select-columns-btn', 'disabled'),
    Input('join-columns1', 'value'),
    Input('join-columns2', 'value')
)
def enable_column_selection(join1, join2):
    if join1 is None or join2 is None:
        return True
    return not (len(join1) > 0 and len(join2) > 0)

# Modal for column selection
@callback(
    Output("columns-modal", "is_open"),
    Input("select-columns-btn", "n_clicks"),
    Input("cancel-columns", "n_clicks"),
    Input("apply-columns", "n_clicks"),
    State("columns-modal", "is_open"),
    prevent_initial_call=True
)
def toggle_modal(n1, n2, n3, is_open):
    if n1 or n2 or n3:
        return not is_open
    return is_open

# Enable run comparison button when conditions are met
@callback(
    Output('run-comparison', 'disabled'),
    Input('join-columns1', 'value'),
    Input('join-columns2', 'value'),
    Input('all-columns-df1', 'value'),
    Input('all-columns-df2', 'value')
)
def enable_run_comparison(join1, join2, cols1, cols2):
    if not join1 or not join2 or len(join1) != len(join2):
        return True
    if not cols1 or not cols2:
        return True
    return False

# Run the comparison when button is clicked
@callback(
    Output('stored-compare', 'data'),
    Output('summary-cards', 'children'),
    Input('run-comparison', 'n_clicks'),
    State('stored-df1', 'data'),
    State('stored-df2', 'data'),
    State('join-columns1', 'value'),
    State('join-columns2', 'value'),
    State('all-columns-df1', 'value'),
    State('all-columns-df2', 'value'),
    prevent_initial_call=True
)
def run_comparison(n_clicks, json_df1, json_df2, join_cols1, join_cols2, compare_cols1, compare_cols2):
    if n_clicks is None:
        return dash.no_update, dash.no_update
    
    df1 = pd.read_json(json_df1, orient='split')
    df2 = pd.read_json(json_df2, orient='split')
    
    # Create join column mapping dictionary
    join_cols = dict(zip(join_cols1, join_cols2))
    
    # Run DataComPy comparison
    compare = datacompy.Compare(
        df1, 
        df2, 
        join_columns=join_cols,
        df1_name='Dataset1', 
        df2_name='Dataset2'
    )
    
    # Calculate metrics
    total_rows = compare.all_rows_cnt
    matches = compare.all_rows_cnt - (compare.df1_unq_rows + compare.df2_unq_rows)
    match_percent = (matches / total_rows) * 100 if total_rows > 0 else 0
    
    # Create summary cards
    cards = dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Total Rows"),
            dbc.CardBody([
                html.H4(f"{total_rows:,}", className="card-title")
            ])
        ]), md=3),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("Matching Rows"),
            dbc.CardBody([
                html.H4(f"{matches:,}", className="card-title"),
                html.P(f"({match_percent:.2f}%)")
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
    
    # Return comparison results and summary cards
    return compare.report(), cards

# Update results tabs with comparison data
@callback(
    Output('overview-results', 'children'),
    Output('row-analysis', 'children'),
    Output('column-analysis', 'children'),
    Output('mismatch-details', 'children'),
    Input('stored-compare', 'data'),
    prevent_initial_call=True
)
def update_results(report_json):
    if not report_json:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    report = json.loads(report_json)
    
    # Overview tab
    overview = html.Div([
        html.H4("Comparison Overview"),
        html.P(report.get('overview', '')),
        html.Hr(),
        html.H5("Key Statistics"),
        dbc.Table([
            html.Thead(html.Tr([html.Th("Metric"), html.Th("Count")])),
            html.Tbody([
                html.Tr([html.Td("Columns in DF1"), html.Td(report.get('columns_df1', []))]),
                html.Tr([html.Td("Columns in DF2"), html.Td(report.get('columns_df2', []))]),
                html.Tr([html.Td("Columns in Common"), html.Td(report.get('columns_in_both', []))])
            ])
        ], bordered=True)
    ])
    
    # Row analysis tab
    row_analysis = html.Div([
        html.H4("Row-Level Analysis"),
        dbc.Row([
            dbc.Col([
                html.H5("Rows Only in DF1"),
                html.P(str(report.get('rows_only_in_df1', []))),
                dbc.Table.from_dataframe(pd.DataFrame(report.get('df1_unq_rows', [])), striped=True)
            ]),
            dbc.Col([
                html.H5("Rows Only in DF2"),
                html.P(str(report.get('rows_only_in_df2', []))),
                dbc.Table.from_dataframe(pd.DataFrame(report.get('df2_unq_rows', [])), striped=True)
            ])
        ])
    ])
    
    # Column analysis tab
    column_analysis = html.Div([
        html.H4("Column-Level Analysis"),
        html.P(report.get('column_stats', '')),
        dbc.Table.from_dataframe(pd.DataFrame(report.get('column_comparison_stats', [])), striped=True)
    ])
    
    # Mismatch details tab
    mismatch_details = html.Div([
        html.H4("Detailed Mismatch Analysis"),
        dbc.Table.from_dataframe(pd.DataFrame(report.get('mismatch_rows', [])), striped=True)
    ])
    
    return overview, row_analysis, column_analysis, mismatch_details

# Data preview tabs
@callback(
    Output('df1-preview', 'children'),
    Input('stored-df1', 'data'),
    prevent_initial_call=True
)
def update_df1_preview(json_data):
    if json_data is None:
        return html.P("No data uploaded yet.")
    
    df = pd.read_json(json_data, orient='split')
    return dbc.Table.from_dataframe(df.head(), striped=True, bordered=True)

@callback(
    Output('df2-preview', 'children'),
    Input('stored-df2', 'data'),
    prevent_initial_call=True
)
def update_df2_preview(json_data):
    if json_data is None:
        return html.P("No data uploaded yet.")
    
    df = pd.read_json(json_data, orient='split')
    return dbc.Table.from_dataframe(df.head(), striped=True, bordered=True)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

