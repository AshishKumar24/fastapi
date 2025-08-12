import dash
from dash import dcc, html, dash_table
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np

# Initialize the Dash app
app = dash.Dash(__name__)

# Sample data for the charts
column_names = ['Col1', 'Col2', 'Col3', 'Col4', 'Col6', 'Col8', 'Col9']
mismatch_counts = [2, 5, 8, 3, 5, 4, 9]

# Generate sample similarity data
similarity_indices = np.linspace(0, 100, 50)
similarity_values = 5 + 2 * np.sin(similarity_indices * 0.1) + np.random.normal(0, 0.2, 50)

# Sample mismatches data
sample_mismatches = pd.DataFrame({
    'Column': ['Name', 'Email', 'Phone', 'Address'],
    'Base Value': ['John Smith', 'john@email.com', '555-1234', '123 Main St'],
    'Compare Value': ['J. Smith', 'john.smith@email.com', '(555) 1234', '123 Main Street'],
    'Mismatch Type': ['Format', 'Domain', 'Format', 'Abbreviation']
})

app.layout = html.Div([
    # Header
    html.H1("Dashboard", style={
        'fontSize': '48px',
        'fontWeight': 'bold',
        'color': '#2c3e50',
        'marginBottom': '30px',
        'fontFamily': 'Arial, sans-serif'
    }),
    
    # Top row of metrics
    html.Div([
        # Base Dataset Rows
        html.Div([
            html.H3("Base Dataset Rows", style={'fontSize': '16px', 'color': '#2c3e50', 'textAlign': 'center', 'marginBottom': '10px'}),
            html.H2("8,567", style={'fontSize': '36px', 'color': '#2c3e50', 'textAlign': 'center', 'margin': '0'})
        ], style={
            'backgroundColor': '#a8d5a8',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'margin': '5px',
            'flex': '1'
        }),
        
        # Compare Dataset Rows
        html.Div([
            html.H3("Compare Dataset Rows", style={'fontSize': '16px', 'color': '#2c3e50', 'textAlign': 'center', 'marginBottom': '10px'}),
            html.H2("9,234", style={'fontSize': '36px', 'color': '#2c3e50', 'textAlign': 'center', 'margin': '0'})
        ], style={
            'backgroundColor': '#a8d5a8',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'margin': '5px',
            'flex': '1'
        }),
        
        # Match Rate
        html.Div([
            html.H3("Match Rate", style={'fontSize': '16px', 'color': '#2c3e50', 'textAlign': 'center', 'marginBottom': '10px'}),
            html.H2("96.2%", style={'fontSize': '36px', 'color': '#2c3e50', 'textAlign': 'center', 'margin': '0'})
        ], style={
            'backgroundColor': '#a8d5a8',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'margin': '5px',
            'flex': '1'
        }),
        
        # Total Mismatches
        html.Div([
            html.H3("Total Mismatches", style={'fontSize': '16px', 'color': '#2c3e50', 'textAlign': 'center', 'marginBottom': '10px'}),
            html.H2("469", style={'fontSize': '36px', 'color': '#2c3e50', 'textAlign': 'center', 'margin': '0'})
        ], style={
            'backgroundColor': '#a8d5a8',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'margin': '5px',
            'flex': '1'
        })
    ], style={'display': 'flex', 'marginBottom': '20px'}),
    
    # Second row of metrics
    html.Div([
        # Rows Only in Base
        html.Div([
            html.H3("Rows Only in Base", style={'fontSize': '16px', 'color': '#2c3e50', 'textAlign': 'center', 'marginBottom': '10px'}),
            html.H2("234", style={'fontSize': '36px', 'color': '#2c3e50', 'textAlign': 'center', 'margin': '0'})
        ], style={
            'backgroundColor': '#f2a5a5',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'margin': '5px',
            'flex': '1'
        }),
        
        # Rows Only in Compare
        html.Div([
            html.H3("Rows Only in Compare", style={'fontSize': '16px', 'color': '#2c3e50', 'textAlign': 'center', 'marginBottom': '10px'}),
            html.H2("201", style={'fontSize': '36px', 'color': '#2c3e50', 'textAlign': 'center', 'margin': '0'})
        ], style={
            'backgroundColor': '#f2a5a5',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'margin': '5px',
            'flex': '1'
        }),
        
        # Common Rows
        html.Div([
            html.H3("Common Rows", style={'fontSize': '16px', 'color': '#2c3e50', 'textAlign': 'center', 'marginBottom': '10px'}),
            html.H2("11,642", style={'fontSize': '36px', 'color': '#2c3e50', 'textAlign': 'center', 'margin': '0'})
        ], style={
            'backgroundColor': '#a8d5a8',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'margin': '5px',
            'flex': '1'
        }),
        
        # Right side metrics
        html.Div([
            # Column Differences
            html.Div([
                html.H3("Column Differences", style={'fontSize': '14px', 'color': '#2c3e50', 'textAlign': 'center', 'marginBottom': '5px'}),
                html.H2("15", style={'fontSize': '28px', 'color': '#2c3e50', 'textAlign': 'center', 'margin': '0'})
            ], style={
                'backgroundColor': '#a8c8e8',
                'padding': '15px',
                'borderRadius': '10px',
                'textAlign': 'center',
                'margin': '5px',
                'marginBottom': '10px'
            }),
            
            # Data Type Mismatches
            html.Div([
                html.H3("Data Type Mismatches", style={'fontSize': '14px', 'color': '#2c3e50', 'textAlign': 'center', 'marginBottom': '5px'}),
                html.H2("3", style={'fontSize': '28px', 'color': '#2c3e50', 'textAlign': 'center', 'margin': '0'})
            ], style={
                'backgroundColor': '#a8c8e8',
                'padding': '15px',
                'borderRadius': '10px',
                'textAlign': 'center',
                'margin': '5px'
            })
        ], style={'flex': '1', 'display': 'flex', 'flexDirection': 'column'})
    ], style={'display': 'flex', 'marginBottom': '20px'}),
    
    # Charts and additional content
    html.Div([
        # Left side charts
        html.Div([
            # Mismatches by Column chart
            html.Div([
                html.H3("Mismatches by Column", style={'fontSize': '16px', 'color': '#2c3e50', 'marginBottom': '10px'}),
                dcc.Graph(
                    figure={
                        'data': [
                            go.Bar(
                                x=column_names,
                                y=mismatch_counts,
                                marker_color='#5b9bd5'
                            )
                        ],
                        'layout': go.Layout(
                            xaxis={'title': ''},
                            yaxis={'title': 'Count', 'range': [0, 10]},
                            margin={'l': 40, 'r': 20, 't': 20, 'b': 40},
                            height=200,
                            plot_bgcolor='white',
                            paper_bgcolor='white'
                        )
                    },
                    config={'displayModeBar': False}
                )
            ], style={
                'backgroundColor': 'white',
                'padding': '15px',
                'borderRadius': '10px',
                'marginBottom': '10px',
                'border': '1px solid #ddd'
            }),
            
            # Row-Level Similarity chart
            html.Div([
                html.H3("Row-Level Similarity", style={'fontSize': '16px', 'color': '#2c3e50', 'marginBottom': '10px'}),
                dcc.Graph(
                    figure={
                        'data': [
                            go.Scatter(
                                x=similarity_indices,
                                y=similarity_values,
                                mode='lines',
                                line=dict(color='#5b9bd5', width=2)
                            )
                        ],
                        'layout': go.Layout(
                            xaxis={'title': 'Index'},
                            yaxis={'title': 'Similarity'},
                            margin={'l': 40, 'r': 20, 't': 20, 'b': 40},
                            height=200,
                            plot_bgcolor='white',
                            paper_bgcolor='white'
                        )
                    },
                    config={'displayModeBar': False}
                )
            ], style={
                'backgroundColor': 'white',
                'padding': '15px',
                'borderRadius': '10px',
                'border': '1px solid #ddd'
            })
        ], style={'flex': '2', 'marginRight': '20px'}),
        
        # Right side content
        html.Div([
            # Pie Chart
            html.Div([
                dcc.Graph(
                    figure={
                        'data': [
                            go.Pie(
                                values=[96.2, 3.8],
                                labels=['Match', 'Mismatch'],
                                marker_colors=['#5b9bd5', '#d9d9d9'],
                                hole=0.3
                            )
                        ],
                        'layout': go.Layout(
                            margin={'l': 20, 'r': 20, 't': 20, 'b': 20},
                            height=200,
                            showlegend=False,
                            plot_bgcolor='white',
                            paper_bgcolor='white'
                        )
                    },
                    config={'displayModeBar': False}
                ),
                html.H3("% Match vs Mismatch", style={'fontSize': '14px', 'color': '#2c3e50', 'textAlign': 'center', 'marginTop': '10px'})
            ], style={
                'backgroundColor': 'white',
                'padding': '15px',
                'borderRadius': '10px',
                'marginBottom': '20px',
                'border': '1px solid #ddd'
            })
        ], style={'flex': '1'})
    ], style={'display': 'flex', 'marginBottom': '20px'}),
    
    # Bottom tabs section
    html.Div([
        dcc.Tabs(id="tabs", value='column-stats', children=[
            dcc.Tab(label='Column-Level Stats', value='column-stats'),
            dcc.Tab(label='Sample Mismatches', value='sample-mismatches'),
            dcc.Tab(label='Schema', value='schema')
        ]),
        html.Div(id='tab-content')
    ])
], style={
    'padding': '30px',
    'backgroundColor': '#f5f5f0',
    'minHeight': '100vh',
    'fontFamily': 'Arial, sans-serif'
})

# Callback for tab content
@app.callback(
    dash.dependencies.Output('tab-content', 'children'),
    [dash.dependencies.Input('tabs', 'value')]
)
def update_tab_content(selected_tab):
    if selected_tab == 'column-stats':
        return html.Div([
            html.Div([
                html.Div([
                    html.H4("Mean:", style={'margin': '10px 0'}),
                    html.H4("Nulls:", style={'margin': '10px 0'})
                ], style={'flex': '1'}),
                html.Div([
                    html.H4("Std:", style={'margin': '10px 0'}),
                ], style={'flex': '1'})
            ], style={'display': 'flex', 'padding': '20px'})
        ])
    elif selected_tab == 'sample-mismatches':
        return html.Div([
            dash_table.DataTable(
                data=sample_mismatches.to_dict('records'),
                columns=[{"name": i, "id": i} for i in sample_mismatches.columns],
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={'backgroundColor': '#f0f0f0', 'fontWeight': 'bold'}
            )
        ], style={'padding': '20px'})
    else:  # schema tab
        return html.Div([
            html.P("Schema information would be displayed here.", style={'padding': '20px'})
        ])

if __name__ == '__main__':
    app.run_server(debug=True)
