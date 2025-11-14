"""
GeoRetail Project - Step 7: Interactive Folium Map
Create interactive HTML map with all analysis results
"""

import folium
from folium import plugins
import geopandas as gpd
import pandas as pd
import branca.colormap as cm
from datetime import datetime
import json
import os

print("""
🎯 GEORETAIL PROJECT - STEP 7
🗺️  Interactive Folium Map Creation
📅 {}
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

# Create output directory
os.makedirs("outputs/final/maps", exist_ok=True)

# Helper: Convert all datetime columns in a GeoDataFrame to string
def convert_datetime_columns_to_str(gdf):
    for col in gdf.columns:
        if pd.api.types.is_datetime64_any_dtype(gdf[col]):
            gdf[col] = gdf[col].astype(str)
    return gdf

# Step 7.1: Load All Data
print("\n" + "="*60)
print("STEP 7.1: Loading Analysis Results")
print("="*60)

# Load grid with suitability scores
print("Loading analysis grid...")
grid_gdf = gpd.read_file("data/processed/grid/analysis_grid_wgs84.geojson")
grid_gdf = convert_datetime_columns_to_str(grid_gdf)
print(f"✅ Grid loaded: {len(grid_gdf)} cells")

# Load top locations
print("Loading top locations...")
top_locations = gpd.read_file("data/processed/grid/top_20_locations.geojson")
top_locations = convert_datetime_columns_to_str(top_locations)
print(f"✅ Top locations loaded: {len(top_locations)}")

# Load underserved areas
print("Loading underserved areas...")
try:
    underserved = gpd.read_file("data/processed/grid/underserved_areas.geojson")
    underserved = convert_datetime_columns_to_str(underserved)
    print(f"✅ Underserved areas loaded: {len(underserved)}")
except:
    underserved = gpd.GeoDataFrame()
    print("⚠️  No underserved areas file found")

# Load boundary
print("Loading city boundary...")
boundary_gdf = gpd.read_file("data/coimbatore_boundary_clean.geojson")
boundary_gdf = convert_datetime_columns_to_str(boundary_gdf)
print(f"✅ Boundary loaded")

# Load POI data
print("Loading POI data...")
poi_files = {
    'retail': 'data/processed/amenities/retail.geojson',
    'education': 'data/processed/amenities/education.geojson',
    'healthcare': 'data/processed/amenities/healthcare.geojson',
    'banking': 'data/processed/amenities/banking.geojson'
}

poi_data = {}
for name, file_path in poi_files.items():
    try:
        gdf = gpd.read_file(file_path)
        gdf = convert_datetime_columns_to_str(gdf)
        if len(gdf) > 0:
            poi_data[name] = gdf
            print(f"  ✅ {name}: {len(gdf)} locations")
    except:
        print(f"  ⚠️  {name}: Not found")

# Helper to get suitability score column name
def get_suitability_score(row):
    for col in ['suitability_score_100', 'suitability_score', 'score']:
        if col in row:
            return row[col]
    raise KeyError("No suitability score column found in row.")

# Step 7.2: Calculate Map Center
print("\n" + "="*60)
print("STEP 7.2: Setting Up Map")
print("="*60)

bounds = boundary_gdf.total_bounds
center_lat = (bounds[1] + bounds[3]) / 2
center_lon = (bounds[0] + bounds[2]) / 2

print(f"Map center: {center_lat:.4f}°N, {center_lon:.4f}°E")

# Create base map
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=12,
    tiles='OpenStreetMap',
    control_scale=True
)

print("✅ Base map created")

# Step 7.3: Add Suitability Score Layer
print("\n" + "="*60)
print("STEP 7.3: Adding Suitability Score Layer")
print("="*60)

# Create color scale for suitability scores
colormap = cm.LinearColormap(
    colors=['#d73027', '#fee08b', '#d9ef8b', '#66bd63', '#1a9850'],
    vmin=0,
    vmax=100,
    caption='Suitability Score (0-100)'
)

# Add suitability layer
suitability_layer = folium.FeatureGroup(name='🎯 Suitability Score', show=True)

for idx, row in grid_gdf.iterrows():
    try:
        score = get_suitability_score(row)
    except KeyError:
        print(f"⚠️  No suitability score found for cell {row.get('cell_id', idx)}. Skipping.")
        continue
    
    # Create detailed popup
    popup_html = f"""
    <div style="font-family: Arial; width: 300px;">
        <h4 style="margin-bottom: 10px; color: #1e40af; border-bottom: 2px solid #3b82f6; padding-bottom: 5px;">
            Cell #{row['cell_id']}
        </h4>
        
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 10px; border-radius: 5px; margin: 10px 0;">
            <div style="font-size: 24px; font-weight: bold;">{score:.1f}/100</div>
            <div style="font-size: 12px; opacity: 0.9;">{row.get('suitability_class', 'N/A')}</div>
        </div>
        
        <table style="width: 100%; font-size: 12px; margin-top: 10px;">
            <tr style="background: #f3f4f6;">
                <td style="padding: 5px; font-weight: bold;">Population</td>
                <td style="padding: 5px; text-align: right;">{row['population']:,.0f}</td>
            </tr>
            <tr>
                <td style="padding: 5px; font-weight: bold;">Density</td>
                <td style="padding: 5px; text-align: right;">{row['pop_density']:,.0f} /km²</td>
            </tr>
            <tr style="background: #f3f4f6;">
                <td style="padding: 5px; font-weight: bold;">Competition</td>
                <td style="padding: 5px; text-align: right; color: {'#dc2626' if row['competition_score'] > 10 else '#16a34a'};">
                    {row['competition_score']:.0f} stores
                </td>
            </tr>
            <tr>
                <td style="padding: 5px; font-weight: bold;">Amenity Score</td>
                <td style="padding: 5px; text-align: right;">{row['amenity_score']:.1f}</td>
            </tr>
            <tr style="background: #f3f4f6;">
                <td style="padding: 5px; font-weight: bold;">Road Density</td>
                <td style="padding: 5px; text-align: right;">{row['road_density_km_per_km2']:.1f} km/km²</td>
            </tr>
            <tr>
                <td style="padding: 5px; font-weight: bold;">Highway Distance</td>
                <td style="padding: 5px; text-align: right;">{row['dist_to_major_road_m']:.0f} m</td>
            </tr>
        </table>
        
        <div style="margin-top: 10px; padding: 8px; background: #fef3c7; border-left: 3px solid #f59e0b; font-size: 11px;">
            <strong>💡 Recommendation:</strong><br>
            {'⭐ High Priority Location' if score > 60 else 
             '✅ Good Opportunity' if score > 50 else 
             '🔍 Consider for specific strategy' if score > 40 else 
             '⚠️ Lower priority area'}
        </div>
    </div>
    """
    
    # Add polygon with color based on score
    folium.GeoJson(
        row.geometry,
        style_function=lambda x, score=score: {
            'fillColor': colormap(score),
            'color': 'gray',
            'weight': 0.5,
            'fillOpacity': 0.6
        },
        popup=folium.Popup(popup_html, max_width=350),
        tooltip=f"Score: {score:.1f}"
    ).add_to(suitability_layer)

suitability_layer.add_to(m)
colormap.add_to(m)
print(f"✅ Added {len(grid_gdf)} grid cells with suitability scores")

# Step 7.4: Add Top Locations Layer
print("\n" + "="*60)
print("STEP 7.4: Adding Top 20 Locations")
print("="*60)

top_locations_layer = folium.FeatureGroup(name='🏆 Top 20 Locations', show=True)

for idx, row in top_locations.iterrows():
    centroid = row.geometry.centroid
    rank = int(row['rank'])
    
    # Medal colors for top 3
    if rank == 1:
        icon_color = 'gold'
        icon_symbol = '★'
    elif rank == 2:
        icon_color = 'silver'
        icon_symbol = '★'
    elif rank == 3:
        icon_color = 'orange'
        icon_symbol = '★'
    else:
        icon_color = 'blue'
        icon_symbol = str(rank)
    
    # Detailed popup for top locations
    try:
        score = get_suitability_score(row)
    except KeyError:
        print(f"⚠️  No suitability score found for top location rank {rank}. Skipping.")
        continue
    
    popup_html = f"""
    <div style="font-family: Arial; width: 320px;">
        <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); 
                    color: white; padding: 15px; border-radius: 5px 5px 0 0; text-align: center;">
            <div style="font-size: 36px; font-weight: bold;">#{rank}</div>
            <div style="font-size: 14px; opacity: 0.9;">TOP RECOMMENDED LOCATION</div>
        </div>
        
        <div style="padding: 15px; background: white;">
            <div style="background: #e0f2fe; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                <div style="font-size: 28px; font-weight: bold; color: #0369a1;">{score:.1f}/100</div>
                <div style="font-size: 12px; color: #0c4a6e;">{row.get('suitability_class', 'N/A')}</div>
            </div>
            
            <table style="width: 100%; font-size: 13px;">
                <tr style="background: #f9fafb;">
                    <td style="padding: 8px; font-weight: bold;">🏘️ Population</td>
                    <td style="padding: 8px, text-align: right;">{row['population']:,.0f}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">📊 Density</td>
                    <td style="padding: 8px; text-align: right; font-weight: bold; color: #16a34a;">
                        {row['pop_density']:,.0f} /km²
                    </td>
                </tr>
                <tr style="background: #f9fafb;">
                    <td style="padding: 8px; font-weight: bold;">🏪 Competition</td>
                    <td style="padding: 8px; text-align: right;">
                        <span style="color: {'#dc2626' if row['competition_score'] > 20 else '#16a34a'}; font-weight: bold;">
                            {row['competition_score']:.0f}
                        </span> stores
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">🎯 Amenities</td>
                    <td style="padding: 8px; text-align: right;">{row['amenity_score']:.1f}</td>
                </tr>
            </table>
            
            <div style="margin-top: 15px; padding: 12px; background: #dcfce7; 
                        border-left: 4px solid #16a34a; border-radius: 3px;">
                <div style="font-weight: bold; color: #166534; margin-bottom: 5px;">✅ WHY THIS LOCATION?</div>
                <ul style="margin: 5px 0; padding-left: 20px; font-size: 12px; color: #166534;">
                    <li>{'Extremely high' if row['pop_density'] > 60000 else 'High'} population density</li>
                    <li>{'Zero' if row['competition_score'] == 0 else 'Low' if row['competition_score'] < 10 else 'Moderate'} competition</li>
                    <li>{'Strong' if row['amenity_score'] > 10 else 'Good'} foot traffic potential</li>
                </ul>
            </div>
            
            <div style="margin-top: 10px; padding: 10px; background: #fef3c7; 
                        border-radius: 3px; text-align: center;">
                <div style="font-weight: bold; color: #92400e; font-size: 13px;">
                    {'🚀 IMMEDIATE PRIORITY' if rank <= 5 else '⭐ STRONG CANDIDATE'}
                </div>
            </div>
        </div>
    </div>
    """
    
    # Add marker
    folium.Marker(
        location=[centroid.y, centroid.x],
        popup=folium.Popup(popup_html, max_width=350),
        icon=folium.DivIcon(html=f"""
            <div style="
                font-size: 16px; 
                font-weight: bold; 
                color: white; 
                background: {'linear-gradient(135deg, #fbbf24, #f59e0b)' if rank <= 3 else 'linear-gradient(135deg, #3b82f6, #1d4ed8)'};
                width: 35px; 
                height: 35px; 
                border-radius: 50%; 
                display: flex; 
                align-items: center; 
                justify-content: center;
                border: 3px solid white;
                box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            ">
                {rank}
            </div>
        """),
        tooltip=f"Rank #{rank} - Score: {score:.1f}"
    ).add_to(top_locations_layer)

top_locations_layer.add_to(m)
print(f"✅ Added {len(top_locations)} top location markers")

# Step 7.5: Add Underserved Areas Layer
if len(underserved) > 0:
    print("\n" + "="*60)
    print("STEP 7.5: Adding Underserved Areas")
    print("="*60)
    
    underserved_layer = folium.FeatureGroup(name='🎯 Underserved Markets', show=False)
    
    for idx, row in underserved.iterrows():
        popup_html = f"""
        <div style="font-family: Arial; width: 280px;">
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                        color: white; padding: 10px; border-radius: 5px 5px 0 0;">
                <h4 style="margin: 0;">🎯 Market Opportunity</h4>
            </div>
            <div style="padding: 10px; background: white;">
                <table style="width: 100%; font-size: 12px;">
                    <tr style="background: #f3f4f6;">
                        <td style="padding: 5px;">Population</td>
                        <td style="padding: 5px; text-align: right; font-weight: bold;">{row['population']:,.0f}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;">Competition</td>
                        <td style="padding: 5px; text-align: right; color: #16a34a; font-weight: bold;">
                            {row['competition_score']:.0f} (LOW!)
                        </td>
                    </tr>
                    <tr style="background: #f3f4f6;">
                        <td style="padding: 5px;">Market Gap Score</td>
                        <td style="padding: 5px; text-align: right; font-weight: bold;">{row['market_gap_score']:.1f}</td>
                    </tr>
                </table>
                <div style="margin-top: 10px; padding: 8px; background: #d1fae5; 
                            border-left: 3px solid #10b981; font-size: 11px;">
                    <strong>💡 Opportunity:</strong> Underserved area with good population but minimal competition
                </div>
            </div>
        </div>
        """
        
        folium.GeoJson(
            row.geometry,
            style_function=lambda x: {
                'fillColor': '#10b981',
                'color': '#059669',
                'weight': 2,
                'fillOpacity': 0.5
            },
            popup=folium.Popup(popup_html, max_width=300),
            tooltip="Underserved Market"
        ).add_to(underserved_layer)
    
    underserved_layer.add_to(m)
    print(f"✅ Added {len(underserved)} underserved areas")

# Step 7.6: Add POI Layers
print("\n" + "="*60)
print("STEP 7.6: Adding POI Layers")
print("="*60)

poi_configs = {
    'retail': {'color': 'red', 'icon': 'shopping-cart', 'name': '🏪 Retail (Competition)'},
    'education': {'color': 'blue', 'icon': 'graduation-cap', 'name': '🏫 Education'},
    'healthcare': {'color': 'green', 'icon': 'plus', 'name': '🏥 Healthcare'},
    'banking': {'color': 'orange', 'icon': 'dollar', 'name': '🏦 Banking'}
}

for poi_type, config in poi_configs.items():
    if poi_type in poi_data:
        poi_layer = folium.FeatureGroup(name=config['name'], show=False)
        
        # Sample POIs if too many (for performance)
        poi_gdf = poi_data[poi_type]
        if len(poi_gdf) > 100:
            poi_gdf = poi_gdf.sample(n=100)
        
        for idx, row in poi_gdf.iterrows():
            popup_text = f"""
            <div style="font-family: Arial;">
                <h4 style="color: {config['color']};">{config['name']}</h4>
                <p style="font-size: 12px;">
                    Type: {poi_type.title()}<br>
                    Category: {config['name']}
                </p>
            </div>
            """
            
            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x],
                radius=4,
                popup=folium.Popup(popup_text, max_width=200),
                color=config['color'],
                fill=True,
                fillColor=config['color'],
                fillOpacity=0.7,
                tooltip=poi_type.title()
            ).add_to(poi_layer)
        
        poi_layer.add_to(m)
        print(f"  ✅ {poi_type}: {len(poi_gdf)} locations")

# Step 7.7: Add City Boundary
print("\n" + "="*60)
print("STEP 7.7: Adding City Boundary")
print("="*60)

folium.GeoJson(
    boundary_gdf,
    name='City Boundary',
    style_function=lambda x: {
        'fillColor': 'none',
        'color': 'black',
        'weight': 3,
        'dashArray': '5, 5'
    },
    tooltip="Coimbatore Municipal Corporation"
).add_to(m)

print("✅ City boundary added")

# Step 7.8: Add Additional Controls
print("\n" + "="*60)
print("STEP 7.8: Adding Map Controls")
print("="*60)

# Add layer control
folium.LayerControl(position='topright', collapsed=False).add_to(m)

# Add fullscreen button
plugins.Fullscreen(position='topleft').add_to(m)

# Add measure control
plugins.MeasureControl(position='bottomleft', primary_length_unit='kilometers').add_to(m)

# Add minimap
minimap = plugins.MiniMap(toggle_display=True)
m.add_child(minimap)

# Add title
title_html = '''
<div style="position: fixed; 
            top: 10px; 
            left: 50px; 
            width: 400px; 
            height: auto; 
            background-color: white; 
            border: 2px solid #3b82f6;
            border-radius: 8px;
            z-index: 9999; 
            font-family: Arial;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    <div style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); 
                color: white; 
                padding: 12px; 
                border-radius: 6px 6px 0 0;">
        <h3 style="margin: 0; font-size: 18px;">🎯 GeoRetail - Coimbatore</h3>
        <p style="margin: 5px 0 0 0; font-size: 12px; opacity: 0.9;">
            Retail Site Suitability Analysis
        </p>
    </div>
    <div style="padding: 10px; font-size: 11px; color: #374151;">
        <div style="margin-bottom: 5px;">
            <strong>📊 Analysis Coverage:</strong> 1,802 cells | 470 km²
        </div>
        <div style="margin-bottom: 5px;">
            <strong>👥 Population:</strong> 1.58M | <strong>🏆 Top Score:</strong> 65.6/100
        </div>
        <div style="background: #fef3c7; padding: 5px; border-radius: 3px; margin-top: 8px;">
            <strong>💡 Tip:</strong> Click on grid cells or markers for details
        </div>
    </div>
</div>
'''
m.get_root().html.add_child(folium.Element(title_html))

print("✅ Map controls added")

# Step 7.9: Save Map
print("\n" + "="*60)
print("STEP 7.9: Saving Interactive Map")
print("="*60)

output_file = "outputs/final/maps/georetail_interactive_map.html"
m.save(output_file)

print(f"✅ Interactive map saved: {output_file}")

# Get file size
file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
print(f"   File size: {file_size:.2f} MB")

# Step 7.10: Create Summary
print("\n" + "="*60)
print("STEP 7.10: Map Summary")
print("="*60)

summary = f"""
╔═══════════════════════════════════════════════════════════════╗
║          INTERACTIVE MAP SUCCESSFULLY CREATED!                ║
╚═══════════════════════════════════════════════════════════════╝

📁 File Location: {output_file}
💾 File Size: {file_size:.2f} MB

🗺️  MAP LAYERS INCLUDED:

✅ Suitability Score Grid
   - {len(grid_gdf):,} grid cells with interactive popups
   - Color-coded by suitability score (0-100)
   - Detailed metrics on click

✅ Top 20 Recommended Locations
   - Numbered markers (1-20)
   - Detailed analysis popups
   - Priority indicators

✅ Underserved Market Areas
   - {len(underserved) if len(underserved) > 0 else 0} opportunity zones
   - Low competition highlights
   - Market gap scores

✅ Points of Interest (POI)
   - Retail locations (competition)
   - Education facilities
   - Healthcare centers
   - Banking locations

✅ City Boundary
   - Coimbatore Municipal Corporation limits

🎮 INTERACTIVE FEATURES:

• Layer Control: Toggle layers on/off
• Fullscreen Mode: Expand to full screen
• Measure Tool: Measure distances
• Mini Map: Overview navigation
• Popups: Click for detailed information
• Tooltips: Hover for quick info

📖 HOW TO USE:

1. Open the HTML file in any web browser
2. Click on grid cells to see suitability details
3. Click on numbered markers for top location analysis
4. Use layer control to show/hide different data
5. Zoom and pan to explore different areas
6. Use measure tool to check distances

💡 RECOMMENDED WORKFLOW:

Step 1: View overall suitability (default layer)
Step 2: Enable "Top 20 Locations" to see recommendations
Step 3: Click top 5 locations for detailed analysis
Step 4: Toggle "Underserved Markets" for expansion opportunities
Step 5: Enable POI layers to understand competition

═══════════════════════════════════════════════════════════════

🎉 YOU CAN NOW:

✅ Open the map in your browser
✅ Present to stakeholders interactively
✅ Share the HTML file (standalone, no dependencies)
✅ Explore all 1,802 analyzed locations
✅ Make data-driven site selection decisions

═══════════════════════════════════════════════════════════════
"""

print(summary)

# Save instructions
instructions_file = "outputs/final/maps/MAP_INSTRUCTIONS.txt"
with open(instructions_file, 'w') as f:
    f.write(summary)

print(f"✅ Instructions saved: {instructions_file}")

print("\n" + "="*60)
print("🎉 INTERACTIVE MAP COMPLETE!")
print("="*60)
print(f"\n📂 Open this file in your browser:")
print(f"   {output_file}")
print("\n🚀 Your GeoRetail analysis is now fully interactive!")