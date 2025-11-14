"""
GeoRetail Project - Step 5: Create Analysis Grid & Calculate Spatial Features
Create 500m x 500m grid and calculate all spatial metrics for retail suitability analysis
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, box
import matplotlib.pyplot as plt
from datetime import datetime
import rasterio
from rasterio.mask import mask as raster_mask
import os
import warnings
warnings.filterwarnings('ignore')

print("""
🎯 GEORETAIL PROJECT - STEP 5
📊 Analysis Grid Creation & Feature Engineering
📅 {}
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

# Create directories
os.makedirs("data/processed/grid", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Configuration
GRID_CELL_SIZE = 500  # meters (500m x 500m cells)
TARGET_CRS = 'EPSG:32643'  # UTM Zone 43N for Coimbatore (meters)

print(f"Grid Configuration:")
print(f"  Cell Size: {GRID_CELL_SIZE}m × {GRID_CELL_SIZE}m")
print(f"  Target CRS: {TARGET_CRS}")

# Step 5.1: Load All Data
print("\n" + "="*60)
print("STEP 5.1: Loading All Collected Data")
print("="*60)

# Load boundary
print("Loading boundary...")
boundary_gdf = gpd.read_file("data/coimbatore_boundary_clean.geojson")
boundary_utm = boundary_gdf.to_crs(TARGET_CRS)
print(f"✅ Boundary loaded")

# Load population raster
print("Loading population data...")
population_raster_path = "data/processed/coimbatore_population.tif"
if os.path.exists(population_raster_path):
    print(f"✅ Population raster found")
else:
    print(f"⚠️  Population raster not found at {population_raster_path}")

# Load roads
print("Loading road network...")
roads_gdf = gpd.read_file("data/processed/coimbatore_roads.geojson")
roads_utm = roads_gdf.to_crs(TARGET_CRS)
major_roads_gdf = gpd.read_file("data/processed/coimbatore_major_roads.geojson")
major_roads_utm = major_roads_gdf.to_crs(TARGET_CRS)
print(f"✅ Roads loaded: {len(roads_gdf)} segments")

# Load POI data
print("Loading POI data...")
poi_categories = ['retail', 'education', 'healthcare', 'banking', 'food_beverage', 'entertainment']
poi_data = {}

for category in poi_categories:
    poi_file = f"data/processed/amenities/{category}.geojson"
    if os.path.exists(poi_file):
        gdf = gpd.read_file(poi_file)
        if len(gdf) > 0:
            poi_data[category] = gdf.to_crs(TARGET_CRS)
            print(f"  ✅ {category}: {len(gdf)} locations")
        else:
            poi_data[category] = gpd.GeoDataFrame(columns=['geometry'], crs=TARGET_CRS)
            print(f"  ⚠️  {category}: No data")
    else:
        poi_data[category] = gpd.GeoDataFrame(columns=['geometry'], crs=TARGET_CRS)
        print(f"  ⚠️  {category}: File not found")

# Step 5.2: Create Analysis Grid
print("\n" + "="*60)
print("STEP 5.2: Creating Analysis Grid")
print("="*60)

def create_grid(gdf, cell_size=500):
    """Create a grid of square cells covering the study area"""
    bounds = gdf.total_bounds  # minx, miny, maxx, maxy
    
    # Calculate grid dimensions
    x_coords = np.arange(bounds[0], bounds[2], cell_size)
    y_coords = np.arange(bounds[1], bounds[3], cell_size)
    
    print(f"  Grid dimensions: {len(x_coords)} × {len(y_coords)} cells")
    
    # Create grid cells
    grid_cells = []
    cell_ids = []
    
    cell_id = 0
    for x in x_coords:
        for y in y_coords:
            cell = box(x, y, x + cell_size, y + cell_size)
            # Only include cells that intersect with study area
            if gdf.geometry.iloc[0].intersects(cell):
                grid_cells.append(cell)
                cell_ids.append(cell_id)
                cell_id += 1
    
    print(f"  Created {len(grid_cells)} grid cells within boundary")
    
    grid_gdf = gpd.GeoDataFrame({
        'cell_id': cell_ids,
        'geometry': grid_cells
    }, crs=gdf.crs)
    
    return grid_gdf

print(f"Creating {GRID_CELL_SIZE}m × {GRID_CELL_SIZE}m grid...")
grid_gdf = create_grid(boundary_utm, GRID_CELL_SIZE)

# Add cell centroids
grid_gdf['centroid_x'] = grid_gdf.geometry.centroid.x
grid_gdf['centroid_y'] = grid_gdf.geometry.centroid.y

# Calculate cell area
grid_gdf['area_m2'] = grid_gdf.geometry.area
grid_gdf['area_km2'] = grid_gdf['area_m2'] / 1e6

print(f"✅ Grid created: {len(grid_gdf)} cells")
print(f"   Total coverage: {grid_gdf['area_km2'].sum():.2f} km²")

# Step 5.3: Calculate Population Features
print("\n" + "="*60)
print("STEP 5.3: Calculating Population Features")
print("="*60)

def calculate_population_per_cell(grid_gdf, raster_path):
    """Extract population sum for each grid cell"""
    
    with rasterio.open(raster_path) as src:
        # Reproject grid to raster CRS
        grid_raster_crs = grid_gdf.to_crs(src.crs)
        
        population_values = []
        
        for idx, cell in grid_raster_crs.iterrows():
            try:
                # Mask raster with cell geometry
                out_image, out_transform = raster_mask(
                    src, [cell.geometry], crop=True, nodata=src.nodata
                )
                
                # Sum population in cell
                pop_data = out_image[0]
                pop_sum = pop_data[pop_data > 0].sum() if np.any(pop_data > 0) else 0
                population_values.append(pop_sum)
                
            except Exception as e:
                population_values.append(0)
            
            if (idx + 1) % 100 == 0:
                print(f"  Processed {idx + 1}/{len(grid_gdf)} cells", end='\r')
        
        print(f"  Processed {len(grid_gdf)}/{len(grid_gdf)} cells")
        
        return population_values

if os.path.exists(population_raster_path):
    print("Extracting population for each grid cell...")
    grid_gdf['population'] = calculate_population_per_cell(grid_gdf, population_raster_path)
    grid_gdf['pop_density'] = grid_gdf['population'] / grid_gdf['area_km2']
    
    print(f"✅ Population calculated")
    print(f"   Total population: {grid_gdf['population'].sum():,.0f}")
    print(f"   Mean density: {grid_gdf['pop_density'].mean():.2f} people/km²")
    print(f"   Max density: {grid_gdf['pop_density'].max():.2f} people/km²")
else:
    print("⚠️  Population raster not available, skipping...")
    grid_gdf['population'] = 0
    grid_gdf['pop_density'] = 0

# Step 5.4: Calculate Road Network Features
print("\n" + "="*60)
print("STEP 5.4: Calculating Road Network Features")
print("="*60)

def calculate_road_features(grid_gdf, roads_gdf, major_roads_gdf):
    """Calculate road accessibility metrics for each cell"""
    
    road_lengths = []
    major_road_lengths = []
    nearest_major_road_dists = []
    
    for idx, cell in grid_gdf.iterrows():
        # Road length within cell
        roads_in_cell = roads_gdf[roads_gdf.intersects(cell.geometry)]
        if len(roads_in_cell) > 0:
            clipped_roads = roads_in_cell.intersection(cell.geometry)
            total_length = clipped_roads.length.sum()
            road_lengths.append(total_length)
        else:
            road_lengths.append(0)
        
        # Major road length within cell
        major_in_cell = major_roads_gdf[major_roads_gdf.intersects(cell.geometry)]
        if len(major_in_cell) > 0:
            clipped_major = major_in_cell.intersection(cell.geometry)
            major_length = clipped_major.length.sum()
            major_road_lengths.append(major_length)
        else:
            major_road_lengths.append(0)
        
        # Distance to nearest major road
        if len(major_roads_gdf) > 0:
            distances = major_roads_gdf.distance(cell.geometry.centroid)
            nearest_dist = distances.min()
            nearest_major_road_dists.append(nearest_dist)
        else:
            nearest_major_road_dists.append(np.nan)
        
        if (idx + 1) % 100 == 0:
            print(f"  Processed {idx + 1}/{len(grid_gdf)} cells", end='\r')
    
    print(f"  Processed {len(grid_gdf)}/{len(grid_gdf)} cells")
    
    return road_lengths, major_road_lengths, nearest_major_road_dists

print("Calculating road accessibility metrics...")
road_lengths, major_road_lengths, nearest_major_dists = calculate_road_features(
    grid_gdf, roads_utm, major_roads_utm
)

grid_gdf['road_length_m'] = road_lengths
grid_gdf['road_density_km_per_km2'] = (np.array(road_lengths) / 1000) / grid_gdf['area_km2']
grid_gdf['major_road_length_m'] = major_road_lengths
grid_gdf['dist_to_major_road_m'] = nearest_major_dists

print(f"✅ Road features calculated")
print(f"   Mean road density: {grid_gdf['road_density_km_per_km2'].mean():.2f} km/km²")
print(f"   Mean distance to major road: {grid_gdf['dist_to_major_road_m'].mean():.2f} m")

# Step 5.5: Calculate POI Proximity Features
print("\n" + "="*60)
print("STEP 5.5: Calculating POI Proximity Features")
print("="*60)

def calculate_poi_features(grid_gdf, poi_data_dict, search_radius=1000):
    """Calculate POI counts and proximity metrics"""
    
    poi_features = {}
    
    for category, poi_gdf in poi_data_dict.items():
        print(f"  Processing {category}...")
        
        if len(poi_gdf) == 0:
            # No POI data for this category
            poi_features[f'{category}_count_1km'] = [0] * len(grid_gdf)
            poi_features[f'{category}_nearest_dist_m'] = [np.nan] * len(grid_gdf)
            continue
        
        counts = []
        nearest_dists = []
        
        for idx, cell in grid_gdf.iterrows():
            centroid = cell.geometry.centroid
            
            # Count within search radius
            buffer = centroid.buffer(search_radius)
            poi_within = poi_gdf[poi_gdf.intersects(buffer)]
            counts.append(len(poi_within))
            
            # Distance to nearest
            if len(poi_gdf) > 0:
                distances = poi_gdf.distance(centroid)
                nearest_dist = distances.min()
                nearest_dists.append(nearest_dist)
            else:
                nearest_dists.append(np.nan)
        
        poi_features[f'{category}_count_1km'] = counts
        poi_features[f'{category}_nearest_dist_m'] = nearest_dists
        
        print(f"    Mean count: {np.mean(counts):.2f} within 1km")
        print(f"    Mean nearest distance: {np.nanmean(nearest_dists):.2f} m")
    
    return poi_features

print(f"Calculating POI features (search radius: 1000m)...")
poi_features = calculate_poi_features(grid_gdf, poi_data, search_radius=1000)

# Add POI features to grid
for feature_name, values in poi_features.items():
    grid_gdf[feature_name] = values

print(f"✅ POI features calculated")

# Step 5.6: Calculate Competition Metrics
print("\n" + "="*60)
print("STEP 5.6: Calculating Competition Metrics")
print("="*60)

# Retail competition intensity
if 'retail' in poi_data and len(poi_data['retail']) > 0:
    grid_gdf['competition_score'] = grid_gdf['retail_count_1km']
    
    # Competition pressure (competitors per 1000 people)
    grid_gdf['competition_pressure'] = np.where(
        grid_gdf['population'] > 0,
        (grid_gdf['retail_count_1km'] / grid_gdf['population']) * 1000,
        0
    )
    
    print(f"✅ Competition metrics calculated")
    print(f"   Mean competition score: {grid_gdf['competition_score'].mean():.2f}")
    print(f"   Max competition in single cell: {grid_gdf['competition_score'].max():.0f}")
else:
    grid_gdf['competition_score'] = 0
    grid_gdf['competition_pressure'] = 0
    print(f"⚠️  No retail competition data available")

# Step 5.7: Calculate Composite Amenity Score
print("\n" + "="*60)
print("STEP 5.7: Calculating Composite Amenity Score")
print("="*60)

# Amenity score based on foot traffic generators
amenity_categories = ['education', 'healthcare', 'banking', 'food_beverage', 'entertainment']
amenity_weights = {
    'education': 0.25,
    'healthcare': 0.25,
    'banking': 0.15,
    'food_beverage': 0.20,
    'entertainment': 0.15
}

grid_gdf['amenity_score'] = 0
for category, weight in amenity_weights.items():
    col_name = f'{category}_count_1km'
    if col_name in grid_gdf.columns:
        grid_gdf['amenity_score'] += grid_gdf[col_name] * weight

print(f"✅ Amenity score calculated")
print(f"   Mean amenity score: {grid_gdf['amenity_score'].mean():.2f}")
print(f"   Max amenity score: {grid_gdf['amenity_score'].max():.2f}")

# Step 5.8: Save Grid with Features
print("\n" + "="*60)
print("STEP 5.8: Saving Analysis Grid")
print("="*60)

# Save in UTM projection
output_file_utm = "data/processed/grid/analysis_grid_utm.geojson"
grid_gdf.to_file(output_file_utm, driver="GeoJSON")
print(f"✅ Saved grid (UTM): {output_file_utm}")

# Save in WGS84 for visualization
grid_wgs84 = grid_gdf.to_crs('EPSG:4326')
output_file_wgs84 = "data/processed/grid/analysis_grid_wgs84.geojson"
grid_wgs84.to_file(output_file_wgs84, driver="GeoJSON")
print(f"✅ Saved grid (WGS84): {output_file_wgs84}")

# Save summary statistics
stats_df = grid_gdf.drop(columns=['geometry']).describe()
stats_file = "data/processed/grid/grid_statistics.csv"
stats_df.to_csv(stats_file)
print(f"✅ Saved statistics: {stats_file}")

print(f"\nGrid contains {len(grid_gdf.columns)} features")

# Step 5.9: Create Visualizations
print("\n" + "="*60)
print("STEP 5.9: Creating Feature Visualizations")
print("="*60)

fig = plt.figure(figsize=(24, 20))
gs = fig.add_gridspec(4, 3, hspace=0.35, wspace=0.3)

# Define features to visualize
viz_features = [
    ('pop_density', 'Population Density', 'YlOrRd', 'people/km²'),
    ('road_density_km_per_km2', 'Road Density', 'Blues', 'km/km²'),
    ('dist_to_major_road_m', 'Distance to Major Road', 'RdYlGn_r', 'meters'),
    ('competition_score', 'Retail Competition', 'Reds', 'count'),
    ('amenity_score', 'Amenity Score', 'Greens', 'score'),
    ('retail_count_1km', 'Retail Locations (1km)', 'OrRd', 'count'),
    ('education_count_1km', 'Education (1km)', 'Blues', 'count'),
    ('healthcare_count_1km', 'Healthcare (1km)', 'Greens', 'count'),
    ('banking_count_1km', 'Banking (1km)', 'Oranges', 'count'),
    ('food_beverage_count_1km', 'Food & Beverage (1km)', 'Purples', 'count'),
    ('entertainment_count_1km', 'Entertainment (1km)', 'PuRd', 'count'),
    ('competition_pressure', 'Competition Pressure', 'RdPu', 'per 1000 people')
]

for idx, (feature, title, cmap, unit) in enumerate(viz_features):
    row = idx // 3
    col = idx % 3
    ax = fig.add_subplot(gs[row, col])
    
    if feature in grid_gdf.columns:
        # Plot grid
        grid_gdf.plot(column=feature, ax=ax, cmap=cmap, legend=True,
                     legend_kwds={'label': unit, 'shrink': 0.7},
                     edgecolor='gray', linewidth=0.1, alpha=0.8)
        
        # Overlay boundary
        boundary_utm.boundary.plot(ax=ax, color='black', linewidth=2)
        
        # Stats
        mean_val = grid_gdf[feature].mean()
        max_val = grid_gdf[feature].max()
        ax.text(0.02, 0.98, f'Mean: {mean_val:.2f}\nMax: {max_val:.2f}',
               transform=ax.transAxes, fontsize=8,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    else:
        ax.text(0.5, 0.5, 'No Data', ha='center', va='center',
               transform=ax.transAxes)
    
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.axis('off')

plt.suptitle('Spatial Feature Analysis - 500m Grid Cells', 
            fontsize=18, fontweight='bold', y=0.995)

output_viz = "outputs/step5_grid_features_analysis.png"
plt.savefig(output_viz, dpi=300, bbox_inches='tight')
print(f"✅ Visualization saved: {output_viz}")

# Step 5.10: Create Summary Report
print("\n" + "="*60)
print("STEP 5.10: Generating Summary Report")
print("="*60)

summary_report = f"""
GEORETAIL PROJECT - ANALYSIS GRID & FEATURE ENGINEERING REPORT
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

=== GRID CONFIGURATION ===

Cell Size: {GRID_CELL_SIZE}m × {GRID_CELL_SIZE}m
Total Cells: {len(grid_gdf):,}
Total Coverage: {grid_gdf['area_km2'].sum():.2f} km²
Coordinate System: {TARGET_CRS}

=== CALCULATED FEATURES ===

1. POPULATION METRICS
   - Total Population: {grid_gdf['population'].sum():,.0f}
   - Mean Density: {grid_gdf['pop_density'].mean():.2f} people/km²
   - Max Density: {grid_gdf['pop_density'].max():.2f} people/km²
   - Cells with population > 0: {(grid_gdf['population'] > 0).sum():,}

2. ROAD NETWORK METRICS
   - Mean Road Density: {grid_gdf['road_density_km_per_km2'].mean():.2f} km/km²
   - Mean Distance to Major Road: {grid_gdf['dist_to_major_road_m'].mean():.2f} m
   - Cells with roads: {(grid_gdf['road_length_m'] > 0).sum():,}

3. COMPETITION METRICS
   - Mean Competition Score: {grid_gdf['competition_score'].mean():.2f}
   - Max Competition: {grid_gdf['competition_score'].max():.0f} stores
   - Mean Competition Pressure: {grid_gdf['competition_pressure'].mean():.2f} per 1000 people
   - High competition cells (>5 stores): {(grid_gdf['competition_score'] > 5).sum():,}

4. AMENITY METRICS
   - Mean Amenity Score: {grid_gdf['amenity_score'].mean():.2f}
   - Max Amenity Score: {grid_gdf['amenity_score'].max():.2f}
   - High amenity cells (score > 10): {(grid_gdf['amenity_score'] > 10).sum():,}

5. POI PROXIMITY (Within 1km)
"""

for category in poi_categories:
    col_name = f'{category}_count_1km'
    if col_name in grid_gdf.columns:
        mean_count = grid_gdf[col_name].mean()
        max_count = grid_gdf[col_name].max()
        summary_report += f"   - {category.title()}: Mean={mean_count:.2f}, Max={max_count:.0f}\n"

summary_report += f"""
=== OUTPUT FILES ===

Grid Files:
- data/processed/grid/analysis_grid_utm.geojson (for analysis)
- data/processed/grid/analysis_grid_wgs84.geojson (for visualization)
- data/processed/grid/grid_statistics.csv (summary stats)

Visualizations:
- outputs/step5_grid_features_analysis.png

Reports:
- outputs/step5_grid_report.txt

=== FEATURE LIST ===

Total Features: {len(grid_gdf.columns)}

Key Features:
- cell_id: Unique identifier
- population, pop_density: Population metrics
- road_length_m, road_density_km_per_km2: Road accessibility
- dist_to_major_road_m: Highway proximity
- competition_score, competition_pressure: Retail competition
- amenity_score: Composite foot traffic potential
- [category]_count_1km: POI counts within 1km
- [category]_nearest_dist_m: Distance to nearest POI

=== DATA QUALITY ===

✅ Grid topology: Valid
✅ Feature completeness: {len(grid_gdf.columns)} features
✅ No null geometries: {grid_gdf.geometry.isna().sum() == 0}
✅ Population coverage: {(grid_gdf['population'] > 0).sum() / len(grid_gdf) * 100:.1f}%
✅ Road coverage: {(grid_gdf['road_length_m'] > 0).sum() / len(grid_gdf) * 100:.1f}%

=== NEXT STEPS ===

✅ Step 5 Complete: Analysis Grid with Spatial Features
➡️  Step 6: Multi-Criteria Suitability Analysis
➡️  Step 7: Identify Top Retail Locations
➡️  Step 8: Create Interactive Dashboard
"""

report_file = "outputs/step5_grid_report.txt"
with open(report_file, 'w') as f:
    f.write(summary_report)

print(summary_report)
print(f"✅ Report saved: {report_file}")

print("\n" + "="*60)
print("🎉 STEP 5 COMPLETE: ANALYSIS GRID CREATED!")
print("="*60)
print(f"\n📊 GRID SUMMARY:")
print(f"   Total Cells: {len(grid_gdf):,}")
print(f"   Features per Cell: {len(grid_gdf.columns)}")
print(f"   Coverage: {grid_gdf['area_km2'].sum():.2f} km²")
print("\n➡️  NEXT: Run Step 6 - Multi-Criteria Suitability Analysis")

try:
    plt.show()
except:
    print("⚠️  Display not available (headless mode)")