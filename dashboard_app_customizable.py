"""
GeoRetail Project - Customizable Dashboard for Multiple Business Types
Users can select business type and adjust criteria weights dynamically
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
from sklearn.preprocessing import MinMaxScaler
import warnings

# Suppress warnings
warnings.filterwarnings('ignore', message='.*scatter_mapbox.*')
warnings.filterwarnings('ignore', message='.*geographic CRS.*')

print("""
🎯 GEORETAIL - CUSTOMIZABLE MULTI-BUSINESS DASHBOARD
📊 Dynamic Weight Adjustment for Different Business Types
📅 {}
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

# Load data
print("Loading data...")
grid_gdf = gpd.read_file("data/processed/grid/analysis_grid_wgs84.geojson")
boundary_gdf = gpd.read_file("data/coimbatore_boundary_clean.geojson")

# Fix CRS warnings - reproject to UTM before calculating centroids
utm_crs = grid_gdf.estimate_utm_crs()
grid_utm = grid_gdf.to_crs(utm_crs)
grid_gdf['lon'] = grid_utm.geometry.centroid.to_crs('EPSG:4326').x
grid_gdf['lat'] = grid_utm.geometry.centroid.to_crs('EPSG:4326').y

print(f"✅ Data loaded: {len(grid_gdf)} cells")

# Predefined business types with optimal weights
BUSINESS_TYPES = {
    'Custom': {
        'icon': '⚙️',
        'description': 'Set your own custom weights',
        'weights': {
            'population_density': 30,
            'road_accessibility': 20,
            'competition_level': 15,
            'amenity_proximity': 20,
            'economic_activity': 15
        },
        'reasoning': 'Adjust weights based on your specific business needs'
    },
    'Grocery Store': {
        'icon': '🛒',
        'description': 'Supermarket, General Store, Convenience Store',
        'weights': {
            'population_density': 40,
            'road_accessibility': 15,
            'competition_level': 20,
            'amenity_proximity': 15,
            'economic_activity': 10
        },
        'reasoning': 'Groceries prioritize nearby population and low competition'
    },
    'Medical Store/Pharmacy': {
        'icon': '💊',
        'description': 'Pharmacy, Medical Store, Drugstore',
        'weights': {
            'population_density': 25,
            'road_accessibility': 25,
            'competition_level': 10,
            'amenity_proximity': 30,
            'economic_activity': 10
        },
        'reasoning': 'Pharmacies thrive near healthcare facilities with good access'
    },
    'Stationery Shop': {
        'icon': '📚',
        'description': 'Books, School/Office Supplies, Print Shop',
        'weights': {
            'population_density': 20,
            'road_accessibility': 15,
            'competition_level': 15,
            'amenity_proximity': 40,
            'economic_activity': 10
        },
        'reasoning': 'Stationery stores need proximity to schools and offices'
    },
    'Restaurant/Cafe': {
        'icon': '🍽️',
        'description': 'Restaurant, Cafe, Fast Food, Bakery',
        'weights': {
            'population_density': 25,
            'road_accessibility': 20,
            'competition_level': 10,
            'amenity_proximity': 35,
            'economic_activity': 10
        },
        'reasoning': 'Restaurants thrive in high foot-traffic areas with visibility'
    },
    'Fashion/Clothing Store': {
        'icon': '👕',
        'description': 'Apparel, Fashion, Shoes, Accessories',
        'weights': {
            'population_density': 20,
            'road_accessibility': 25,
            'competition_level': 5,
            'amenity_proximity': 30,
            'economic_activity': 20
        },
        'reasoning': 'Fashion stores benefit from shopping clusters and affluent areas'
    },
    'Electronics Store': {
        'icon': '📱',
        'description': 'Mobile, Computer, Electronics, Gadgets',
        'weights': {
            'population_density': 20,
            'road_accessibility': 25,
            'competition_level': 10,
            'amenity_proximity': 20,
            'economic_activity': 25
        },
        'reasoning': 'Electronics need good access and affluent customer base'
    },
    'Gym/Fitness Center': {
        'icon': '💪',
        'description': 'Gym, Fitness Studio, Yoga Center',
        'weights': {
            'population_density': 35,
            'road_accessibility': 20,
            'competition_level': 20,
            'amenity_proximity': 15,
            'economic_activity': 10
        },
        'reasoning': 'Gyms need dense population with convenient daily access'
    },
    'Beauty Salon/Spa': {
        'icon': '💇',
        'description': 'Hair Salon, Beauty Parlor, Spa',
        'weights': {
            'population_density': 30,
            'road_accessibility': 20,
            'competition_level': 15,
            'amenity_proximity': 20,
            'economic_activity': 15
        },
        'reasoning': 'Salons need good population and moderate purchasing power'
    },
    'Banking/ATM': {
        'icon': '🏦',
        'description': 'Bank Branch, ATM Location, Financial Services',
        'weights': {
            'population_density': 30,
            'road_accessibility': 30,
            'competition_level': 5,
            'amenity_proximity': 20,
            'economic_activity': 15
        },
        'reasoning': 'Banks prioritize accessibility and population coverage'
    }
}

# Color schemes
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

# Initialize Dash app
app = dash.Dash(__name__, title="GeoRetail Multi-Business Dashboard")

# Layout
app.layout = html.Div([
    # Header
    html.Div([
        html.Div([
            html.H1('🎯 GeoRetail - Customizable Business Location Finder',
                   style={'margin': '0', 'color': 'white', 'fontSize': '28px'}),
            html.P('Select Your Business Type & Find Optimal Locations',
                  style={'margin': '5px 0 0 0', 'color': 'rgba(255,255,255,0.9)', 'fontSize': '14px'})
        ])
    ], style={
        'background': f'linear-gradient(135deg, {colors["primary"]} 0%, {colors["secondary"]} 100%)',
        'padding': '20px 30px',
        'marginBottom': '20px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
    }),
    
    # Business Type Selection Row
    html.Div([
        html.Div([
            html.H3('🏪 Select Your Business Type', style={'marginBottom': '15px', 'color': colors['text']}),
            
            # Business type dropdown
            html.Label('Business Type:', style={'fontWeight': 'bold', 'marginBottom': '5px', 'display': 'block'}),
            dcc.Dropdown(
                id='business-type-dropdown',
                options=[
                    {'label': f"{info['icon']} {btype} - {info['description']}", 'value': btype}
                    for btype, info in BUSINESS_TYPES.items()
                ],
                value='Grocery Store',
                clearable=False,
                style={'marginBottom': '15px'}
            ),
            
            # Business description
            html.Div(id='business-description', style={
                'padding': '15px',
                'background': '#e0f2fe',
                'borderRadius': '8px',
                'marginBottom': '15px',
                'borderLeft': '4px solid #3b82f6'
            }),
            
            # Reasoning
            html.Div(id='business-reasoning', style={
                'padding': '12px',
                'background': '#fef3c7',
                'borderRadius': '8px',
                'fontSize': '14px',
                'borderLeft': '4px solid #f59e0b'
            })
            
        ], style={
            'background': colors['card'],
            'padding': '20px',
            'borderRadius': '8px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
        })
    ], style={'padding': '0 20px', 'marginBottom': '20px'}),
    
    # Weight Adjustment Sliders
    html.Div([
        html.Div([
            html.H3('⚖️ Adjust Criteria Weights', style={'marginBottom': '15px', 'color': colors['text']}),
            html.P('Customize the importance of each criterion for your business (Total must = 100%)',
                  style={'fontSize': '14px', 'color': colors['text_light'], 'marginBottom': '20px'}),
            
            # Population Density Slider
            html.Div([
                html.Label([
                    '👥 Population Density ',
                    html.Span(id='pop-weight-display', style={'fontWeight': 'bold', 'color': colors['primary']})
                ], style={'fontWeight': 'bold', 'marginBottom': '5px', 'display': 'block'}),
                dcc.Slider(
                    id='pop-density-slider',
                    min=0, max=50, step=5, value=30,
                    marks={i: f'{i}%' for i in range(0, 55, 10)},
                    tooltip={'placement': 'bottom', 'always_visible': False}
                )
            ], style={'marginBottom': '20px'}),
            
            # Road Accessibility Slider
            html.Div([
                html.Label([
                    '🛣️ Road Accessibility ',
                    html.Span(id='road-weight-display', style={'fontWeight': 'bold', 'color': colors['primary']})
                ], style={'fontWeight': 'bold', 'marginBottom': '5px', 'display': 'block'}),
                dcc.Slider(
                    id='road-accessibility-slider',
                    min=0, max=50, step=5, value=20,
                    marks={i: f'{i}%' for i in range(0, 55, 10)},
                    tooltip={'placement': 'bottom', 'always_visible': False}
                )
            ], style={'marginBottom': '20px'}),
            
            # Competition Level Slider
            html.Div([
                html.Label([
                    '🏪 Low Competition (inverse) ',
                    html.Span(id='comp-weight-display', style={'fontWeight': 'bold', 'color': colors['primary']})
                ], style={'fontWeight': 'bold', 'marginBottom': '5px', 'display': 'block'}),
                dcc.Slider(
                    id='competition-slider',
                    min=0, max=50, step=5, value=15,
                    marks={i: f'{i}%' for i in range(0, 55, 10)},
                    tooltip={'placement': 'bottom', 'always_visible': False}
                )
            ], style={'marginBottom': '20px'}),
            
            # Amenity Proximity Slider
            html.Div([
                html.Label([
                    '🎯 Amenity Proximity ',
                    html.Span(id='amenity-weight-display', style={'fontWeight': 'bold', 'color': colors['primary']})
                ], style={'fontWeight': 'bold', 'marginBottom': '5px', 'display': 'block'}),
                dcc.Slider(
                    id='amenity-proximity-slider',
                    min=0, max=50, step=5, value=20,
                    marks={i: f'{i}%' for i in range(0, 55, 10)},
                    tooltip={'placement': 'bottom', 'always_visible': False}
                )
            ], style={'marginBottom': '20px'}),
            
            # Economic Activity Slider
            html.Div([
                html.Label([
                    '💰 Economic Activity ',
                    html.Span(id='econ-weight-display', style={'fontWeight': 'bold', 'color': colors['primary']})
                ], style={'fontWeight': 'bold', 'marginBottom': '5px', 'display': 'block'}),
                dcc.Slider(
                    id='economic-activity-slider',
                    min=0, max=50, step=5, value=15,
                    marks={i: f'{i}%' for i in range(0, 55, 10)},
                    tooltip={'placement': 'bottom', 'always_visible': False}
                )
            ], style={'marginBottom': '20px'}),
            
            # Total Weight Display
            html.Div(id='total-weight-display', style={
                'padding': '15px',
                'background': '#dcfce7',
                'borderRadius': '8px',
                'textAlign': 'center',
                'fontSize': '18px',
                'fontWeight': 'bold',
                'marginTop': '10px'
            }),
            
            # Calculate Button
            html.Button(
                '🔄 Recalculate Suitability Scores',
                id='calculate-button',
                n_clicks=0,
                style={
                    'width': '100%',
                    'padding': '15px',
                    'marginTop': '15px',
                    'background': f'linear-gradient(135deg, {colors["success"]} 0%, #059669 100%)',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '8px',
                    'fontSize': '16px',
                    'fontWeight': 'bold',
                    'cursor': 'pointer',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                }
            )
            
        ], style={
            'background': colors['card'],
            'padding': '20px',
            'borderRadius': '8px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
        })
    ], style={'padding': '0 20px', 'marginBottom': '20px'}),
    
    # Results Section
    html.Div([
        # Map
        html.Div([
            html.Div([
                html.H3('🗺️ Location Suitability Map', style={'marginBottom': '15px', 'color': colors['text']}),
                html.Div(id='map-subtitle', style={'fontSize': '14px', 'color': colors['text_light'], 'marginBottom': '15px'}),
                dcc.Graph(id='suitability-map', style={'height': '600px'})
            ], style={
                'background': colors['card'],
                'padding': '20px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            })
        ], style={'flex': '2', 'marginRight': '20px'}),
        
        # Top Locations
        html.Div([
            html.Div([
                html.H3('🏆 Top 10 Recommended Locations', style={'marginBottom': '15px', 'color': colors['text']}),
                html.Div(id='top-locations-list')
            ], style={
                'background': colors['card'],
                'padding': '20px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'maxHeight': '600px',
                'overflowY': 'auto'
            })
        ], style={'flex': '1'})
        
    ], style={'display': 'flex', 'padding': '0 20px', 'marginBottom': '20px'}),
    
    # Statistics Row
    html.Div([
        html.Div([
            html.Div([
                html.H3('📊 Score Distribution', style={'marginBottom': '15px', 'color': colors['text']}),
                dcc.Graph(id='score-distribution', style={'height': '300px'})
            ], style={
                'background': colors['card'],
                'padding': '20px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            })
        ], style={'flex': '1', 'marginRight': '20px'}),
        
        html.Div([
            html.Div([
                html.H3('💡 Business Insights', style={'marginBottom': '15px', 'color': colors['text']}),
                html.Div(id='business-insights')
            ], style={
                'background': colors['card'],
                'padding': '20px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            })
        ], style={'flex': '1'})
        
    ], style={'display': 'flex', 'padding': '0 20px', 'marginBottom': '20px'})
    
], style={'fontFamily': 'Arial, sans-serif', 'background': colors['background'], 'minHeight': '100vh', 'paddingBottom': '20px'})

# Callbacks

# Update business description
@app.callback(
    [Output('business-description', 'children'),
     Output('business-reasoning', 'children'),
     Output('pop-density-slider', 'value'),
     Output('road-accessibility-slider', 'value'),
     Output('competition-slider', 'value'),
     Output('amenity-proximity-slider', 'value'),
     Output('economic-activity-slider', 'value')],
    Input('business-type-dropdown', 'value')
)
def update_business_info(business_type):
    info = BUSINESS_TYPES[business_type]
    weights = info['weights']
    
    description = html.Div([
        html.Strong(f"{info['icon']} {business_type}", style={'fontSize': '16px'}),
        html.Br(),
        html.Span(info['description'], style={'fontSize': '14px', 'color': colors['text_light']})
    ])
    
    reasoning = html.Div([
        html.Strong('💡 Why these weights? '),
        html.Span(info['reasoning'])
    ])
    
    return (description, reasoning, 
            weights['population_density'],
            weights['road_accessibility'],
            weights['competition_level'],
            weights['amenity_proximity'],
            weights['economic_activity'])

# Update weight displays
@app.callback(
    [Output('pop-weight-display', 'children'),
     Output('road-weight-display', 'children'),
     Output('comp-weight-display', 'children'),
     Output('amenity-weight-display', 'children'),
     Output('econ-weight-display', 'children'),
     Output('total-weight-display', 'children'),
     Output('total-weight-display', 'style')],
    [Input('pop-density-slider', 'value'),
     Input('road-accessibility-slider', 'value'),
     Input('competition-slider', 'value'),
     Input('amenity-proximity-slider', 'value'),
     Input('economic-activity-slider', 'value')]
)
def update_weight_displays(pop, road, comp, amenity, econ):
    total = pop + road + comp + amenity + econ
    
    base_style = {
        'padding': '15px',
        'borderRadius': '8px',
        'textAlign': 'center',
        'fontSize': '18px',
        'fontWeight': 'bold',
        'marginTop': '10px'
    }
    
    if total == 100:
        style = {**base_style, 'background': '#dcfce7', 'color': '#166534'}
        message = f'✅ Total: {total}% (Perfect!)'
    elif total < 100:
        style = {**base_style, 'background': '#fef3c7', 'color': '#92400e'}
        message = f'⚠️ Total: {total}% (Add {100-total}% more)'
    else:
        style = {**base_style, 'background': '#fee2e2', 'color': '#991b1b'}
        message = f'❌ Total: {total}% (Reduce by {total-100}%)'
    
    return (f'{pop}%', f'{road}%', f'{comp}%', f'{amenity}%', f'{econ}%', message, style)

# Calculate and update results
@app.callback(
    [Output('suitability-map', 'figure'),
     Output('map-subtitle', 'children'),
     Output('top-locations-list', 'children'),
     Output('score-distribution', 'figure'),
     Output('business-insights', 'children')],
    [Input('calculate-button', 'n_clicks'),
     Input('business-type-dropdown', 'value')],
    [State('pop-density-slider', 'value'),
     State('road-accessibility-slider', 'value'),
     State('competition-slider', 'value'),
     State('amenity-proximity-slider', 'value'),
     State('economic-activity-slider', 'value')]
)
def update_results(n_clicks, business_type, pop_w, road_w, comp_w, amenity_w, econ_w):
    # Calculate custom suitability scores
    grid_df = grid_gdf.copy()
    
    # Recalculate with custom weights
    weights_sum = pop_w + road_w + comp_w + amenity_w + econ_w
    
    if weights_sum != 100:
        # Normalize to 100%
        pop_w = (pop_w / weights_sum) * 100
        road_w = (road_w / weights_sum) * 100
        comp_w = (comp_w / weights_sum) * 100
        amenity_w = (amenity_w / weights_sum) * 100
        econ_w = (econ_w / weights_sum) * 100
    
    grid_df['custom_score'] = (
        (pop_w/100) * grid_df['pop_density_norm'] +
        (road_w/100) * grid_df['road_accessibility_norm'] +
        (comp_w/100) * grid_df['competition_norm'] +
        (amenity_w/100) * grid_df['amenity_proximity_norm'] +
        (econ_w/100) * grid_df['economic_activity_norm']
    ) * 100
    
    # Sort and get top locations
    top_10 = grid_df.nlargest(10, 'custom_score')
    
    # Create map using scatter_map (updated method)
    fig_map = px.scatter_map(
        grid_df,
        lat='lat',
        lon='lon',
        color='custom_score',
        color_continuous_scale='RdYlGn',
        range_color=[0, 100],
        hover_data={
            'lat': False,
            'lon': False,
            'custom_score': ':.1f',
            'population': ':,.0f',
            'competition_score': ':.0f'
        },
        size_max=15,
        zoom=11,
        map_style='open-street-map'
    )
    
    # Add top 10 markers
    fig_map.add_scattermap(
        lat=top_10['lat'],
        lon=top_10['lon'],
        mode='markers+text',
        marker=dict(size=15, color='gold', symbol='star'),
        text=[str(i+1) for i in range(len(top_10))],
        textfont=dict(size=10, color='black'),
        name='Top 10',
        hovertemplate='<b>Rank #%{text}</b><br>Score: %{customdata[0]:.1f}<extra></extra>',
        customdata=top_10[['custom_score']]
    )
    
    fig_map.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(
            title=dict(
                text='Suitability<br>Score',
                side='right'
            ),
            tickmode='linear',
            tick0=0,
            dtick=20,
            len=0.7
        )
    )
    
    # Map subtitle
    subtitle = f"Optimized for {BUSINESS_TYPES[business_type]['icon']} {business_type} | Weights: Pop {pop_w:.0f}% | Road {road_w:.0f}% | Comp {comp_w:.0f}% | Amenity {amenity_w:.0f}% | Econ {econ_w:.0f}%"
    
    # Top locations list
    locations_list = []
    for i, (idx, row) in enumerate(top_10.iterrows()):
        rank_color = '#fbbf24' if i < 3 else '#3b82f6'
        
        locations_list.append(
            html.Div([
                html.Div(f"#{i+1}", style={
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
                    html.Div(f"Score: {row['custom_score']:.1f}/100", 
                            style={'fontWeight': 'bold', 'fontSize': '16px'}),
                    html.Div(f"Pop: {row['pop_density']:,.0f}/km² | Comp: {row['competition_score']:.0f}",
                            style={'fontSize': '12px', 'color': colors['text_light']})
                ], style={'flex': '1'})
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'padding': '12px',
                'borderBottom': '1px solid #e2e8f0',
                'marginBottom': '5px'
            })
        )
    
    # Score distribution
    fig_dist = go.Figure(data=[
        go.Histogram(x=grid_df['custom_score'], nbinsx=30, marker_color='#3b82f6')
    ])
    fig_dist.update_layout(
        xaxis_title='Suitability Score',
        yaxis_title='Number of Locations',
        margin=dict(l=40, r=40, t=20, b=40),
        showlegend=False
    )
    
    # Business insights
    mean_score = grid_df['custom_score'].mean()
    high_score = len(grid_df[grid_df['custom_score'] > 60])
    zero_comp = len(grid_df[grid_df['competition_score'] == 0])
    
    insights = html.Div([
        html.Div([
            html.Div('📈 Mean Score:', style={'fontWeight': 'bold'}),
            html.Div(f'{mean_score:.1f}/100', style={'fontSize': '24px', 'color': colors['primary']})
        ], style={'marginBottom': '15px'}),
        
        html.Div([
            html.Div('⭐ High Potential Areas:', style={'fontWeight': 'bold'}),
            html.Div(f'{high_score} locations', style={'fontSize': '20px', 'color': colors['success']})
        ], style={'marginBottom': '15px'}),
        
        html.Div([
            html.Div('🎯 Zero Competition:', style={'fontWeight': 'bold'}),
            html.Div(f'{zero_comp} locations', style={'fontSize': '20px', 'color': colors['warning']})
        ], style={'marginBottom': '15px'}),
        
        html.Div([
            html.Strong('💡 Recommendation: '),
            html.Span(f"For {business_type}, focus on top {min(5, len(top_10))} locations with scores above {top_10.iloc[4]['custom_score'] if len(top_10) >= 5 else top_10.iloc[-1]['custom_score']:.1f}")
        ], style={'padding': '10px', 'background': '#fef3c7', 'borderRadius': '5px', 'fontSize': '14px'})
    ])
    
    return fig_map, subtitle, locations_list, fig_dist, insights

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 STARTING CUSTOMIZABLE DASHBOARD...")
    print("="*60)
    print("\n📱 Dashboard URL: http://127.0.0.1:8050/")
    print("⚠️  Press CTRL+C to stop\n")
    print("🎯 Features:")
    print("   • 10 predefined business types")
    print("   • Custom weight adjustment")
    print("   • Real-time recalculation")
    print("   • Interactive map & charts")
    print("\n✨ Select a business type and adjust weights!")
    
    # Updated method: use app.run() instead of app.run_server()
    app.run(debug=True, port=8050)