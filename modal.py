import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import re

import random
import string


def generate_random_gibberish(length=6):
    return ''.join(random.choices(string.ascii_lowercase, k=length))


# Initialize app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# ✅ Embed CSS in custom layout
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Smart Modal App</title>
        {%favicon%}
        {%css%}
        <style>
            .checklist-chunk label:hover {
                background-color: #e3f2fd;
                transition: background-color 0.3s ease;
                border-radius: 4px;
            }
            .badge-selected {
                font-size: 0.8rem;
                animation: pulse 0.4s;
                margin-bottom: 6px;
                margin-right: 6px;
            }
            @keyframes pulse {
                0% { opacity: 0.6; transform: scale(1); }
                50% { opacity: 1; transform: scale(1.05); }
                100% { opacity: 0.6; transform: scale(1); }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Sample data
original_items = column_names = [
    "User_ID", "Timestamp", "Country", "Region", "City",
    "Device_Type", "OS_Version", "Browser", "IP_Address", "Session_Duration",
    "Page_Views", "Bounce_Rate", "Conversion_Flag", "Referral_Source", "Campaign_ID",
    "Product_Code", "Product_Category", "Price_USD", "Discount_Percent", "Final_Price",
    "Inventory_Count", "Restock_Date", "Supplier_Name", "Review_Score", "Review_Count",
    "Search_Term", "Click_Through_Rate", "Ad_Impressions", "Ad_Clicks", "Revenue_USD",
    "Profit_Margin", "Customer_Segment", "Subscription_Type", "Renewal_Status", "Churn_Flag",
    "Temperature_C", "Humidity_Level", "Sensor_Reading", "Alert_Status", "Last_Updated",
    "Experiment_ID", "Trial_Phase", "Gene_Symbol", "Mutation_Flag", "Expression_Level",
    "Color_Code", "Theme_Label", "UI_Version", "Module_Name", "Is_Active"
]
# [f"Item {i}" for i in generate_random_gibberish()]


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


def chunk_list(lst, n):
    chunk_size = len(lst) // n + (len(lst) % n > 0)
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


gradient_style = {
    "background": "linear-gradient(135deg, #3f51b5, #2196f3)",
    "color": "white",
    "padding": "10px",
    "borderRadius": "6px",
    "boxShadow": "0 2px 6px rgba(0,0,0,0.2)",
    "marginTop": "10px"
}

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
        )
    ], id="item-modal", is_open=False, size="lg")
], className="p-4")


@app.callback(
    Output("item-modal", "is_open"),
    [Input("open-modal", "n_clicks"), Input("close-modal", "n_clicks")],
    State("item-modal", "is_open")
)
def toggle_modal(open_clicks, close_clicks, is_open):
    return not is_open if (open_clicks or close_clicks) else is_open


@app.callback(
    Output("checklist-output", "children"),
    Output("selected-tags", "children"),
    Input("search-bar", "value"),
    Input("sort-items", "value"),
    Input("regex-mode", "value"),
    Input("select-all", "value"),
)
def update_checklist(search_value, sort_items, regex_mode, select_all):
    filtered = fuzzy_filter(original_items, search_value, bool(regex_mode))
    if sort_items:
        filtered.sort()
    selected_items = filtered if select_all else []

    columns = chunk_list(filtered, 3)
    checklist_layout = dbc.Row([
        dbc.Col(
            dcc.Checklist(
                options=[{"label": item, "value": item} for item in col],
                value=[item for item in col if item in selected_items],
                inputStyle={"margin-right": "6px"},
                labelStyle={"display": "block", "margin-bottom": "4px"},
                className="checklist-chunk"
            ), width=4
        ) for col in columns
    ])

    tags = [dbc.Badge(item, color="light", className="badge-selected")
            for item in selected_items]
    return checklist_layout, tags


if __name__ == "__main__":
    app.run(debug=True)
