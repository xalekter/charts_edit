import dash
from dash import dcc, html, Input, Output, State, callback_context, dash_table
from dash.dependencies import ALL
import plotly.graph_objs as go
import pandas as pd
import io
import base64
import json

# Initialize the Dash app
app = dash.Dash(__name__)

# Global variable to store data
data_store = {'df': None, 'original_df': None, 'x_col': None, 'y_col': None, 'markers': []}

app.layout = html.Div([
    html.H1("FM-Trace Editor", style={'textAlign': 'center', 'marginBottom': 30}),
    
    # File upload section
    html.Div([
        html.H3("File Operations"),
        dcc.Upload(
            id='upload-data',
            children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
            style={
                'width': '100%', 'height': '60px', 'lineHeight': '60px',
                'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                'textAlign': 'center', 'margin': '10px'
            },
            multiple=False
        ),
        html.Div(id='upload-status'),
        html.Button('Download Modified Data', id='download-btn', style={'margin': '10px'}),
        dcc.Download(id="download-data"),
        html.Button('Reset Changes', id='reset-btn', style={'margin': '10px'}),
    ], style={'marginBottom': 30, 'padding': 20, 'border': '1px solid #ddd', 'borderRadius': 5}),
    
    # Instructions
    html.Div([
        html.H4("🔬 Species Analysis:"),
        html.P("🔍 Filter by species (Sc) to compare different organisms"),
        html.P("📅 Add vertical marker lines for important phenological dates"),
        html.P("📈 Blue/colored lines show species-specific trends"),
        html.P("🎯 Red circles are editable points - click to select for editing"),
        html.P("⌨️ Keyboard shortcuts: Arrow keys move selected points (←→ X-axis, ↑↓ Y-axis)"),
        html.P("🧠 Smart interpolation: New points calculate realistic values for all parameters"),
        html.P("⌨️ Use fine-tune buttons for precise species-specific adjustments"),
    ], style={'backgroundColor': '#f8f9fa', 'padding': 15, 'borderRadius': 5, 'marginBottom': 20}),
    
    # Plot controls with filtering
    html.Div([
        html.H3("Plot Controls & Filtering"),
        
        # Filtering section
        html.Div([
            html.H5("🔍 Data Filtering"),
            html.Div([
                html.Label("Filter by Species (Sc): "),
                dcc.Dropdown(id='species-filter', multi=True, placeholder="Select species (leave empty for all)", 
                           style={'width': '200px', 'display': 'inline-block', 'marginRight': 15}),
                html.Label("Filter by Site (SiteC): "),
                dcc.Dropdown(id='site-filter', multi=True, placeholder="Select sites (leave empty for all)", 
                           style={'width': '200px', 'display': 'inline-block', 'marginRight': 15}),
            ], style={'marginBottom': 10}),
            html.Div([
                html.Label("Filter by Description: "),
                dcc.Dropdown(id='description-filter', multi=True, placeholder="Select descriptions (optional)", 
                           style={'width': '300px', 'display': 'inline-block'}),
            ], style={'marginBottom': 15}),
            html.Div(id='filter-status', style={'fontSize': '14px', 'color': '#6c757d', 'marginBottom': 10}),
        ], style={'marginBottom': 20, 'padding': 15, 'backgroundColor': '#e8f4f8', 'borderRadius': 5}),
        
        # Phenological markers section
        html.Div([
            html.H5("📅 Phenological Date Markers"),
            html.Div([
                html.Label("Add Important DOY: "),
                dcc.Input(id='marker-doy', type='number', placeholder="DOY (1-365)", min=1, max=365, 
                         style={'width': '100px', 'marginRight': 10}),
                html.Label("Label: "),
                dcc.Input(id='marker-label', type='text', placeholder="e.g., First Buds", 
                         style={'width': '150px', 'marginRight': 10}),
                html.Label("Color: "),
                dcc.Dropdown(
                    id='marker-color',
                    options=[
                        {'label': '🔴 Red', 'value': 'red'},
                        {'label': '🟠 Orange', 'value': 'orange'},
                        {'label': '🟡 Gold', 'value': 'gold'},
                        {'label': '🟢 Green', 'value': 'green'},
                        {'label': '🔵 Blue', 'value': 'blue'},
                        {'label': '🟣 Purple', 'value': 'purple'},
                        {'label': '🟤 Brown', 'value': 'brown'},
                        {'label': '⚫ Black', 'value': 'black'}
                    ],
                    value='red',
                    style={'width': '120px', 'display': 'inline-block', 'marginRight': 10}
                ),
                html.Button('Add Marker', id='add-marker-btn', 
                           style={'backgroundColor': '#ffc107', 'color': 'black', 'border': 'none', 'padding': '8px 12px', 'borderRadius': '4px'}),
            ], style={'marginBottom': 10}),
            
            # Quick preset buttons
            html.Div([
                html.Label("Quick Presets: ", style={'marginRight': 10}),
                html.Button('Spring Start (DOY 80)', id='preset-spring', style={'margin': '2px', 'padding': '4px 8px', 'fontSize': '12px'}),
                html.Button('Peak Growing (DOY 150)', id='preset-peak', style={'margin': '2px', 'padding': '4px 8px', 'fontSize': '12px'}),
                html.Button('Autumn Start (DOY 245)', id='preset-autumn', style={'margin': '2px', 'padding': '4px 8px', 'fontSize': '12px'}),
                html.Button('Winter Start (DOY 335)', id='preset-winter', style={'margin': '2px', 'padding': '4px 8px', 'fontSize': '12px'}),
                html.Button('Clear All Markers', id='clear-markers-btn', 
                           style={'margin': '2px', 'padding': '4px 8px', 'fontSize': '12px', 'backgroundColor': '#dc3545', 'color': 'white', 'border': 'none'}),
            ]),
            
            # Current markers display
            html.Div(id='current-markers', style={'marginTop': 10, 'fontSize': '14px'}),
        ], style={'marginBottom': 20, 'padding': 15, 'backgroundColor': '#fff3cd', 'borderRadius': 5}),
        
        # Plot axis selection
        html.Div([
            html.H5("📊 Axis Selection"),
            html.Div([
                html.Label("X-axis Column:"),
                dcc.Dropdown(id='x-column', style={'width': '200px', 'display': 'inline-block', 'marginRight': 20}),
                html.Label("Y-axis Column:"),
                dcc.Dropdown(id='y-column', style={'width': '200px', 'display': 'inline-block'}),
            ]),
            html.Button('Create Plot', id='plot-btn', style={'margin': '10px', 'backgroundColor': '#17a2b8', 'color': 'white', 'border': 'none', 'padding': '10px 20px', 'borderRadius': '5px'}),
        ]),
    ], style={'marginBottom': 30, 'padding': 20, 'border': '1px solid #ddd', 'borderRadius': 5}),
    
    # Point editing controls - now more streamlined
    html.Div([
        html.H4("Point Operations"),
        
        # Quick edit section
        html.Div([
            html.H5("🎯 Quick Edit (Click any red point)"),
            html.Div([
                html.Span("Selected: ", style={'fontWeight': 'bold'}),
                html.Span(id='selected-point', children="None", style={'fontWeight': 'bold', 'color': 'blue', 'marginRight': 20}),
                html.Label("X: "),
                dcc.Input(id='new-x-value', type='number', step=0.01, style={'width': '100px', 'marginRight': 10}),
                html.Label("Y: "),
                dcc.Input(id='new-y-value', type='number', step=0.01, style={'width': '100px', 'marginRight': 10}),
                html.Button('Update', id='update-point-btn', style={'backgroundColor': '#007bff', 'color': 'white', 'border': 'none', 'padding': '5px 15px', 'borderRadius': '4px', 'marginRight': 10}),
                html.Button('Delete', id='remove-point-btn', style={'backgroundColor': '#dc3545', 'color': 'white', 'border': 'none', 'padding': '5px 15px', 'borderRadius': '4px'}),
            ], style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'}),
        ], style={'marginBottom': 15, 'padding': 15, 'backgroundColor': '#f8f9fa', 'borderRadius': 5}),
        
        # Fine-tune controls
        html.Div([
            html.H5("⌨️ Fine-tune Selected Point (Arrow Keys or Buttons)"),
            html.P("🎮 Use keyboard: ← → for X-axis, ↑ ↓ for Y-axis", 
                style={'fontSize': '12px', 'color': '#6c757d', 'marginBottom': 10}),
            html.Div([
                html.Button('← X-1 (←)', id='x-minus-btn', style={'margin': '2px', 'padding': '5px 10px'}),
                html.Button('X+1 → (→)', id='x-plus-btn', style={'margin': '2px', 'padding': '5px 10px'}),
                html.Button('↓ Y-0.1 (↓)', id='y-minus-btn', style={'margin': '2px', 'padding': '5px 10px'}),
                html.Button('Y+0.1 ↑ (↑)', id='y-plus-btn', style={'margin': '2px', 'padding': '5px 10px'}),
                html.Div("Step size:", style={'display': 'inline-block', 'marginLeft': 15}),
                dcc.Input(id='step-size', type='number', value=0.1, step=0.01, style={'width': '80px', 'marginLeft': 5}),
            ], style={'display': 'flex', 'alignItems': 'center', 'gap': '5px'}),
        ], style={'marginBottom': 15, 'padding': 15, 'backgroundColor': '#fff3cd', 'borderRadius': 5}),
        
        # Add new point
        html.Div([
            html.H5("➕ Add New Point (Smart Interpolation)"),
            html.P("🧠 Automatically interpolates all parameters from neighboring points", 
                style={'fontSize': '12px', 'color': '#6c757d', 'marginBottom': 10}),
            html.Div([
                html.Label("X: "),
                dcc.Input(id='add-x-value', type='number', step=0.01, style={'width': '100px', 'marginRight': 15}),
                html.Label("Y: "),
                dcc.Input(id='add-y-value', type='number', step=0.01, style={'width': '100px', 'marginRight': 15}),
                html.Button('Add Point', id='add-point-btn', style={'backgroundColor': '#28a745', 'color': 'white', 'border': 'none', 'padding': '8px 16px', 'borderRadius': '4px'}),
            ], style={'display': 'flex', 'alignItems': 'center'}),
            html.Div(id='add-point-status', style={'marginTop': 10, 'fontSize': '14px'}),
        ], style={'padding': 15, 'backgroundColor': '#d1ecf1', 'borderRadius': 5}),
        
    ], style={'marginBottom': 30, 'padding': 20, 'border': '1px solid #ddd', 'borderRadius': 5}),
    
    # Plot area and statistics
    html.Div([
        dcc.Graph(id='interactive-plot', style={'height': '600px'}),
        # Statistics panel
        html.Div([
            html.Div(id='plot-stats', style={
                'backgroundColor': '#f8f9fa', 
                'padding': '10px', 
                'borderRadius': '5px', 
                'marginTop': '10px',
                'border': '1px solid #dee2e6'
            })
        ])
    ]),
    
    # Data table
    html.Div([
        html.H3("📊 Filtered Data Preview"),
        html.Div(id='data-table'),
    ], style={'marginTop': 30}),
    
    # Hidden div to store data
    html.Div(id='data-store', style={'display': 'none'}),

    # Keyboard event listener - add this new component
    html.Div(
        id='keyboard-listener',
        children=[],
        tabIndex=0,  # Make it focusable
        style={
            'position': 'fixed',
            'top': 0,
            'left': 0,
            'width': '100%',
            'height': '100%',
            'outline': 'none',
            'pointerEvents': 'none',  # Don't interfere with other interactions
            'zIndex': -1
        }
    ),
    
    # Status
    html.Div(id='status', style={'marginTop': 20, 'padding': 10, 'backgroundColor': '#f0f0f0'}),

# Keyboard handler script
html.Script("""
    document.addEventListener('keydown', function(event) {
        // Only handle when not typing in inputs
        if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA') {
            return;
        }
        
        // Handle arrow keys
        if (event.key === 'ArrowLeft') {
            event.preventDefault();
            const btn = document.getElementById('x-minus-btn');
            if (btn) btn.click();
        } else if (event.key === 'ArrowRight') {
            event.preventDefault();
            const btn = document.getElementById('x-plus-btn');
            if (btn) btn.click();
        } else if (event.key === 'ArrowDown') {
            event.preventDefault();
            const btn = document.getElementById('y-minus-btn');
            if (btn) btn.click();
        } else if (event.key === 'ArrowUp') {
            event.preventDefault();
            const btn = document.getElementById('y-plus-btn');
            if (btn) btn.click();
        }
    });
    """)
])

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        else:
            # Try tab-separated first
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep='\t')
    except Exception as e:
        return None, f"Error reading file: {str(e)}"
    
    return df, f"Successfully loaded {len(df)} rows and {len(df.columns)} columns"

def create_interpolated_row(df, new_x, x_col, y_col, new_y, species_filter=None, site_filter=None):
    """
    Create a new row with interpolated values for all parameters.
    Respects current filters and rounds decimal values to 2 places.
    """
    import numpy as np
    
    def round_if_decimal(value):
        """Round numeric values to 2 decimal places if they have decimal part"""
        try:
            if pd.isna(value):
                return value
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                # Check if it's effectively an integer
                if abs(value - round(value)) < 1e-10:
                    return int(round(value))
                else:
                    return round(float(value), 2)
            return value
        except (TypeError, ValueError):
            return value
    
    # Apply filters to get relevant data for interpolation
    working_df = df.copy()
    original_len = len(working_df)
    
    # Filter by species if specified
    if species_filter and len(species_filter) == 1:
        species_data = working_df[working_df['Sc'] == species_filter[0]]
        if len(species_data) > 0:
            working_df = species_data
    
    # Filter by site if specified  
    if site_filter and len(site_filter) == 1:
        site_data = working_df[working_df['SiteC'] == site_filter[0]]
        if len(site_data) > 0:
            working_df = site_data
    
    # Handle edge cases
    if len(working_df) == 0:
        # Create basic row with filter values
        new_row = pd.Series(dtype=object)
        new_row[x_col] = new_x
        new_row[y_col] = round_if_decimal(new_y)
        
        # Set categorical values from filters
        if species_filter and len(species_filter) == 1:
            new_row['Sc'] = species_filter[0]
        if site_filter and len(site_filter) == 1:
            new_row['SiteC'] = site_filter[0]
            
        # Set default values for other common columns
        for col in df.columns:
            if col not in [x_col, y_col, 'Sc', 'SiteC'] and col not in new_row:
                if df[col].dtype in ['object', 'string']:
                    new_row[col] = '-'  # Default categorical value
                else:
                    new_row[col] = round_if_decimal(df[col].median())  # Use median for numeric
        
        return new_row
    
    if len(working_df) == 1:
        new_row = working_df.iloc[0].copy()
        new_row[x_col] = new_x  
        new_row[y_col] = round_if_decimal(new_y)
        return new_row
    
    # Sort for interpolation
    df_sorted = working_df.sort_values(x_col).reset_index(drop=True)
    x_values = df_sorted[x_col].values
    
    # Determine interpolation strategy
    if new_x <= x_values[0]:
        # Extrapolate from first point
        new_row = df_sorted.iloc[0].copy()
        interp_type = "extrapolated_before"
    elif new_x >= x_values[-1]:
        # Extrapolate from last point
        new_row = df_sorted.iloc[-1].copy()  
        interp_type = "extrapolated_after"
    else:
        # Interpolate between points
        try:
            idx_after = np.searchsorted(x_values, new_x)
            idx_before = max(0, idx_after - 1)
            idx_after = min(len(df_sorted) - 1, idx_after)
            
            x_before = x_values[idx_before]
            x_after = x_values[idx_after]
            
            if abs(x_after - x_before) < 1e-10:
                # Points are essentially at same X value
                new_row = df_sorted.iloc[idx_before].copy()
                interp_type = "duplicated_x"
            else:
                # Linear interpolation
                weight = (new_x - x_before) / (x_after - x_before)
                new_row = df_sorted.iloc[idx_before].copy()
                
                # Get all numeric columns for interpolation
                numeric_columns = df_sorted.select_dtypes(include=[np.number]).columns
                
                for col in numeric_columns:
                    if col != x_col:  # Don't interpolate X column
                        try:
                            value_before = df_sorted.iloc[idx_before][col]
                            value_after = df_sorted.iloc[idx_after][col]
                            
                            # Skip NaN values
                            if pd.isna(value_before) or pd.isna(value_after):
                                continue
                            
                            # Linear interpolation with rounding
                            interpolated = value_before + weight * (value_after - value_before)
                            new_row[col] = round_if_decimal(interpolated)
                            
                        except (KeyError, TypeError, ValueError):
                            continue
                
                # Handle categorical columns (take from closest point)
                categorical_columns = df_sorted.select_dtypes(exclude=[np.number]).columns
                for col in categorical_columns:
                    if col not in [x_col, y_col]:
                        try:
                            if weight < 0.5:
                                new_row[col] = df_sorted.iloc[idx_before][col]
                            else:
                                new_row[col] = df_sorted.iloc[idx_after][col]
                        except (KeyError, TypeError):
                            continue
                
                interp_type = "interpolated"
                
        except Exception as e:
            # Fallback to nearest point
            new_row = df_sorted.iloc[0].copy()
            interp_type = "fallback"
    
    # Set final X and Y values with rounding
    new_row[x_col] = new_x  # X is usually DOY (integer)
    new_row[y_col] = round_if_decimal(new_y)
    
    # Override with single filter values if specified
    if species_filter and len(species_filter) == 1:
        new_row['Sc'] = species_filter[0]
    if site_filter and len(site_filter) == 1:
        new_row['SiteC'] = site_filter[0]
    
    # Apply rounding to all numeric columns in final row
    for col in new_row.index:
        try:
            if col in df.select_dtypes(include=[np.number]).columns:
                new_row[col] = round_if_decimal(new_row[col])
        except (KeyError, TypeError):
            continue
    
    return new_row

def apply_filters(df, species_filter, site_filter, description_filter):
    """Apply selected filters to the dataframe"""
    filtered_df = df.copy()
    
    if species_filter:
        filtered_df = filtered_df[filtered_df['Sc'].isin(species_filter)]
    
    if site_filter:
        filtered_df = filtered_df[filtered_df['SiteC'].isin(site_filter)]
    
    if description_filter:
        filtered_df = filtered_df[filtered_df['Description'].isin(description_filter)]
    
    return filtered_df

def display_current_markers():
    if not data_store['markers']:
        return "No markers set"
    
    marker_elements = []
    for i, marker in enumerate(data_store['markers']):
        color_emoji = {
            'red': '🔴', 'orange': '🟠', 'gold': '🟡', 'green': '🟢',
            'blue': '🔵', 'purple': '🟣', 'brown': '🟤', 'black': '⚫'
        }.get(marker['color'], '📍')
        
        marker_elements.extend([
            html.Span(f"{color_emoji} DOY {marker['doy']}: {marker['label']}", 
                     style={'marginRight': 15, 'fontSize': '13px'}),
            html.Button('×', id={'type': 'remove-marker', 'index': i}, 
                       style={'fontSize': '12px', 'padding': '2px 6px', 'marginRight': 10, 
                             'backgroundColor': '#dc3545', 'color': 'white', 'border': 'none', 'borderRadius': '3px'})
        ])
    
    return html.Div(marker_elements)

@app.callback(
    [Output('upload-status', 'children'),
     Output('x-column', 'options'),
     Output('y-column', 'options'),
     Output('x-column', 'value'),
     Output('y-column', 'value'),
     Output('species-filter', 'options'),
     Output('site-filter', 'options'),
     Output('description-filter', 'options'),
     Output('data-store', 'children')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_output(contents, filename):
    if contents is None:
        return "", [], [], None, None, [], [], [], ""
    
    df, message = parse_contents(contents, filename)
    if df is None:
        return message, [], [], None, None, [], [], [], ""
    
    # Store data globally
    data_store['df'] = df
    data_store['original_df'] = df.copy()
    
    # Get column options
    all_columns = [{'label': col, 'value': col} for col in df.columns]
    numeric_columns = [{'label': col, 'value': col} for col in df.select_dtypes(include=['number']).columns]
    
    # Get filter options
    species_options = []
    site_options = []
    description_options = []
    
    # Species filter (Sc column)
    if 'Sc' in df.columns:
        unique_species = sorted(df['Sc'].dropna().unique())
        species_options = [{'label': species, 'value': species} for species in unique_species]
    
    # Site filter (SiteC column)
    if 'SiteC' in df.columns:
        unique_sites = sorted(df['SiteC'].dropna().unique())
        site_options = [{'label': site, 'value': site} for site in unique_sites]
    
    # Description filter
    if 'Description' in df.columns:
        unique_descriptions = sorted(df['Description'].dropna().unique())
        description_options = [{'label': desc, 'value': desc} for desc in unique_descriptions if desc != '-']
    
    # Set default values
    x_default = 'DOY' if 'DOY' in df.columns else df.columns[0]
    y_default = None
    if len(numeric_columns) > 1:
        y_default = numeric_columns[1]['value']
    elif len(numeric_columns) > 0:
        y_default = numeric_columns[0]['value']
    
    return message, all_columns, numeric_columns, x_default, y_default, species_options, site_options, description_options, df.to_json()

@app.callback(
    Output('filter-status', 'children'),
    [Input('species-filter', 'value'),
     Input('site-filter', 'value'),
     Input('description-filter', 'value')]
)
def update_filter_status(species_filter, site_filter, description_filter):
    if not species_filter and not site_filter and not description_filter:
        return "📊 Showing all data"
    
    status_parts = []
    if species_filter:
        status_parts.append(f"Species: {', '.join(species_filter)}")
    if site_filter:
        status_parts.append(f"Sites: {', '.join(site_filter)}")
    if description_filter:
        status_parts.append(f"Descriptions: {', '.join(description_filter)}")
    
    return f"🔍 Filtered by: {' | '.join(status_parts)}"

@app.callback(
    [Output('current-markers', 'children'),
     Output('marker-doy', 'value'),
     Output('marker-label', 'value')],
    [Input('add-marker-btn', 'n_clicks'),
     Input('preset-spring', 'n_clicks'),
     Input('preset-peak', 'n_clicks'),
     Input('preset-autumn', 'n_clicks'),
     Input('preset-winter', 'n_clicks'),
     Input('clear-markers-btn', 'n_clicks')],
    [State('marker-doy', 'value'),
     State('marker-label', 'value'),
     State('marker-color', 'value')]
)
def manage_markers(add_clicks, spring_clicks, peak_clicks, autumn_clicks, winter_clicks, clear_clicks,
                   marker_doy, marker_label, marker_color):
    ctx = callback_context
    
    if ctx.triggered:
        trigger_id = ctx.triggered[0]['prop_id']
        
        # Handle clear all markers
        if 'clear-markers-btn' in trigger_id:
            data_store['markers'] = []
        
        # Handle preset buttons
        elif 'preset-spring' in trigger_id:
            data_store['markers'].append({
                'doy': 80,
                'label': 'Spring Start',
                'color': 'green'
            })
        elif 'preset-peak' in trigger_id:
            data_store['markers'].append({
                'doy': 150,
                'label': 'Peak Growing',
                'color': 'orange'
            })
        elif 'preset-autumn' in trigger_id:
            data_store['markers'].append({
                'doy': 245,
                'label': 'Autumn Start',
                'color': 'brown'
            })
        elif 'preset-winter' in trigger_id:
            data_store['markers'].append({
                'doy': 335,
                'label': 'Winter Start',
                'color': 'blue'
            })
        
        # Handle manual add marker
        elif 'add-marker-btn' in trigger_id and marker_doy is not None and marker_label:
            data_store['markers'].append({
                'doy': marker_doy,
                'label': marker_label,
                'color': marker_color or 'red'
            })
            
            # Clear input fields after adding
            return display_current_markers(), None, ""
    
    return display_current_markers(), marker_doy, marker_label

@app.callback(
    Output('current-markers', 'children', allow_duplicate=True),
    [Input({'type': 'remove-marker', 'index': ALL}, 'n_clicks')],
    prevent_initial_call=True
)
def remove_marker(remove_clicks):
    ctx = callback_context
    if not ctx.triggered or not any(remove_clicks):
        return display_current_markers()
    
    # Find which marker to remove
    for i, clicks in enumerate(remove_clicks):
        if clicks:
            if i < len(data_store['markers']):
                data_store['markers'].pop(i)
            break
    
    return display_current_markers()

@app.callback(
    [Output('interactive-plot', 'figure'),
     Output('status', 'children'),
     Output('plot-stats', 'children')],
    [Input('plot-btn', 'n_clicks'),
     Input('update-point-btn', 'n_clicks'),
     Input('add-point-btn', 'n_clicks'),
     Input('remove-point-btn', 'n_clicks'),
     Input('x-minus-btn', 'n_clicks'),
     Input('x-plus-btn', 'n_clicks'),
     Input('y-minus-btn', 'n_clicks'),
     Input('y-plus-btn', 'n_clicks'),
     Input('species-filter', 'value'),
     Input('site-filter', 'value'),
     Input('description-filter', 'value'),
     Input('add-marker-btn', 'n_clicks'),
     Input('preset-spring', 'n_clicks'),
     Input('preset-peak', 'n_clicks'),
     Input('preset-autumn', 'n_clicks'),
     Input('preset-winter', 'n_clicks'),
     Input('clear-markers-btn', 'n_clicks'),
     Input({'type': 'remove-marker', 'index': ALL}, 'n_clicks')],
    [State('x-column', 'value'),
     State('y-column', 'value'),
     State('new-x-value', 'value'),
     State('new-y-value', 'value'),
     State('add-x-value', 'value'),
     State('add-y-value', 'value'),
     State('selected-point', 'children'),
     State('step-size', 'value')]
)
def update_plot(plot_clicks, update_clicks, add_clicks, remove_clicks, 
                x_minus_clicks, x_plus_clicks, y_minus_clicks, y_plus_clicks,
                species_filter, site_filter, description_filter,
                add_marker_clicks, spring_clicks, peak_clicks, autumn_clicks, winter_clicks, clear_markers_clicks, remove_marker_clicks,
                x_col, y_col, new_x, new_y, add_x, add_y, selected_point, step_size):
    ctx = callback_context
    
    if data_store['df'] is None:
        return {}, "Load data first", ""
    
    df = data_store['df']
    
    # Apply filters to get the working dataset
    filtered_df = apply_filters(df, species_filter, site_filter, description_filter)
    
    if len(filtered_df) == 0:
        return {}, "❌ No data matches the selected filters", ""
    
    # Handle editing operations on the full dataset
    status_message = f"Plotted {len(filtered_df)} points (filtered from {len(df)} total)"
    
    # Handle different button clicks - these operate on the full dataset
    if ctx.triggered:
        trigger_id = ctx.triggered[0]['prop_id']
        
        # Handle fine-tuning buttons
        if selected_point != "None" and step_size is not None:
            try:
                
                point_idx = int(selected_point)
                current_x = df.iloc[point_idx, df.columns.get_loc(data_store['x_col'])]
                current_y = df.iloc[point_idx, df.columns.get_loc(data_store['y_col'])]

                if data_store['x_col'] == 'DOY':
                    x_step_size = 1  # Whole days for DOY
                elif 'date' in data_store['x_col'].lower():
                    x_step_size = 1  # Whole days for any date column
                else:
                    x_step_size = step_size  # Use user-defined for other X columns
                
                if 'x-minus-btn' in trigger_id:
                    new_x_val = current_x - x_step_size
                    df.iloc[point_idx, df.columns.get_loc(data_store['x_col'])] = new_x_val
                    status_message = f"⬅️ Moved point {point_idx} X: {current_x:.3f} → {new_x_val:.3f}"
                    x_col, y_col = data_store['x_col'], data_store['y_col']
                elif 'x-plus-btn' in trigger_id:
                    new_x_val = current_x + x_step_size
                    df.iloc[point_idx, df.columns.get_loc(data_store['x_col'])] = new_x_val
                    status_message = f"➡️ Moved point {point_idx} X: {current_x:.3f} → {new_x_val:.3f}"
                    x_col, y_col = data_store['x_col'], data_store['y_col']
                elif 'y-minus-btn' in trigger_id:
                    new_y_val = current_y - step_size
                    df.iloc[point_idx, df.columns.get_loc(data_store['y_col'])] = new_y_val
                    status_message = f"⬇️ Moved point {point_idx} Y: {current_y:.3f} → {new_y_val:.3f}"
                    x_col, y_col = data_store['x_col'], data_store['y_col']
                elif 'y-plus-btn' in trigger_id:
                    new_y_val = current_y + step_size
                    df.iloc[point_idx, df.columns.get_loc(data_store['y_col'])] = new_y_val
                    status_message = f"⬆️ Moved point {point_idx} Y: {current_y:.3f} → {new_y_val:.3f}"
                    x_col, y_col = data_store['x_col'], data_store['y_col']
                    
                # Re-apply filters after editing
                filtered_df = apply_filters(df, species_filter, site_filter, description_filter)
            except:
                pass
        
        # Handle point update
        if 'update-point-btn' in trigger_id:
            if selected_point != "None" and new_x is not None and new_y is not None:
                try:
                    point_idx = int(selected_point)
                    
                    # Update the dataframe
                    df.iloc[point_idx, df.columns.get_loc(data_store['x_col'])] = new_x
                    df.iloc[point_idx, df.columns.get_loc(data_store['y_col'])] = new_y
                    
                    status_message = f"✅ Updated point {point_idx} to ({new_x}, {new_y})"
                    
                    # Use current plot columns
                    x_col = data_store['x_col']
                    y_col = data_store['y_col']
                    
                    # Re-apply filters after editing
                    filtered_df = apply_filters(df, species_filter, site_filter, description_filter)
                except Exception as e:
                    status_message = f"❌ Error updating point: {str(e)}"
        
        # Handle point addition
        elif 'add-point-btn' in trigger_id:
            if add_x is not None and add_y is not None and data_store['x_col'] and data_store['y_col']:
                try:
                    # Create new row with interpolated values respecting current filters
                    new_row = create_interpolated_row(df, add_x, data_store['x_col'], data_store['y_col'], add_y, 
                                species_filter, site_filter)
                    
                    # Check if we got a valid row
                    if new_row is not None:
                        # Add the new row to main dataframe
                        df = pd.concat([df, new_row.to_frame().T], ignore_index=True)
                        data_store['df'] = df
                        
                        # Build status message with filter info
                        filter_info = []
                        if species_filter and len(species_filter) == 1:
                            filter_info.append(f"Species: {species_filter[0]}")
                        if site_filter and len(site_filter) == 1:
                            filter_info.append(f"Site: {site_filter[0]}")

                        # Determine interpolation context
                        context_info = ""
                        if len(df) > 1:
                            if add_x <= df[data_store['x_col']].min():
                                context_info = " (extrapolated from first)"
                            elif add_x >= df[data_store['x_col']].max():
                                context_info = " (extrapolated from last)"
                            else:
                                context_info = " (interpolated)"

                        filter_text = f" • {', '.join(filter_info)}" if filter_info else ""
                        rounded_y = round(add_y, 2) if isinstance(add_y, float) and add_y != int(add_y) else add_y

                        status_message = f"✅ Added point: DOY {add_x}, Y={rounded_y}{context_info}{filter_text}"
                    else:
                        status_message = "❌ Failed to create interpolated point"

                    
                    # Use current plot columns
                    x_col = data_store['x_col']
                    y_col = data_store['y_col']
                    
                    # Re-apply filters after adding
                    filtered_df = apply_filters(df, species_filter, site_filter, description_filter)
                except Exception as e:
                    status_message = f"❌ Error adding point: {str(e)}"
        
        # Handle point removal
        elif 'remove-point-btn' in trigger_id:
            if selected_point != "None":
                try:
                    point_idx = int(selected_point)
                    
                    # Remove the point from main dataframe
                    df = df.drop(df.index[point_idx]).reset_index(drop=True)
                    data_store['df'] = df
                    
                    status_message = f"🗑️ Removed point {point_idx}. Total points: {len(df)}"
                    
                    # Use current plot columns
                    x_col = data_store['x_col']
                    y_col = data_store['y_col']
                    
                    # Re-apply filters after removal
                    filtered_df = apply_filters(df, species_filter, site_filter, description_filter)
                except Exception as e:
                    status_message = f"❌ Error removing point: {str(e)}"
    
    if not x_col or not y_col:
        return {}, "Please select both X and Y columns and click 'Create Plot'", ""
    
    # Store current columns
    data_store['x_col'] = x_col
    data_store['y_col'] = y_col
    
    # Work with filtered data for plotting
    if len(filtered_df) == 0:
        return {}, "❌ No data matches the selected filters", ""
    
    fig = go.Figure()
    
    # Calculate statistics on filtered data
    y_mean = filtered_df[y_col].mean()
    y_std = filtered_df[y_col].std()
    y_min = filtered_df[y_col].min()
    y_max = filtered_df[y_col].max()
    
    # Create scatter+line plot (sorted by X for proper line connection)
    df_sorted = filtered_df.sort_values(x_col).reset_index(drop=True)
    
    # Color mapping for different species
    colors = ['steelblue', 'forestgreen', 'darkorange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
    
    if species_filter and len(species_filter) > 1:
        # Multiple species - use different colors
        for i, species in enumerate(species_filter):
            species_data = df_sorted[df_sorted['Sc'] == species]
            if len(species_data) > 0:
                color = colors[i % len(colors)]
                
                # Main trend line
                fig.add_trace(go.Scatter(
                    x=species_data[x_col],
                    y=species_data[y_col],
                    mode='lines+markers',
                    line=dict(color=color, width=2.5),
                    marker=dict(size=12, color=color, opacity=0.9),
                    name=f'{species} Trend',
                    hovertemplate=f'<b>{species}</b><br><b>{x_col}</b>: %{{x}}<br><b>{y_col}</b>: %{{y}}<extra></extra>',
                    yaxis='y'
                ))
    elif site_filter and len(site_filter) > 1:
        # Multiple sites - use different colors
        for i, site in enumerate(site_filter):
            site_data = df_sorted[df_sorted['SiteC'] == site]
            if len(site_data) > 0:
                color = colors[i % len(colors)]
                
                # Main trend line
                fig.add_trace(go.Scatter(
                    x=site_data[x_col],
                    y=site_data[y_col],
                    mode='lines+markers',
                    line=dict(color=color, width=2.5),
                    marker=dict(size=12, color=color, opacity=0.9),
                    name=f'Site {site} Trend',
                    hovertemplate=f'<b>Site {site}</b><br><b>{x_col}</b>: %{{x}}<br><b>{y_col}</b>: %{{y}}<extra></extra>',
                    yaxis='y'
                ))
    else:
        # Single species/site or no filter - use blue
        fig.add_trace(go.Scatter(
            x=df_sorted[x_col],
            y=df_sorted[y_col],
            mode='lines+markers',
            line=dict(color='rgba(70, 130, 180, 0.8)', width=2.5),
            marker=dict(size=12, color='steelblue', opacity=0.9, 
                       line=dict(width=1, color='darkblue')),
            name='Data Trend',
            hovertemplate=f'<b>Trend Line</b><br><b>{x_col}</b>: %{{x}}<br><b>{y_col}</b>: %{{y}}<extra></extra>',
            yaxis='y'
        ))
    
    # Editable points overlay (maintains original indices for editing)
    fig.add_trace(go.Scatter(
        x=filtered_df[x_col],
        y=filtered_df[y_col],
        mode='markers',
        marker=dict(size=10, color='red', opacity=0.8, 
                   line=dict(width=2, color='darkred'),
                   symbol='circle-open'),
        name='Edit Points',
        text=[f"Point {i}" for i in filtered_df.index],
        customdata=list(filtered_df.index),
        hovertemplate=f'<b>Editable Point %{{customdata}}</b><br><b>{x_col}</b>: %{{x}}<br><b>{y_col}</b>: %{{y}}<br><i>🎯 Click to select</i><extra></extra>',
        yaxis='y'
    ))
    
    # Add phenological marker lines
    if data_store['markers'] and len(filtered_df) > 0:
        for marker in data_store['markers']:
            marker_doy = marker['doy']
            marker_label = marker['label']
            marker_color = marker['color']
            
            # Only add marker if it's within the data range
            x_min, x_max = filtered_df[x_col].min(), filtered_df[x_col].max()
            if x_min <= marker_doy <= x_max:
                # Add vertical line
                fig.add_vline(
                    x=marker_doy,
                    line=dict(color=marker_color, width=2, dash='dashdot'),
                    annotation_text=marker_label,
                    annotation_position="top",
                    annotation_textangle=90,
                    annotation=dict(
                        font=dict(size=12, color=marker_color),
                        bgcolor="rgba(255,255,255,0.8)",
                        bordercolor=marker_color,
                        borderwidth=1
                    )
                )
    
    # Add mean line
    fig.add_trace(go.Scatter(
        x=[filtered_df[x_col].min(), filtered_df[x_col].max()],
        y=[y_mean, y_mean],
        mode='lines',
        line=dict(color='green', width=3, dash='dash'),
        name=f'Mean: {y_mean:.3f}',
        hovertemplate=f'<b>Mean Level</b>: {y_mean:.3f}<extra></extra>',
        yaxis='y'
    ))
    
    # Add secondary axis trace (invisible)
    fig.add_trace(go.Scatter(
        x=[filtered_df[x_col].min(), filtered_df[x_col].max()],
        y=[y_mean, y_mean],
        mode='lines',
        line=dict(color='green', width=0),
        name='Mean Level (AU)',
        yaxis='y2',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Build title with filter info and markers
    title_parts = [f'{y_col} vs {x_col} - {len(filtered_df)} points']
    if species_filter:
        title_parts.append(f"Species: {', '.join(species_filter)}")
    if site_filter:
        title_parts.append(f"Sites: {', '.join(site_filter)}")
    if data_store['markers']:
        title_parts.append(f"📅 {len(data_store['markers'])} markers")
    title_parts.append(f"Mean: {y_mean:.3f}")
    
    fig.update_layout(
        title=' • '.join(title_parts),
        xaxis_title=x_col,
        yaxis=dict(
            title=y_col,
            side='left'
        ),
        yaxis2=dict(
            title='Mean Level (Arbitrary Units)',
            side='right',
            overlaying='y',
            range=[y_mean - abs(y_mean) * 0.1, y_mean + abs(y_mean) * 0.1],
            tickmode='linear',
            tick0=y_mean,
            dtick=abs(y_mean) * 0.05 if y_mean != 0 else 0.1
        ),
        hovermode='closest',
        height=600,
        clickmode='event+select',
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='rgba(0,0,0,0.2)',
            borderwidth=1
        )
    )
    
    # Create statistics panel
    filter_info = ""
    if species_filter or site_filter or description_filter:
        filter_parts = []
        if species_filter:
            filter_parts.append(f"Species: {', '.join(species_filter)}")
        if site_filter:
            filter_parts.append(f"Sites: {', '.join(site_filter)}")
        if description_filter:
            filter_parts.append(f"Desc: {', '.join(description_filter)}")
        filter_info = f" ({' | '.join(filter_parts)})"
    
    stats_panel = html.Div([
        html.H5(f"📊 Statistics{filter_info}", style={'marginBottom': '10px', 'color': '#495057'}),
        html.Div([
            html.Span(f"Mean: ", style={'fontWeight': 'bold'}),
            html.Span(f"{y_mean:.4f}", style={'color': 'green', 'fontWeight': 'bold', 'fontSize': '16px'}),
            html.Span(" | ", style={'margin': '0 10px', 'color': '#6c757d'}),
            html.Span(f"Std: ", style={'fontWeight': 'bold'}),
            html.Span(f"{y_std:.4f}", style={'color': '#007bff'}),
            html.Span(" | ", style={'margin': '0 10px', 'color': '#6c757d'}),
            html.Span(f"Range: ", style={'fontWeight': 'bold'}),
            html.Span(f"{y_min:.3f} - {y_max:.3f}", style={'color': '#6f42c1'}),
            html.Span(" | ", style={'margin': '0 10px', 'color': '#6c757d'}),
            html.Span(f"Filtered: ", style={'fontWeight': 'bold'}),
            html.Span(f"{len(filtered_df)}/{len(df)}", style={'color': '#dc3545', 'fontWeight': 'bold', 'fontSize': '16px'}),
        ])
    ])
    
    return fig, status_message, stats_panel

@app.callback(
    [Output('selected-point', 'children'),
     Output('new-x-value', 'value'),
     Output('new-y-value', 'value')],
    [Input('interactive-plot', 'clickData'),
     Input('remove-point-btn', 'n_clicks'),
     Input('x-minus-btn', 'n_clicks'),
     Input('x-plus-btn', 'n_clicks'),
     Input('y-minus-btn', 'n_clicks'),
     Input('y-plus-btn', 'n_clicks')],
    [State('x-column', 'value'),
     State('y-column', 'value'),
     State('selected-point', 'children'),
     State('step-size', 'value')]
)
def select_point(clickData, remove_clicks, x_minus_clicks, x_plus_clicks, y_minus_clicks, y_plus_clicks, x_col, y_col, selected_point, step_size):
    ctx = callback_context
    
    # If remove button was clicked, clear selection
    if ctx.triggered and 'remove-point-btn' in ctx.triggered[0]['prop_id']:
        return "None", None, None
    
    # Handle fine-tuning buttons - update the input values to reflect changes
    if ctx.triggered and selected_point != "None" and data_store['df'] is not None:
        trigger_id = ctx.triggered[0]['prop_id']
        if any(btn in trigger_id for btn in ['x-minus-btn', 'x-plus-btn', 'y-minus-btn', 'y-plus-btn']):
            try:
                point_idx = int(selected_point)
                df = data_store['df']
                
                # Get updated values after button press
                current_x = df.iloc[point_idx][data_store['x_col']]
                current_y = df.iloc[point_idx][data_store['y_col']]
                
                return selected_point, current_x, current_y
            except:
                pass
    
    if clickData is None or data_store['df'] is None:
        return "None", None, None
    
    # Get the clicked point - check if it's from the editable points trace
    clicked_point = clickData['points'][0]
    
    # Only handle clicks on the editable points trace (red circles)
    if 'customdata' not in clicked_point:
        return "None", None, None
        
    point_idx = clicked_point['customdata']
    df = data_store['df']
    
    # Check if point index is still valid (in case points were removed)
    if point_idx >= len(df):
        return "None", None, None
    
    # Get current values
    current_x = df.iloc[point_idx][x_col] if x_col else None
    current_y = df.iloc[point_idx][y_col] if y_col else None
    
    return str(point_idx), current_x, current_y

@app.callback(
    [Output('add-point-status', 'children'),
     Output('add-x-value', 'value'),
     Output('add-y-value', 'value')],
    [Input('add-point-btn', 'n_clicks')],
    [State('add-x-value', 'value'),
     State('add-y-value', 'value')],
    prevent_initial_call=True
)
def clear_add_inputs(n_clicks, add_x, add_y):
    if add_x is not None and add_y is not None:
        return f"✅ Point ({add_x}, {add_y}) added successfully!", None, None
    return "⚠️ Please enter both X and Y values", None, None

@app.callback(
    Output('data-table', 'children'),
    [Input('data-store', 'children'),
     Input('update-point-btn', 'n_clicks'),
     Input('add-point-btn', 'n_clicks'),
     Input('remove-point-btn', 'n_clicks'),
     Input('x-minus-btn', 'n_clicks'),
     Input('x-plus-btn', 'n_clicks'),
     Input('y-minus-btn', 'n_clicks'),
     Input('y-plus-btn', 'n_clicks'),
     Input('species-filter', 'value'),
     Input('site-filter', 'value'),
     Input('description-filter', 'value')]
)
def update_table(data, update_clicks, add_clicks, remove_clicks, x_minus_clicks, x_plus_clicks, y_minus_clicks, y_plus_clicks, species_filter, site_filter, description_filter):
    if data_store['df'] is None:
        return ""
    
    df = data_store['df']
    
    # Apply filters to table display
    filtered_df = apply_filters(df, species_filter, site_filter, description_filter)
    
    # Show more data for better preview
    display_rows = min(20, len(filtered_df))
    
    table_title = f"Data Preview (Showing {display_rows} of {len(filtered_df)} filtered rows"
    if len(filtered_df) < len(df):
        table_title += f" from {len(df)} total)"
    else:
        table_title += ")"
    
    return html.Div([
        html.H5(table_title, style={'marginBottom': 10}),
        dash_table.DataTable(
            data=filtered_df.head(20).to_dict('records'),
            columns=[{"name": i, "id": i} for i in filtered_df.columns],
            style_cell={'textAlign': 'left', 'fontSize': 11, 'padding': '4px'},
            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold', 'fontSize': 12},
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            page_size=20
        )
    ])

@app.callback(
    Output("download-data", "data"), 
    [Input("download-btn", "n_clicks")],
    prevent_initial_call=True,
)

def download_data(n_clicks):
    if data_store['df'] is not None:
        return dcc.send_data_frame(data_store['df'].to_csv, "modified_data.DOY", sep='\t', index=False)

@app.callback(
    [Output('upload-status', 'children', allow_duplicate=True),
     Output('interactive-plot', 'figure', allow_duplicate=True)],
    [Input('reset-btn', 'n_clicks')],
    prevent_initial_call=True
)

def reset_data(n_clicks):
    if data_store['original_df'] is not None:
        data_store['df'] = data_store['original_df'].copy()
        return "Data reset to original values", {}
    return "No original data to reset", {}
app.clientside_callback(
    """
    function(n_intervals) {
        document.addEventListener('keydown', function(event) {
            if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA') {
                return;
            }
            
            if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(event.key)) {
                event.preventDefault();
                
                let buttonId = '';
                switch(event.key) {
                    case 'ArrowLeft': buttonId = 'x-minus-btn'; break;
                    case 'ArrowRight': buttonId = 'x-plus-btn'; break;
                    case 'ArrowDown': buttonId = 'y-minus-btn'; break;
                    case 'ArrowUp': buttonId = 'y-plus-btn'; break;
                }
                
                const button = document.getElementById(buttonId);
                if (button) button.click();
            }
        });
        return '';
    }
    """,
    Output('keyboard-listener', 'children'),
    Input('keyboard-listener', 'id')
)

if __name__ == '__main__':
    print("Starting FM-Trace Data Editor...")
    print("Open your browser and go to: http://127.0.0.1:8050")
    print("📅 NEW: Phenological date markers + Species filtering + Precision editing")
    print("🎯 Add vertical markers for important dates • Filter species • Edit precisely")
    app.run(debug=True, port=8050)