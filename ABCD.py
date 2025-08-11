import dash
from dash import dcc, html, Input, Output, State, ctx, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import duckdb
import tempfile
import os
import base64
import io
import atexit

# 🦆 DuckDB session setup
duckdb_file = tempfile.NamedTemporaryFile(suffix=".duckdb", delete=False)
duckdb_path = duckdb_file.name
duckdb_file.close()
conn = duckdb.connect(duckdb_path)

def cleanup_duckdb():
    try:
        conn.close()
        os.remove(duckdb_path)
        print(f"Deleted DuckDB session file: {duckdb_path}")
    except Exception as e:
        print(f"Cleanup error: {e}")
atexit.register(cleanup_duckdb)

comparison_results = {}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "DuckDB Comparison Dashboard"

app.layout = html.Div([
    dcc.Store(id="sidebar-visible", data=True),

    dbc.Row([
        dbc.Col(
            id="sidebar-container",
            children=[
                html.H4("Data Input", className="mt-2"),
                dcc.Upload(id="upload-base", children=dbc.Button("Upload Base CSV"), multiple=False),
                dcc.Upload(id="upload-compare", children=dbc.Button("Upload Compare CSV"), multiple=False),
                dbc.Textarea(id="sql-base", placeholder="Base SQL query", className="mt-2"),
                dbc.Textarea(id="sql-compare", placeholder="Compare SQL query", className="mt-2"),
                dbc.Button("Run SQL", id="btn-run-sql", color="primary", className="mt-2"),
                html.Div(id="status", className="mt-2"),
                dbc.Button("Select Columns", id="btn-open-modal", color="secondary", className="mt-3"),
            ],
            width=2,
            style={"backgroundColor": "#fff7ed", "borderRight": "1px solid #ddd", "padding": "1rem"}
        ),

        dbc.Col([
            dbc.Button("☰ Toggle Sidebar", id="toggle-button", color="warning", className="mb-2"),
            html.H2("Dashboard", className="text-white p-2", style={
                "background": "linear-gradient(to right, #f97316, #f43f5e)",
                "borderRadius": "6px"
            }),
            dbc.Tabs([
                dbc.Tab(label="Overview", tab_id="overview"),
                dbc.Tab(label="Row Analysis", tab_id="row"),
                dbc.Tab(label="Column Analysis", tab_id="column"),
                dbc.Tab(label="Mismatch Details", tab_id="mismatch"),
                dbc.Tab(label="Unique Rows", tab_id="unique"),
            ], id="tabs", active_tab="overview"),
            html.Div(id="tab-content", className="p-4")
        ], style={"flexGrow": 1})
    ]),

    dbc.Modal([
        dbc.ModalHeader("Select Join and Compare Columns"),
        dbc.ModalBody([
            html.Label("Join Columns"),
            dcc.Dropdown(id="join-cols", multi=True),
            html.Br(),
            html.Label("Compare Columns"),
            dcc.Dropdown(id="compare-cols", multi=True),
            html.Br(),
            dbc.Checklist(
                options=[
                    {"label": "Ignore Case", "value": "ignore_case"},
                    {"label": "Ignore Spaces", "value": "ignore_spaces"},
                ],
                value=["ignore_spaces"],
                id="compare-options",
                inline=True
            ),
        ]),
        dbc.ModalFooter([
            dbc.Button("Run Comparison", id="run-compare", color="primary"),
            dbc.Button("Close", id="close-modal", color="secondary")
        ])
    ], id="modal", is_open=False)
])

# 📦 CSV parser
def parse_csv(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return pd.read_csv(io.StringIO(decoded.decode('utf-8')))

# 📥 Upload or SQL → DuckDB
@app.callback(
    Output("status", "children"),
    Input("upload-base", "contents"),
    Input("upload-compare", "contents"),
    Input("btn-run-sql", "n_clicks"),
    State("sql-base", "value"),
    State("sql-compare", "value"),
)
def load_data(base_csv, compare_csv, n_sql, sql_base, sql_compare):
    try:
        if base_csv:
            df_base = parse_csv(base_csv)
            conn.execute("DROP TABLE IF EXISTS base")
            conn.register("base", df_base)
        if compare_csv:
            df_compare = parse_csv(compare_csv)
            conn.execute("DROP TABLE IF EXISTS compare")
            conn.register("compare", df_compare)
        if ctx.triggered_id == "btn-run-sql" and sql_base and sql_compare:
            conn.execute("DROP TABLE IF EXISTS base")
            conn.execute("DROP TABLE IF EXISTS compare")
            conn.execute(f"CREATE TABLE base AS {sql_base}")
            conn.execute(f"CREATE TABLE compare AS {sql_compare}")
        return "Data loaded into DuckDB."
    except Exception as e:
        return f"Error: {e}"

# 📤 Modal open + populate
@app.callback(
    Output("modal", "is_open"),
    Output("join-cols", "options"),
    Output("compare-cols", "options"),
    Input("btn-open-modal", "n_clicks"),
    Input("close-modal", "n_clicks"),
    State("modal", "is_open")
)
def toggle_modal(n_open, n_close, is_open):
    if ctx.triggered_id == "btn-open-modal":
        cols = conn.execute("SELECT * FROM base LIMIT 1").fetchdf().columns
        options = [{"label": c, "value": c} for c in cols]
        return True, options, options
    elif ctx.triggered_id == "close-modal":
        return False, [], []
    return is_open, [], []

# ☰ Sidebar toggle
@app.callback(
    Output("sidebar-visible", "data"),
    Input("toggle-button", "n_clicks"),
    State("sidebar-visible", "data"),
    prevent_initial_call=True
)
def toggle_sidebar(n_clicks, visible):
    return not visible

@app.callback(
    Output("sidebar-container", "style"),
    Input("sidebar-visible", "data")
)
def update_sidebar_visibility(visible):
    if visible:
        return {"backgroundColor": "#fff7ed", "borderRight": "1px solid #ddd", "padding": "1rem"}
    else:
        return {"display": "none"}

# 🧮 Run comparison
@app.callback(
    Output("tab-content", "children"),
    Input("run-compare", "n_clicks"),
    State("join-cols", "value"),
    State("compare-cols", "value"),
    State("compare-options", "value"),
    State("tabs", "active_tab")
)
def run_comparison(n, join_cols, compare_cols, options, tab):
    if not n or not join_cols or not compare_cols:
        return "Please select join and compare columns."

    ignore_case = "ignore_case" in options
    ignore_spaces = "ignore_spaces" in options

    def normalize(col):
        expr = f"TRIM({col})" if ignore_spaces else col
        expr = f"LOWER({expr})" if ignore_case else expr
        return expr

    join_cond = " AND ".join([
        f"{normalize('base.' + c)} = {normalize('compare.' + c)}" for c in join_cols
    ])

    query = f"""
        SELECT base.*, compare.*, 
        {', '.join([f"(base.{c} = compare.{c}) AS match_{c}" for c in compare_cols])}
        FROM base
        LEFT JOIN compare ON {join_cond}
    """
    df = conn.execute(query).fetchdf()

    total_rows = len(df)
    match_counts = {c: df[f"match_{c}"].sum() for c in compare_cols}
    match_rate = sum(match_counts.values()) / (total_rows * len(compare_cols)) if total_rows else 0

    mismatch_rows = []
    for col in compare_cols:
        mismatches = df[df[f"match_{col}"] == False]
        for _, row in mismatches.iterrows():
            mismatch_rows.append({
                "column": col,
                "base_value": row[col],
                "compare_value": row.get(f"{col}_compare", None),
                                **{c: row[c] for c in join_cols}
            })

    base_keys = conn.execute(f"SELECT DISTINCT {', '.join(join_cols)} FROM base").fetchdf()
    compare_keys = conn.execute(f"SELECT DISTINCT {', '.join(join_cols)} FROM compare").fetchdf()

    base_only = pd.merge(base_keys, compare_keys, on=join_cols, how='left', indicator=True)
    base_only = base_only[base_only['_merge'] == 'left_only'].drop(columns=['_merge'])

    compare_only = pd.merge(compare_keys, base_keys, on=join_cols, how='left', indicator=True)
    compare_only = compare_only[compare_only['_merge'] == 'left_only'].drop(columns=['_merge'])

    comparison_results["metrics"] = {
        "total_rows": total_rows,
        "match_rate": match_rate,
        "column_match_counts": match_counts
    }
    comparison_results["mismatch_details"] = pd.DataFrame(mismatch_rows)
    comparison_results["unique_base"] = base_only
    comparison_results["unique_compare"] = compare_only

    return render_tab(tab)

@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab")
)
def render_tab(tab):
    metrics = comparison_results.get("metrics", {})
    if tab == "overview":
        return dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Total Rows"),
                dbc.CardBody(html.H5(f"{metrics.get('total_rows', '-'):,}", className="card-title"))
            ], style={"background": "linear-gradient(to right, #f97316, #f43f5e)", "color": "white"})),
            dbc.Col(dbc.Card([
                dbc.CardHeader("Match Rate"),
                dbc.CardBody(html.H5(f"{metrics.get('match_rate', 0):.2%}", className="card-title"))
            ], style={"background": "linear-gradient(to right, #f97316, #f43f5e)", "color": "white"})),
        ])
    elif tab == "row":
        base_only = comparison_results.get("unique_base", pd.DataFrame())
        compare_only = comparison_results.get("unique_compare", pd.DataFrame())
        return html.Div([
            html.H5("Rows only in base"),
            dash_table.DataTable(
                columns=[{"name": c, "id": c} for c in base_only.columns],
                data=base_only.to_dict("records"),
                page_size=5
            ),
            html.H5("Rows only in compare", className="mt-4"),
            dash_table.DataTable(
                columns=[{"name": c, "id": c} for c in compare_only.columns],
                data=compare_only.to_dict("records"),
                page_size=5
            )
        ])
    elif tab == "column":
        rows = []
        for col, count in metrics.get("column_match_counts", {}).items():
            rows.append(html.Tr([html.Td(col), html.Td(f"{count:,}")]))
        return dbc.Table([
            html.Thead(html.Tr([html.Th("Column"), html.Th("Matches")])),
            html.Tbody(rows)
        ])
    elif tab == "mismatch":
        df_mismatch = comparison_results.get("mismatch_details", pd.DataFrame())
        if df_mismatch.empty:
            return "No mismatches found."
        return dash_table.DataTable(
            columns=[{"name": c, "id": c} for c in df_mismatch.columns],
            data=df_mismatch.to_dict("records"),
            page_size=10,
            style_table={"overflowX": "auto"},
            filter_action="native",
            sort_action="native"
        )
    elif tab == "unique":
        base_df = comparison_results.get("unique_base", pd.DataFrame())
        compare_df = comparison_results.get("unique_compare", pd.DataFrame())
        return html.Div([
            html.H5("Rows only in base"),
            dash_table.DataTable(
                columns=[{"name": c, "id": c} for c in base_df.columns],
                data=base_df.to_dict("records"),
                page_size=5
            ),
            html.H5("Rows only in compare", className="mt-4"),
            dash_table.DataTable(
                columns=[{"name": c, "id": c} for c in compare_df.columns],
                data=compare_df.to_dict("records"),
                page_size=5
            )
        ])
    return "Select a tab to view analysis."

# 🏁 Run app
if __name__ == "__main__":
    app.run_server(debug=True)
