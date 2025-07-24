import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import re

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

original_items = [f"Item {i+1}" for i in range(24)]

gradient_style = {
    "background": "linear-gradient(135deg, #3f51b5, #2196f3)",
    "color": "white",
    "padding": "10px",
    "borderRadius": "6px",
    "boxShadow": "0 2px 6px rgba(0,0,0,0.2)",
    "marginTop": "10px"
}

# Utility: fuzzy or regex filter


def fuzzy_filter(items, query, use_regex=False):
    if not query:
        return items
    if use_regex:
        try:
            pattern = re.compile(query, re.IGNORECASE)
            return [i for i in items if pattern.search(i)]
        except re.error:
            return []
    return [i for i in items if query.lower() in i.lower()]

# Utility: chunk into columns


def chunk_list(lst, n):
    chunk_size = len(lst) // n + (len(lst) % n > 0)
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


app.layout = dbc.Container([
    dbc.Button("Open Modal", id="open-modal", n_clicks=0),

    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Select Items")),

        dbc.ModalBody([
            dbc.Row([
                dbc.Col(dbc.Checkbox(label="Select All", id="select-all")),
                dbc.Col(dbc.Checkbox(label="Sort Items", id="sort-items")),
                dbc.Col(dbc.Checkbox(label="Regex Mode", id="regex-mode")),
                dbc.Col(dcc.Input(id="search-bar", type="text",
                        placeholder="Search...", debounce=True)),
            ], className="mb-3"),

            html.Div(id="checklist-output"),

            html.Div(id="selected-tags", style=gradient_style)
        ]),

        dbc.ModalFooter(
            dbc.Button("Close", id="close-modal",
                       className="ms-auto", n_clicks=0)
        ),
    ], id="item-modal", is_open=False, size="lg"),
], className="p-4")


# Toggle modal visibility
@app.callback(
    Output("item-modal", "is_open"),
    [Input("open-modal", "n_clicks"), Input("close-modal", "n_clicks")],
    State("item-modal", "is_open")
)
def toggle_modal(open_clicks, close_clicks, is_open):
    return not is_open if (open_clicks or close_clicks) else is_open


# Update checklist display + selected tags
@app.callback(
    Output("checklist-output", "children"),
    Output("selected-tags", "children"),
    Input("search-bar", "value"),
    Input("sort-items", "value"),
    Input("regex-mode", "value"),
    Input("select-all", "value"),
)
def display_checklists(search_value, sort_items, regex_mode, select_all):
    # Filter & sort
    filtered = fuzzy_filter(original_items, search_value, bool(regex_mode))
    if sort_items:
        filtered.sort()

    # Select all logic
    selected = filtered if select_all else []

    # Chunk columns
    columns = chunk_list(filtered, 3)

    checklist_rows = dbc.Row([
        dbc.Col(
            dcc.Checklist(
                options=[{"label": item, "value": item} for item in col],
                value=[i for i in col if i in selected],
                inputStyle={"margin-right": "6px"},
                labelStyle={"display": "block", "margin-bottom": "4px"},
                className="checklist-chunk"
            ), width=4
        ) for col in columns
    ])

    # Tag display
    badges = [dbc.Badge(i, color="light", className="me-1 badge-selected")
              for i in selected]

    return checklist_rows, badges


if __name__ == "__main__":
    app.run(debug=True)
