import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Initialize the Dash app
app = dash.Dash(__name__)

# Sample DataComPy-like results data
def generate_sample_data():
    """Generate sample data that mimics DataComPy comparison results"""
    
    # Overall comparison metrics
    comparison_summary = {
        'total_rows_base': 1000,
        'total_rows_compare': 1020,
        'total_columns_base': 8,
        'total_columns_compare': 8,
        'rows_only_base': 15,
        'rows_only_compare': 35,
        'rows_both': 985,
        'columns_only_base': 0,
        'columns_only_compare': 0,
        'columns_both': 8,
        'matches': 850,
        'mismatches': 135,
        'match_rate': 0.863
    }
    
    # Column-level comparison details
    column_details = pd.DataFrame({
        'column_name': ['id', 'name', 'age', 'salary', 'department', 'hire_date', 'active', 'score'],
        'matches': [985, 920, 875, 800, 940, 890, 960, 820],
        'mismatches': [0, 65, 110, 185, 45, 95, 25, 165],
        'match_rate': [1.0, 0.934, 0.888, 0.812, 0.954, 0.904, 0.975, 0.833],
        'data_type_base': ['int64', 'object', 'int64', 'float64', 'object', 'datetime64', 'bool', 'float64'],
        'data_type_compare': ['int64', 'object', 'int64', 'float64', 'object', 'datetime64', 'bool', 'float64'],
        'null_count_base': [0, 5, 2, 10, 1, 0, 0, 8],
        'null_count_compare': [0, 8, 3, 12, 2, 1, 0, 10]
    })
    
    # Sample mismatched records
    mismatched_records = pd.DataFrame({
        'row_id': [23, 45, 67, 89, 156, 234, 345, 456, 567, 678],
        'column': ['salary', 'age', 'name', 'score', 'department', 'hire_date', 'salary', 'age', 'active', 'score'],
        'base_value': [50000, 28, 'John Smith', 85.5, 'Engineering', '2020-01-15', 75000, 35, True, 92.3],
        'compare_value': [52000, 29, 'Jon Smith', 87.2, 'Engineering', '2020-01-16', 77000, 36, False, 94.1],
        'difference': [2000, 1, 'Typo', 1.7, 'Same', '1 day', 2000, 1, 'Changed', 1.8]
    })
    
    return comparison_summary, column_details, mismatched_records

# Generate sample data
summary, column_details, mismatched_records = generate_sample_data()

# Helper functions for quality assessment
def get_quality_grade(match_rate):
    """Get quality grade based on match rate"""
    if match_rate >= 0.95:
        return "A"
    elif match_rate >= 0.90:
        return "B"
    elif match_rate >= 0.80:
        return "C"
    elif match_rate >= 0.70:
        return "D"
    else:
        return "F"

def get_quality_color(match_rate):
    """Get color based on quality grade"""
    if match_rate >= 0.95:
        return "#27ae60"
    elif match_rate >= 0.90:
        return "#f39c12"
    elif match_rate >= 0.80:
        return "#e67e22"
    elif match_rate >= 0.70:
        return "#e74c3c"
    else:
        return "#c0392b"

# Define the app layout
app.layout = html.Div([
    html.Div([
        html.H1("DataComPy Results Dashboard", 
                style={'textAlign': 'center', 'marginBottom': 30, 'color': '#2c3e50'}),
        
        # Summary Cards (always visible)
        html.Div([
            # First row of cards
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-database", style={'fontSize': '2em', 'color': '#3498db', 'marginBottom': '10px'}),
                        html.H3(f"{summary['total_rows_base']:,}", style={'margin': 0, 'color': '#3498db'}),
                        html.P("Base Dataset Rows", style={'margin': 0, 'fontSize': '0.9em', 'color': '#666'})
                    ])
                ], className='summary-card'),
                
                html.Div([
                    html.Div([
                        html.I(className="fas fa-database", style={'fontSize': '2em', 'color': '#e74c3c', 'marginBottom': '10px'}),
                        html.H3(f"{summary['total_rows_compare']:,}", style={'margin': 0, 'color': '#e74c3c'}),
                        html.P("Compare Dataset Rows", style={'margin': 0, 'fontSize': '0.9em', 'color': '#666'})
                    ])
                ], className='summary-card'),
                
                html.Div([
                    html.Div([
                        html.I(className="fas fa-check-circle", style={'fontSize': '2em', 'color': '#27ae60', 'marginBottom': '10px'}),
                        html.H3(f"{summary['match_rate']:.1%}", style={'margin': 0, 'color': '#27ae60'}),
                        html.P("Overall Match Rate", style={'margin': 0, 'fontSize': '0.9em', 'color': '#666'})
                    ])
                ], className='summary-card'),
                
                html.Div([
                    html.Div([
                        html.I(className="fas fa-exclamation-triangle", style={'fontSize': '2em', 'color': '#f39c12', 'marginBottom': '10px'}),
                        html.H3(f"{summary['mismatches']:,}", style={'margin': 0, 'color': '#f39c12'}),
                        html.P("Total Mismatches", style={'margin': 0, 'fontSize': '0.9em', 'color': '#666'})
                    ])
                ], className='summary-card')
            ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': 15}),
            
            # Second row of cards
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-plus", style={'fontSize': '1.5em', 'color': '#e74c3c', 'marginBottom': '8px'}),
                        html.H4(f"{summary['rows_only_base']:,}", style={'margin': 0, 'color': '#e74c3c'}),
                        html.P("Rows Only in Base", style={'margin': 0, 'fontSize': '0.8em', 'color': '#666'})
                    ])
                ], className='summary-card-small'),
                
                html.Div([
                    html.Div([
                        html.I(className="fas fa-minus", style={'fontSize': '1.5em', 'color': '#f39c12', 'marginBottom': '8px'}),
                        html.H4(f"{summary['rows_only_compare']:,}", style={'margin': 0, 'color': '#f39c12'}),
                        html.P("Rows Only in Compare", style={'margin': 0, 'fontSize': '0.8em', 'color': '#666'})
                    ])
                ], className='summary-card-small'),
                
                html.Div([
                    html.Div([
                        html.I(className="fas fa-equals", style={'fontSize': '1.5em', 'color': '#27ae60', 'marginBottom': '8px'}),
                        html.H4(f"{summary['rows_both']:,}", style={'margin': 0, 'color': '#27ae60'}),
                        html.P("Common Rows", style={'margin': 0, 'fontSize': '0.8em', 'color': '#666'})
                    ])
                ], className='summary-card-small'),
                
                html.Div([
                    html.Div([
                        html.I(className="fas fa-columns", style={'fontSize': '1.5em', 'color': '#9b59b6', 'marginBottom': '8px'}),
                        html.H4(f"{summary['columns_both']}", style={'margin': 0, 'color': '#9b59b6'}),
                        html.P("Columns Compared", style={'margin': 0, 'fontSize': '0.8em', 'color': '#666'})
                    ])
                ], className='summary-card-small'),
                
                html.Div([
                    html.Div([
                        html.I(className="fas fa-chart-line", style={'fontSize': '1.5em', 'color': '#16a085', 'marginBottom': '8px'}),
                        html.H4(f"{column_details['match_rate'].mean():.1%}", style={'margin': 0, 'color': '#16a085'}),
                        html.P("Avg Column Match Rate", style={'margin': 0, 'fontSize': '0.8em', 'color': '#666'})
                    ])
                ], className='summary-card-small'),
                
                html.Div([
                    html.Div([
                        html.I(className="fas fa-times-circle", style={'fontSize': '1.5em', 'color': '#e74c3c', 'marginBottom': '8px'}),
                        html.H4(f"{len(column_details[column_details['match_rate'] < 0.9])}", style={'margin': 0, 'color': '#e74c3c'}),
                        html.P("Columns < 90% Match", style={'margin': 0, 'fontSize': '0.8em', 'color': '#666'})
                    ])
                ], className='summary-card-small')
            ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': 15}),
            
            # Third row - Quality indicators
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-shield-alt", style={'fontSize': '1.5em', 'color': '#2c3e50', 'marginBottom': '8px'}),
                        html.H4(get_quality_grade(summary['match_rate']), style={'margin': 0, 'color': get_quality_color(summary['match_rate'])}),
                        html.P("Data Quality Grade", style={'margin': 0, 'fontSize': '0.8em', 'color': '#666'})
                    ])
                ], className='summary-card-small'),
                
                html.Div([
                    html.Div([
                        html.I(className="fas fa-balance-scale", style={'fontSize': '1.5em', 'color': '#8e44ad', 'marginBottom': '8px'}),
                        html.H4(f"{abs(summary['total_rows_compare'] - summary['total_rows_base'])/summary['total_rows_base']:.1%}", 
                               style={'margin': 0, 'color': '#8e44ad'}),
                        html.P("Row Count Difference", style={'margin': 0, 'fontSize': '0.8em', 'color': '#666'})
                    ])
                ], className='summary-card-small'),
                
                html.Div([
                    html.Div([
                        html.I(className="fas fa-search", style={'fontSize': '1.5em', 'color': '#d35400', 'marginBottom': '8px'}),
                        html.H4(f"{column_details['null_count_base'].sum() + column_details['null_count_compare'].sum()}", 
                               style={'margin': 0, 'color': '#d35400'}),
                        html.P("Total Null Values", style={'margin': 0, 'fontSize': '0.8em', 'color': '#666'})
                    ])
                ], className='summary-card-small'),
                
                html.Div([
                    html.Div([
                        html.I(className="fas fa-code", style={'fontSize': '1.5em', 'color': '#2980b9', 'marginBottom': '8px'}),
                        html.H4(f"{sum(column_details['data_type_base'] != column_details['data_type_compare'])}", 
                               style={'margin': 0, 'color': '#2980b9'}),
                        html.P("Type Mismatches", style={'margin': 0, 'fontSize': '0.8em', 'color': '#666'})
                    ])
                ], className='summary-card-small'),
                
                html.Div([
                    html.Div([
                        html.I(className="fas fa-clock", style={'fontSize': '1.5em', 'color': '#7f8c8d', 'marginBottom': '8px'}),
                        html.H4(datetime.now().strftime("%H:%M"), style={'margin': 0, 'color': '#7f8c8d'}),
                        html.P("Last Updated", style={'margin': 0, 'fontSize': '0.8em', 'color': '#666'})
                    ])
                ], className='summary-card-small')
            ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': 30})
        ]),
        
        # Tabs
        dcc.Tabs(id='main-tabs', value='overview-tab', children=[
            dcc.Tab(label='Overview', value='overview-tab'),
            dcc.Tab(label='Row Analysis', value='row-analysis-tab'),
            dcc.Tab(label='Column Analysis', value='column-analysis-tab'),
            dcc.Tab(label='Mismatch Details', value='mismatch-details-tab'),
            dcc.Tab(label='Data Quality', value='data-quality-tab')
        ], style={'marginBottom': 20}),
        
        # Tab content
        html.Div(id='tab-content')
        
    ], style={'padding': '20px', 'maxWidth': '1200px', 'margin': '0 auto'})
])

# Main callback for tab content
@app.callback(
    Output('tab-content', 'children'),
    [Input('main-tabs', 'value')]
)
def render_tab_content(active_tab):
    """Render content based on active tab"""
    
    if active_tab == 'overview-tab':
        return html.Div([
            html.H3("Comparison Overview", style={'marginBottom': 20}),
            
            # Key metrics cards
            html.Div([
                html.Div([
                    html.H4("Data Completeness", style={'color': '#2c3e50', 'marginBottom': 15}),
                    html.P(f"Base dataset: {summary['total_rows_base']:,} rows × {summary['total_columns_base']} columns"),
                    html.P(f"Compare dataset: {summary['total_rows_compare']:,} rows × {summary['total_columns_compare']} columns"),
                    html.P(f"Common rows: {summary['rows_both']:,} ({summary['rows_both']/summary['total_rows_base']:.1%})")
                ], style={'flex': 1, 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px', 'margin': '0 10px'}),
                
                html.Div([
                    html.H4("Match Statistics", style={'color': '#2c3e50', 'marginBottom': 15}),
                    html.P(f"Total comparisons: {summary['matches'] + summary['mismatches']:,}"),
                    html.P(f"Matches: {summary['matches']:,} ({summary['match_rate']:.1%})"),
                    html.P(f"Mismatches: {summary['mismatches']:,} ({1-summary['match_rate']:.1%})")
                ], style={'flex': 1, 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px', 'margin': '0 10px'}),
                
                html.Div([
                    html.H4("Data Quality Score", style={'color': '#2c3e50', 'marginBottom': 15}),
                    html.Div([
                        html.H2(f"{summary['match_rate']:.1%}", style={'color': '#27ae60' if summary['match_rate'] > 0.9 else '#e74c3c', 'margin': 0}),
                        html.P("Overall Quality", style={'margin': 0})
                    ], style={'textAlign': 'center'})
                ], style={'flex': 1, 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px', 'margin': '0 10px'})
            ], style={'display': 'flex', 'marginBottom': 30}),
            
            # Quick insights
            html.Div([
                html.H4("Quick Insights", style={'marginBottom': 15}),
                html.Ul([
                    html.Li(f"Row difference: {abs(summary['total_rows_compare'] - summary['total_rows_base']):,} rows"),
                    html.Li(f"Most problematic column: {column_details.loc[column_details['match_rate'].idxmin(), 'column_name']} ({column_details['match_rate'].min():.1%} match rate)"),
                    html.Li(f"Best performing column: {column_details.loc[column_details['match_rate'].idxmax(), 'column_name']} ({column_details['match_rate'].max():.1%} match rate)"),
                    html.Li(f"Columns with type mismatches: {sum(column_details['data_type_base'] != column_details['data_type_compare'])}")
                ])
            ], style={'backgroundColor': '#e8f4f8', 'padding': '20px', 'borderRadius': '8px'})
        ])
    
    elif active_tab == 'row-analysis-tab':
        return html.Div([
            html.H3("Row-Level Analysis", style={'marginBottom': 20}),
            
            # Row comparison chart
            html.Div([
                dcc.Graph(id='row-comparison-chart')
            ], style={'marginBottom': 30}),
            
            # Row statistics table
            html.Div([
                html.H4("Row Statistics Summary", style={'marginBottom': 15}),
                dash_table.DataTable(
                    columns=[
                        {'name': 'Metric', 'id': 'metric'},
                        {'name': 'Base Dataset', 'id': 'base'},
                        {'name': 'Compare Dataset', 'id': 'compare'},
                        {'name': 'Difference', 'id': 'difference'}
                    ],
                    data=[
                        {
                            'metric': 'Total Rows',
                            'base': f"{summary['total_rows_base']:,}",
                            'compare': f"{summary['total_rows_compare']:,}",
                            'difference': f"{summary['total_rows_compare'] - summary['total_rows_base']:+,}"
                        },
                        {
                            'metric': 'Unique Rows',
                            'base': f"{summary['rows_only_base']:,}",
                            'compare': f"{summary['rows_only_compare']:,}",
                            'difference': f"{summary['rows_only_compare'] - summary['rows_only_base']:+,}"
                        },
                        {
                            'metric': 'Common Rows',
                            'base': f"{summary['rows_both']:,}",
                            'compare': f"{summary['rows_both']:,}",
                            'difference': "0"
                        }
                    ],
                    style_cell={'textAlign': 'left'},
                    style_header={'backgroundColor': '#3498db', 'color': 'white'}
                )
            ])
        ])
    
    elif active_tab == 'column-analysis-tab':
        return html.Div([
            html.H3("Column-Level Analysis", style={'marginBottom': 20}),
            
            # Column match rates chart
            html.Div([
                dcc.Graph(id='column-match-rates')
            ], style={'marginBottom': 30}),
            
            # Column details table
            html.Div([
                html.H4("Detailed Column Comparison", style={'marginBottom': 15}),
                dash_table.DataTable(
                    id='column-details-table',
                    columns=[
                        {'name': 'Column', 'id': 'column_name'},
                        {'name': 'Matches', 'id': 'matches', 'type': 'numeric'},
                        {'name': 'Mismatches', 'id': 'mismatches', 'type': 'numeric'},
                        {'name': 'Match Rate', 'id': 'match_rate', 'type': 'numeric', 'format': {'specifier': '.1%'}},
                        {'name': 'Base Type', 'id': 'data_type_base'},
                        {'name': 'Compare Type', 'id': 'data_type_compare'},
                        {'name': 'Base Nulls', 'id': 'null_count_base', 'type': 'numeric'},
                        {'name': 'Compare Nulls', 'id': 'null_count_compare', 'type': 'numeric'}
                    ],
                    data=column_details.to_dict('records'),
                    style_cell={'textAlign': 'left'},
                    style_data_conditional=[
                        {
                            'if': {'filter_query': '{match_rate} < 0.9', 'column_id': 'match_rate'},
                            'backgroundColor': '#ffebee',
                            'color': 'black',
                        },
                        {
                            'if': {'filter_query': '{match_rate} >= 0.95', 'column_id': 'match_rate'},
                            'backgroundColor': '#e8f5e8',
                            'color': 'black',
                        }
                    ],
                    sort_action="native"
                )
            ])
        ])
    
    elif active_tab == 'mismatch-details-tab':
        return html.Div([
            html.H3("Mismatch Analysis", style={'marginBottom': 20}),
            
            # Mismatch distribution chart
            html.Div([
                dcc.Graph(id='mismatch-distribution')
            ], style={'marginBottom': 30}),
            
            # Mismatched records table
            html.Div([
                html.H4("Sample Mismatched Records", style={'marginBottom': 15}),
                dash_table.DataTable(
                    id='mismatched-records-table',
                    columns=[
                        {'name': 'Row ID', 'id': 'row_id'},
                        {'name': 'Column', 'id': 'column'},
                        {'name': 'Base Value', 'id': 'base_value'},
                        {'name': 'Compare Value', 'id': 'compare_value'},
                        {'name': 'Difference', 'id': 'difference'}
                    ],
                    data=mismatched_records.to_dict('records'),
                    style_cell={'textAlign': 'left'},
                    page_size=15,
                    sort_action="native",
                    filter_action="native"
                )
            ])
        ])
    
    elif active_tab == 'data-quality-tab':
        return html.Div([
            html.H3("Data Quality Assessment", style={'marginBottom': 20}),
            
            # Data quality metrics
            html.Div([
                html.Div([
                    html.H4("Null Value Analysis", style={'marginBottom': 15}),
                    dcc.Graph(id='null-analysis-chart')
                ], style={'width': '48%', 'display': 'inline-block'}),
                
                html.Div([
                    html.H4("Data Type Consistency", style={'marginBottom': 15}),
                    dcc.Graph(id='datatype-consistency-chart')
                ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
            ], style={'marginBottom': 30}),
            
            # Quality recommendations
            html.Div([
                html.H4("Data Quality Recommendations", style={'marginBottom': 15}),
                html.Div(id='quality-recommendations')
            ], style={'backgroundColor': '#fff3cd', 'padding': '20px', 'borderRadius': '8px'})
        ])

# Callbacks for interactive charts
@app.callback(
    Output('row-comparison-chart', 'figure'),
    [Input('main-tabs', 'value')]
)
def update_row_comparison(active_tab):
    """Create row comparison chart"""
    
    # Data for row comparison
    categories = ['Rows Only in Base', 'Rows Only in Compare', 'Rows in Both']
    values = [summary['rows_only_base'], summary['rows_only_compare'], summary['rows_both']]
    colors = ['#e74c3c', '#f39c12', '#27ae60']
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=values,
            marker_color=colors,
            text=[f'{v:,}' for v in values],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Row Distribution Comparison",
        xaxis_title="Category",
        yaxis_title="Count",
        height=400,
        showlegend=False
    )
    
    return fig

@app.callback(
    Output('column-match-rates', 'figure'),
    [Input('main-tabs', 'value')]
)
def update_column_match_rates(active_tab):
    """Create column match rates chart"""
    
    fig = px.bar(
        column_details, 
        x='column_name', 
        y='match_rate',
        title="Match Rate by Column",
        color='match_rate',
        color_continuous_scale='RdYlGn',
        range_color=[0.8, 1.0]
    )
    
    fig.update_layout(
        xaxis_title="Column",
        yaxis_title="Match Rate",
        height=400,
        yaxis_tickformat='.1%'
    )
    
    return fig

@app.callback(
    Output('mismatch-distribution', 'figure'),
    [Input('main-tabs', 'value')]
)
def update_mismatch_distribution(active_tab):
    """Create mismatch distribution chart"""
    
    # Count mismatches by column
    mismatch_counts = mismatched_records['column'].value_counts()
    
    fig = px.pie(
        values=mismatch_counts.values,
        names=mismatch_counts.index,
        title="Distribution of Mismatches by Column"
    )
    
    fig.update_layout(height=400)
    
    return fig

@app.callback(
    Output('null-analysis-chart', 'figure'),
    [Input('main-tabs', 'value')]
)
def update_null_analysis(active_tab):
    """Create null value analysis chart"""
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Base Dataset',
        x=column_details['column_name'],
        y=column_details['null_count_base'],
        marker_color='#3498db'
    ))
    
    fig.add_trace(go.Bar(
        name='Compare Dataset',
        x=column_details['column_name'],
        y=column_details['null_count_compare'],
        marker_color='#e74c3c'
    ))
    
    fig.update_layout(
        title="Null Value Comparison by Column",
        xaxis_title="Column",
        yaxis_title="Null Count",
        height=400,
        barmode='group'
    )
    
    return fig

@app.callback(
    Output('datatype-consistency-chart', 'figure'),
    [Input('main-tabs', 'value')]
)
def update_datatype_consistency(active_tab):
    """Create data type consistency chart"""
    
    # Check for type mismatches
    type_matches = (column_details['data_type_base'] == column_details['data_type_compare']).sum()
    type_mismatches = len(column_details) - type_matches
    
    fig = go.Figure(data=[
        go.Pie(
            labels=['Type Matches', 'Type Mismatches'],
            values=[type_matches, type_mismatches],
            marker_colors=['#27ae60', '#e74c3c']
        )
    ])
    
    fig.update_layout(
        title="Data Type Consistency",
        height=400
    )
    
    return fig

@app.callback(
    Output('quality-recommendations', 'children'),
    [Input('main-tabs', 'value')]
)
def update_quality_recommendations(active_tab):
    """Generate data quality recommendations"""
    
    recommendations = []
    
    # Check for low match rates
    low_match_columns = column_details[column_details['match_rate'] < 0.9]
    if not low_match_columns.empty:
        recommendations.append(
            html.Li(f"🔍 Investigate columns with low match rates: {', '.join(low_match_columns['column_name'].tolist())}")
        )
    
    # Check for null value differences
    null_diff_columns = column_details[
        abs(column_details['null_count_base'] - column_details['null_count_compare']) > 5
    ]
    if not null_diff_columns.empty:
        recommendations.append(
            html.Li(f"🔧 Review null value handling for: {', '.join(null_diff_columns['column_name'].tolist())}")
        )
    
    # Check for type mismatches
    type_mismatch_columns = column_details[
        column_details['data_type_base'] != column_details['data_type_compare']
    ]
    if not type_mismatch_columns.empty:
        recommendations.append(
            html.Li(f"⚠️ Fix data type inconsistencies in: {', '.join(type_mismatch_columns['column_name'].tolist())}")
        )
    
    # General recommendations
    if summary['match_rate'] < 0.95:
        recommendations.append(
            html.Li("📊 Overall match rate is below 95%. Consider data validation improvements.")
        )
    
    if abs(summary['total_rows_compare'] - summary['total_rows_base']) > 50:
        recommendations.append(
            html.Li("📈 Significant row count difference detected. Verify data completeness.")
        )
    
    if not recommendations:
        recommendations.append(
            html.Li("✅ Data quality looks good! No major issues detected.")
        )
    
    return html.Ul(recommendations)

# CSS styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f8f9fa;
            }
            .summary-card {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
                min-width: 180px;
                flex: 1;
                margin: 0 5px;
                transition: transform 0.2s ease;
            }
            .summary-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }
            .summary-card-small {
                background: white;
                padding: 15px;
                border-radius: 6px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                text-align: center;
                min-width: 120px;
                flex: 1;
                margin: 0 3px;
                transition: transform 0.2s ease;
            }
            .summary-card-small:hover {
                transform: translateY(-1px);
                box-shadow: 0 2px 6px rgba(0,0,0,0.15);
            }
            .summary-card h3 {
                font-size: 2em;
                font-weight: bold;
            }
            .summary-card-small h4 {
                font-size: 1.4em;
                font-weight: bold;
            }
            .summary-card p, .summary-card-small p {
                color: #666;
                font-size: 0.9em;
            }
            .dash-table-container {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .tab-content {
                min-height: 500px;
            }
            ._dash-undo-redo {
                display: none;
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

if __name__ == '__main__':
    app.run_server(debug=True)
