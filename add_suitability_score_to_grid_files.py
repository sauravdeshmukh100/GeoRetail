"""
Fix: Add suitability scores to the grid file
This should have been done at the end of Step 6
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime

print("Fixing grid file with suitability scores...")

# Load the grid
grid_gdf = gpd.read_file("data/processed/grid/analysis_grid_wgs84.geojson")
print(f"Loaded grid: {len(grid_gdf)} cells")

# Check if suitability_score_100 already exists
if 'suitability_score_100' in grid_gdf.columns:
    print("✅ Suitability scores already exist!")
else:
    print("Adding suitability scores...")
    
    # Criteria weights
    criteria_weights = {
        'population_density': 0.30,
        'road_accessibility': 0.20,
        'competition_level': 0.15,
        'amenity_proximity': 0.20,
        'economic_activity': 0.15
    }
    
    # Normalize features
    scaler = MinMaxScaler()
    
    # Population density (maximize)
    grid_gdf['pop_density_norm'] = scaler.fit_transform(
        grid_gdf[['pop_density']]
    ).flatten()
    
    # Road accessibility (composite)
    grid_gdf['road_density_norm'] = scaler.fit_transform(
        grid_gdf[['road_density_km_per_km2']]
    ).flatten()
    
    grid_gdf['highway_proximity_norm'] = 1 - scaler.fit_transform(
        grid_gdf[['dist_to_major_road_m']]
    ).flatten()
    
    grid_gdf['road_accessibility_norm'] = (
        0.6 * grid_gdf['road_density_norm'] + 
        0.4 * grid_gdf['highway_proximity_norm']
    )
    
    # Competition level (minimize - invert)
    grid_gdf['competition_norm'] = 1 - scaler.fit_transform(
        grid_gdf[['competition_score']]
    ).flatten()
    
    # Amenity proximity (maximize)
    grid_gdf['amenity_proximity_norm'] = scaler.fit_transform(
        grid_gdf[['amenity_score']]
    ).flatten()
    
    # Economic activity (maximize)
    grid_gdf['economic_activity_norm'] = scaler.fit_transform(
        grid_gdf[['banking_count_1km']]
    ).flatten()
    
    # Calculate suitability score
    grid_gdf['suitability_score'] = (
        criteria_weights['population_density'] * grid_gdf['pop_density_norm'] +
        criteria_weights['road_accessibility'] * grid_gdf['road_accessibility_norm'] +
        criteria_weights['competition_level'] * grid_gdf['competition_norm'] +
        criteria_weights['amenity_proximity'] * grid_gdf['amenity_proximity_norm'] +
        criteria_weights['economic_activity'] * grid_gdf['economic_activity_norm']
    )
    
    # Convert to 0-100 scale
    grid_gdf['suitability_score_100'] = grid_gdf['suitability_score'] * 100
    
    # Classify suitability
    def classify_suitability(score):
        if score >= 75:
            return 'Excellent'
        elif score >= 60:
            return 'Very Good'
        elif score >= 45:
            return 'Good'
        elif score >= 30:
            return 'Moderate'
        else:
            return 'Low'
    
    grid_gdf['suitability_class'] = grid_gdf['suitability_score_100'].apply(classify_suitability)
    
    # Calculate market gap score
    grid_gdf['market_gap_score'] = (
        grid_gdf['pop_density_norm'] * 0.4 +
        grid_gdf['competition_norm'] * 0.4 +
        grid_gdf['road_accessibility_norm'] * 0.2
    ) * 100
    
    print("✅ Suitability scores calculated")
    print(f"   Mean score: {grid_gdf['suitability_score_100'].mean():.2f}")
    print(f"   Max score: {grid_gdf['suitability_score_100'].max():.2f}")

# Convert any datetime columns to string to avoid JSON serialization issues
for col in grid_gdf.columns:
    if pd.api.types.is_datetime64_any_dtype(grid_gdf[col]):
        grid_gdf[col] = grid_gdf[col].astype(str)

# Save updated grid
print("\nSaving updated grid files...")

# Save WGS84 version
grid_gdf.to_file("data/processed/grid/analysis_grid_wgs84.geojson", driver="GeoJSON")
print("✅ Saved: data/processed/grid/analysis_grid_wgs84.geojson")

# Also update UTM version
grid_utm = grid_gdf.to_crs('EPSG:32643')
grid_utm.to_file("data/processed/grid/analysis_grid_utm.geojson", driver="GeoJSON")
print("✅ Saved: data/processed/grid/analysis_grid_utm.geojson")

# Print summary
print(f"\n📊 SUMMARY:")
print(f"Total cells: {len(grid_gdf):,}")
print(f"Features per cell: {len(grid_gdf.columns)}")
print(f"\nSuitability Distribution:")
class_counts = grid_gdf['suitability_class'].value_counts()
for class_name in ['Excellent', 'Very Good', 'Good', 'Moderate', 'Low']:
    count = class_counts.get(class_name, 0)
    percentage = (count / len(grid_gdf)) * 100
    print(f"  {class_name:12} : {count:4} cells ({percentage:5.1f}%)")

print("\n✅ Grid files updated with suitability scores!")
print("You can now run the Folium map script.")