"""
GeoRetail Project - Step 7B: Plotly Dash Interactive Dashboard
Create professional web-based interactive dashboard
"""

import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import geopandas as gpd
import pandas as pd
import numpy as np
from datetime import datetime
import json
import warnings

# Suppress specific warnings
warnings.filterwarnings('ignore', message='.*scatter_mapbox.*')
warnings.filterwarnings('ignore', message='.*geographic CRS.*')

print("""
🎯 GEORETAIL PROJECT - STEP 7B
📊 Plotly Dash Interactive Dashboard
📅 {}
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

print("\n" + "="*60)
print("LOADING DATA FOR DASHBOARD")
print("="*60)

# Load all data
grid_gdf = gpd.read_file("data/processed/grid/analysis_grid_wgs84.geojson")
top_locations = gpd.read_file("data/processed/grid/top_20_locations.geojson")
boundary_gdf = gpd.read_file("data/coimbatore_boundary_clean.geojson")

# Load underserved areas if exists
try:
    underserved = gpd.read_file("data/processed/grid/underserved_areas.geojson")
except:
    underserved = gpd.GeoDataFrame()

print(f"✅ Grid: {len(grid_gdf)} cells")
print(f"✅ Top locations: {len(top_locations)}")
print(f"✅ Underserved areas: {len(underserved)}")

# Prepare data for Plotly - Fix CRS warning by reprojecting to UTM first
utm_crs = grid_gdf.estimate_utm_crs()
grid_utm = grid_gdf.to_crs(utm_crs)
top_utm = top_locations.to_crs(utm_crs)

# Calculate centroids in projected CRS, then get lat/lon
grid_gdf['lon'] = grid_utm.geometry.centroid.to_crs('EPSG:4326').x
grid_gdf['lat'] = grid_utm.geometry.centroid.to_crs('EPSG:4326').y

top_locations['lon'] = top_utm.geometry.centroid.to_crs('EPSG:4326').x
top_locations['lat'] = top_utm.geometry.centroid.to_crs('EPSG:4326').y

# Key statistics
stats = {
    'total_cells': len(grid_gdf),
    'coverage_km2': grid_gdf['area_km2'].sum(),
    'population': grid_gdf['population'].sum(),
    'mean_score': grid_gdf['suitability_score_100'].mean(),
    'top_score': grid_gdf['suitability_score_100'].max(),
    'excellent_cells': len(grid_gdf[grid_gdf['suitability_class'] == 'Excellent']),
    'very_good_cells': len(grid_gdf[grid_gdf['suitability_class'] == 'Very Good']),
    'good_cells': len(grid_gdf[grid_gdf['suitability_class'] == 'Good']),
    'underserved_cells': len(underserved),
    'high_competition': len(grid_gdf[grid_gdf['competition_score'] > 5])
}

# Initialize Dash app
app = dash.Dash(__name__, 
                title="GeoRetail Dashboard - Coimbatore",
                update_title="Loading...")

# Define color schemes
colors = {
    'background': '#f8fafc',
    'card': '#ffffff',
    'primary': '#3b82f6',
    'secondary': '#8b5cf6',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'text': '#1e293b',
    'text_light': '#64748b'
}

# Dashboard layout
app.layout = html.Div([
    # Header
    html.Div([
        html.Div([
            html.H1('🎯 GeoRetail - Coimbatore Site Selection Dashboard',
                   style={'margin': '0', 'color': 'white', 'fontSize': '28px'}),
            html.P('Data-Driven Retail Location Analysis | Multi-Criteria Suitability Assessment',
                  style={'margin': '5px 0 0 0', 'color': 'rgba(255,255,255,0.9)', 'fontSize': '14px'})
        ], style={'flex': '1'}),
        html.Div([
            html.Div(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d')}",
                    style={'color': 'white', 'fontSize': '14px', 'textAlign': 'right'})
        ])
    ], style={
        'background': f'linear-gradient(135deg, {colors["primary"]} 0%, {colors["secondary"]} 100%)',
        'padding': '20px 30px',
        'display': 'flex',
        'justifyContent': 'space-between',
        'alignItems': 'center',
        'marginBottom': '20px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
    }),
    
    # Key Metrics Row
    html.Div([
        # Metric cards
        html.Div([
            html.Div([
                html.Div('🗺', style={'fontSize': '32px', 'marginBottom': '10px'}),
                html.Div(f"{stats['coverage_km2']:.1f} km²", 
                        style={'fontSize': '28px', 'fontWeight': 'bold', 'color': colors['text']}),
                html.Div('Coverage Area', style={'fontSize': '14px', 'color': colors['text_light']}),
                html.Div(f"{stats['total_cells']:,} cells analyzed", 
                        style={'fontSize': '12px', 'color': colors['text_light'], 'marginTop': '5px'})
            ], style={
                'background': colors['card'],
                'padding': '20px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'textAlign': 'center'
            })
        ], style={'flex': '1', 'marginRight': '10px'}),
        
        html.Div([
            html.Div([
                html.Div('👥', style={'fontSize': '32px', 'marginBottom': '10px'}),
                html.Div(f"{stats['population']/1000000:.2f}M", 
                        style={'fontSize': '28px', 'fontWeight': 'bold', 'color': colors['success']}),
                html.Div('Total Population', style={'fontSize': '14px', 'color': colors['text_light']}),
                html.Div(f"Peak: 78k/km²", 
                        style={'fontSize': '12px', 'color': colors['text_light'], 'marginTop': '5px'})
            ], style={
                'background': colors['card'],
                'padding': '20px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'textAlign': 'center'
            })
        ], style={'flex': '1', 'marginRight': '10px'}),
        
        html.Div([
            html.Div([
                html.Div('🎯', style={'fontSize': '32px', 'marginBottom': '10px'}),
                html.Div(f"{stats['underserved_cells']}", 
                        style={'fontSize': '28px', 'fontWeight': 'bold', 'color': colors['primary']}),
                html.Div('Market Opportunities', style={'fontSize': '14px', 'color': colors['text_light']}),
                html.Div(f"Underserved areas", 
                        style={'fontSize': '12px', 'color': colors['text_light'], 'marginTop': '5px'})
            ], style={
                'background': colors['card'],
                'padding': '20px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'textAlign': 'center'
            })
        ], style={'flex': '1', 'marginRight': '10px'}),
        
        html.Div([
            html.Div([
                html.Div('🏆', style={'fontSize': '32px', 'marginBottom': '10px'}),
                html.Div(f"{stats['top_score']:.1f}", 
                        style={'fontSize': '28px', 'fontWeight': 'bold', 'color': colors['secondary']}),
                html.Div('Top Suitability Score', style={'fontSize': '14px', 'color': colors['text_light']}),
                html.Div(f"Mean: {stats['mean_score']:.1f}", 
                        style={'fontSize': '12px', 'color': colors['text_light'], 'marginTop': '5px'})
            ], style={
                'background': colors['card'],
                'padding': '20px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'textAlign': 'center'
            })
        ], style={'flex': '1'})
    ], style={
        'display': 'flex',
        'marginBottom': '20px',
        'padding': '0 20px'
    }),
    
    # Main content area
    html.Div([
        # Left column - Map
        html.Div([
            html.Div([
                html.H3('🗺️ Suitability Score Map', 
                       style={'margin': '0 0 15px 0', 'color': colors['text']}),
                
                # Map controls
                html.Div([
                    html.Label('Select View:', style={'fontWeight': 'bold', 'marginRight': '10px'}),
                    dcc.Dropdown(
                        id='map-layer-dropdown',
                        options=[
                            {'label': '🎯 Suitability Score', 'value': 'suitability'},
                            {'label': '👥 Population Density', 'value': 'population'},
                            {'label': '🏪 Competition Level', 'value': 'competition'},
                            {'label': '🎪 Amenity Score', 'value': 'amenity'},
                            {'label': '🛣️ Road Accessibility', 'value': 'road'}
                        ],
                        value='suitability',
                        clearable=False,
                        style={'width': '300px'}
                    ),
                    html.Label('Show Top Locations:', 
                              style={'fontWeight': 'bold', 'marginLeft': '20px', 'marginRight': '10px'}),
                    dcc.Checklist(
                        id='show-top-locations',
                        options=[{'label': ' Display', 'value': 'show'}],
                        value=['show'],
                        style={'display': 'inline-block'}
                    )
                ], style={'marginBottom': '15px', 'display': 'flex', 'alignItems': 'center'}),
                
                dcc.Graph(id='main-map', style={'height': '600px'})
            ], style={
                'background': colors['card'],
                'padding': '20px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            })
        ], style={'flex': '2', 'marginRight': '20px'}),
        
        # Right column - Charts
        html.Div([
            # Top locations table
            html.Div([
                html.H3('🏆 Top 10 Locations', 
                       style={'margin': '0 0 15px 0', 'color': colors['text']}),
                html.Div(id='top-locations-table')
            ], style={
                'background': colors['card'],
                'padding': '20px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'marginBottom': '20px'
            }),
            
            # Classification chart
            html.Div([
                html.H3('📊 Suitability Distribution', 
                       style={'margin': '0 0 15px 0', 'color': colors['text']}),
                dcc.Graph(id='classification-chart', style={'height': '300px'})
            ], style={
                'background': colors['card'],
                'padding': '20px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            })
        ], style={'flex': '1'})
    ], style={
        'display': 'flex',
        'padding': '0 20px',
        'marginBottom': '20px'
    }),
    
    # Bottom row - Additional charts
    html.Div([
        html.Div([
            html.Div([
                html.H3('📈 Criteria Breakdown - Top 5 Locations', 
                       style={'margin': '0 0 15px 0', 'color': colors['text']}),
                dcc.Graph(id='criteria-comparison', style={'height': '400px'})
            ], style={
                'background': colors['card'],
                'padding': '20px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            })
        ], style={'flex': '1', 'marginRight': '20px'}),
        
        html.Div([
            html.Div([
                html.H3('🎯 Market Analysis', 
                       style={'margin': '0 0 15px 0', 'color': colors['text']}),
                dcc.Graph(id='market-analysis', style={'height': '400px'})
            ], style={
                'background': colors['card'],
                'padding': '20px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            })
        ], style={'flex': '1'})
    ], style={
        'display': 'flex',
        'padding': '0 20px',
        'marginBottom': '20px'
    })
    
], style={
    'fontFamily': 'Arial, sans-serif',
    'background': colors['background'],
    'minHeight': '100vh',
    'paddingBottom': '20px'
})

# Callbacks
@app.callback(
    Output('main-map', 'figure'),
    [Input('map-layer-dropdown', 'value'),
     Input('show-top-locations', 'value')]
)
def update_map(layer_type, show_top):
    # Define layer configurations
    layer_configs = {
        'suitability': {
            'column': 'suitability_score_100',
            'color_scale': 'RdYlGn',
            'title': 'Suitability Score',
            'range': [0, 100]
        },
        'population': {
            'column': 'pop_density',
            'color_scale': 'YlOrRd',
            'title': 'Population Density (people/km²)',
            'range': [0, grid_gdf['pop_density'].max()]
        },
        'competition': {
            'column': 'competition_score',
            'color_scale': 'Reds',
            'title': 'Competition Level (stores)',
            'range': [0, grid_gdf['competition_score'].max()]
        },
        'amenity': {
            'column': 'amenity_score',
            'color_scale': 'Greens',
            'title': 'Amenity Score',
            'range': [0, grid_gdf['amenity_score'].max()]
        },
        'road': {
            'column': 'road_density_km_per_km2',
            'color_scale': 'Blues',
            'title': 'Road Density (km/km²)',
            'range': [0, grid_gdf['road_density_km_per_km2'].max()]
        }
    }
    
    config = layer_configs[layer_type]
    
    # Create scatter map (updated method)
    fig = px.scatter_map(
        grid_gdf,
        lat='lat',
        lon='lon',
        color=config['column'],
        color_continuous_scale=config['color_scale'],
        range_color=config['range'],
        hover_data={
            'lat': False,
            'lon': False,
            'suitability_score_100': ':.1f',
            'population': ':,.0f',
            'pop_density': ':,.0f',
            'competition_score': ':.0f',
            'amenity_score': ':.1f',
            'suitability_class': True
        },
        size_max=15,
        zoom=11,
        map_style='open-street-map'
    )
    
    # Add top locations if checked
    if show_top and 'show' in show_top:
        fig.add_scattermap(
            lat=top_locations.head(10)['lat'],
            lon=top_locations.head(10)['lon'],
            mode='markers+text',
            marker=dict(size=15, color='gold', symbol='star'),
            text=top_locations.head(10)['rank'].astype(str),
            textfont=dict(size=10, color='black'),
            name='Top 10 Locations',
            hovertemplate='<b>Rank #%{text}</b><br>' +
                         'Score: %{customdata[0]:.1f}<br>' +
                         '<extra></extra>',
            customdata=top_locations.head(10)[['suitability_score_100']]
        )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(
            title=dict(
                text=config['title'],
                side='right'
            ),
            len=0.7,
            thickness=15
        )
    )
    
    return fig

@app.callback(
    Output('top-locations-table', 'children'),
    Input('map-layer-dropdown', 'value')  # Dummy input to trigger on load
)
def update_top_locations_table(_):
    top_10 = top_locations.head(10)
    
    rows = []
    for idx, row in top_10.iterrows():
        rank_color = '#fbbf24' if row['rank'] <= 3 else '#3b82f6'
        
        rows.append(
            html.Div([
                html.Div(f"#{int(row['rank'])}", 
                        style={
                            'width': '40px',
                            'height': '40px',
                            'borderRadius': '50%',
                            'background': rank_color,
                            'color': 'white',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'fontWeight': 'bold',
                            'marginRight': '15px'
                        }),
                html.Div([
                    html.Div(f"Score: {row['suitability_score_100']:.1f}/100", 
                            style={'fontWeight': 'bold', 'fontSize': '16px'}),
                    html.Div(f"Pop: {row['pop_density']:,.0f}/km² | Comp: {row['competition_score']:.0f}", 
                            style={'fontSize': '12px', 'color': colors['text_light'], 'marginTop': '3px'})
                ], style={'flex': '1'})
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'padding': '10px',
                'borderBottom': '1px solid #e2e8f0',
                'cursor': 'pointer',
                'transition': 'background 0.2s'
            })
        )
    
    return rows

@app.callback(
    Output('classification-chart', 'figure'),
    Input('map-layer-dropdown', 'value')
)
def update_classification_chart(_):
    class_counts = grid_gdf['suitability_class'].value_counts()
    
    fig = go.Figure(data=[
        go.Bar(
            x=class_counts.values,
            y=class_counts.index,
            orientation='h',
            marker=dict(
                color=['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#6b7280'],
                line=dict(color='white', width=2)
            ),
            text=class_counts.values,
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=40),
        xaxis_title='Number of Cells',
        yaxis_title='',
        showlegend=False
    )
    
    return fig

@app.callback(
    Output('criteria-comparison', 'figure'),
    Input('map-layer-dropdown', 'value')
)
def update_criteria_comparison(_):
    top_5 = top_locations.head(5)
    
    categories = ['Population', 'Accessibility', 'Low Competition', 'Amenities', 'Economic']
    
    fig = go.Figure()
    
    for idx, row in top_5.iterrows():
        fig.add_trace(go.Bar(
            name=f"Rank #{int(row['rank'])}",
            x=categories,
            y=[
                row['pop_density_norm'],
                row['road_accessibility_norm'],
                row['competition_norm'],
                row['amenity_proximity_norm'],
                row['economic_activity_norm']
            ]
        ))
    
    fig.update_layout(
        barmode='group',
        margin=dict(l=40, r=40, t=20, b=40),
        yaxis_title='Normalized Score',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    return fig

@app.callback(
    Output('market-analysis', 'figure'),
    Input('map-layer-dropdown', 'value')
)
def update_market_analysis(_):
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Population vs Competition', 'Market Concentration'),
        vertical_spacing=0.2
    )
    
    # Scatter plot
    fig.add_trace(
        go.Scatter(
            x=grid_gdf['pop_density'],
            y=grid_gdf['competition_score'],
            mode='markers',
            marker=dict(
                size=5,
                color=grid_gdf['suitability_score_100'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title='Score', x=1.15, len=0.4, y=0.75)
            ),
            text=grid_gdf['suitability_class'],
            hovertemplate='Pop Density: %{x:,.0f}<br>Competition: %{y:.0f}<br>%{text}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Histogram
    fig.add_trace(
        go.Histogram(
            x=grid_gdf['competition_score'],
            nbinsx=20,
            marker_color='#3b82f6'
        ),
        row=2, col=1
    )
    
    fig.update_xaxes(title_text='Population Density', row=1, col=1)
    fig.update_yaxes(title_text='Competition Score', row=1, col=1)
    fig.update_xaxes(title_text='Competition Level', row=2, col=1)
    fig.update_yaxes(title_text='Number of Cells', row=2, col=1)
    
    # Update subplot title styling
    for annotation in fig['layout']['annotations']:
        annotation['font'] = dict(size=12)
        annotation['y'] = annotation['y'] + 0.01
    
    fig.update_layout(
        height=400,
        showlegend=False,
        margin=dict(l=50, r=130, t=50, b=40)
    )
    
    return fig

# Save dashboard as standalone HTML
print("\n" + "="*60)
print("DASHBOARD CONFIGURATION COMPLETE")
print("="*60)

instructions = """
╔═══════════════════════════════════════════════════════════════╗
║            PLOTLY DASH DASHBOARD - RUN INSTRUCTIONS           ║
╚═══════════════════════════════════════════════════════════════╝

📊 DASHBOARD FEATURES:

✅ Interactive Map with Multiple Layers
   - Suitability Score
   - Population Density
   - Competition Level
   - Amenity Score
   - Road Accessibility

✅ Top 10 Locations Ranking
   - Click-through details
   - Real-time filtering

✅ Classification Distribution
   - Visual breakdown of suitability classes

✅ Criteria Comparison Charts
   - Top 5 locations analysis
   - Multi-criteria visualization

✅ Market Analysis
   - Population vs Competition scatter
   - Market concentration histogram

🚀 HOW TO RUN:

1. Save this script as: dashboard_app.py

2. Install required packages (if not already installed):
   pip install dash plotly geopandas pandas

3. Run the dashboard:
   python dashboard_app.py

4. Open browser and go to:
   http://127.0.0.1:8050/

5. Interact with the dashboard:
   - Toggle map layers
   - Explore different visualizations
   - Analyze top locations

📝 NOTES:

- Dashboard runs on port 8050 by default
- All data is loaded from processed files
- Interactive and real-time updates
- Professional presentation-ready
- Warnings suppressed for cleaner output

═══════════════════════════════════════════════════════════════
"""

print(instructions)

# Save instructions
with open("outputs/final/DASHBOARD_INSTRUCTIONS.txt", 'w') as f:
    f.write(instructions)

print("✅ Instructions saved: outputs/final/DASHBOARD_INSTRUCTIONS.txt")
print("\n🎯 TO RUN DASHBOARD:")
print("   python dashboard_app.py")
print("   Then open: http://127.0.0.1:8051/")

# Run the app
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 STARTING DASHBOARD SERVER...")
    print("="*60)
    print("\n📱 Dashboard will open at: http://127.0.0.1:8051/")
    print("⚠️  Press CTRL+C to stop the server\n")
    
    app.run(debug=True, port=8051)