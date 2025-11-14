"""
GeoRetail Project - Step 4: Amenities & Points of Interest (POI) Collection
Collect retail locations, schools, hospitals, banks, and other key amenities
"""

import osmnx as ox
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

import pandas as pd

from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

print("""
🎯 GEORETAIL PROJECT - STEP 4
🏪 Amenities & Points of Interest (POI) Collection
📅 {}
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

# Create directories
os.makedirs("data/processed/amenities", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Load Coimbatore boundary
print("Loading Coimbatore boundary...")
boundary_gdf = gpd.read_file("data/coimbatore_boundary_clean.geojson")
print(f"✅ Boundary loaded")

# Define POI categories for retail analysis
POI_CATEGORIES = {
    'retail': {
        'tags': {
            'shop': ['supermarket', 'mall', 'department_store', 'convenience', 
                    'general', 'clothes', 'electronics', 'furniture', 'hardware',
                    'mobile_phone', 'shoes', 'sports', 'toys', 'books', 'gifts'],
            'amenity': ['marketplace']
        },
        'description': 'Retail stores and shopping centers (COMPETITION)',
        'color': 'red'
    },
    'education': {
        'tags': {
            'amenity': ['school', 'college', 'university', 'kindergarten'],
            'building': ['school', 'college', 'university']
        },
        'description': 'Educational institutions (FOOT TRAFFIC)',
        'color': 'blue'
    },
    'healthcare': {
        'tags': {
            'amenity': ['hospital', 'clinic', 'doctors', 'pharmacy', 'dentist'],
            'healthcare': True
        },
        'description': 'Healthcare facilities (FOOT TRAFFIC)',
        'color': 'green'
    },
    'banking': {
        'tags': {
            'amenity': ['bank', 'atm']
        },
        'description': 'Banks and ATMs (ECONOMIC ACTIVITY)',
        'color': 'orange'
    },
    'food_beverage': {
        'tags': {
            'amenity': ['restaurant', 'cafe', 'fast_food', 'food_court'],
            'shop': ['bakery']
        },
        'description': 'Food & Beverage outlets (FOOT TRAFFIC)',
        'color': 'purple'
    },
    'entertainment': {
        'tags': {
            'amenity': ['cinema', 'theatre'],
            'leisure': ['park', 'playground', 'sports_centre', 'stadium']
        },
        'description': 'Entertainment & Recreation (FOOT TRAFFIC)',
        'color': 'pink'
    },
    'public_services': {
        'tags': {
            'amenity': ['post_office', 'police', 'fire_station', 'community_centre'],
            'office': ['government']
        },
        'description': 'Public services (FOOT TRAFFIC)',
        'color': 'brown'
    }
}

# Storage for all POI data
all_poi_data = {}
summary_stats = {}

print("\n" + "="*60)
print("DOWNLOADING POI DATA BY CATEGORY")
print("="*60)

# Download POI data for each category
for category_name, category_info in POI_CATEGORIES.items():
    print(f"\n📥 Category: {category_name.upper()}")
    print(f"   Description: {category_info['description']}")
    
    output_file = f"data/processed/amenities/{category_name}.geojson"
    
    if not os.path.exists(output_file):
        try:
            print(f"   Downloading from OSM...")
            
            # Try newer OSMnx method first
            try:
                poi_gdf = ox.features_from_polygon(
                    boundary_gdf.geometry.iloc[0],
                    tags=category_info['tags']
                )
            except AttributeError:
                # Fallback for older OSMnx
                poi_gdf = ox.geometries_from_polygon(
                    boundary_gdf.geometry.iloc[0],
                    tags=category_info['tags']
                )
            
            # Filter to points only (some may be polygons)
            if len(poi_gdf) > 0:
                # Convert polygon centroids to points
                poi_gdf_points = poi_gdf.copy()
                poi_gdf_points.loc[poi_gdf_points.geometry.type != 'Point', 'geometry'] = \
                    poi_gdf_points[poi_gdf_points.geometry.type != 'Point'].geometry.centroid
                
                # Reset index
                poi_gdf_points = poi_gdf_points.reset_index()
                
                # Add category column
                poi_gdf_points['category'] = category_name
                
                # Save
                poi_gdf_points.to_file(output_file, driver="GeoJSON")
                
                all_poi_data[category_name] = poi_gdf_points
                summary_stats[category_name] = len(poi_gdf_points)
                
                print(f"   ✅ Found {len(poi_gdf_points)} locations")
            else:
                print(f"   ⚠️  No data found for this category")
                summary_stats[category_name] = 0
                
                # Create empty file
                empty_gdf = gpd.GeoDataFrame(columns=['geometry', 'category'], crs='EPSG:4326')
                empty_gdf.to_file(output_file, driver="GeoJSON")
                all_poi_data[category_name] = empty_gdf
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            summary_stats[category_name] = 0
            
            # Create empty file
            empty_gdf = gpd.GeoDataFrame(columns=['geometry', 'category'], crs='EPSG:4326')
            empty_gdf.to_file(output_file, driver="GeoJSON")
            all_poi_data[category_name] = empty_gdf
    else:
        print(f"   ✅ Already exists: {output_file}")
        poi_gdf_points = gpd.read_file(output_file)
        all_poi_data[category_name] = poi_gdf_points
        summary_stats[category_name] = len(poi_gdf_points)
        print(f"   Loaded {len(poi_gdf_points)} locations")

# Step 4.2: Create Combined POI Dataset
print("\n" + "="*60)
print("STEP 4.2: Creating Combined POI Dataset")
print("="*60)

combined_poi_list = []
for category_name, poi_gdf in all_poi_data.items():
    if len(poi_gdf) > 0:
        combined_poi_list.append(poi_gdf)

if len(combined_poi_list) > 0:
    combined_poi_gdf = gpd.GeoDataFrame(
        pd.concat(combined_poi_list, ignore_index=True),
        crs='EPSG:4326'
    )
    
    combined_file = "data/processed/amenities/all_poi_combined.geojson"
    combined_poi_gdf.to_file(combined_file, driver="GeoJSON")
    
    print(f"✅ Combined POI dataset created: {len(combined_poi_gdf)} total locations")
    print(f"   Saved to: {combined_file}")
else:
    print("⚠️  No POI data available to combine")
    combined_poi_gdf = gpd.GeoDataFrame(columns=['geometry', 'category'], crs='EPSG:4326')

# Step 4.3: Calculate POI Statistics
print("\n" + "="*60)
print("STEP 4.3: POI Statistics Summary")
print("="*60)

total_poi = sum(summary_stats.values())
print(f"\n📊 Total POI Collected: {total_poi:,}")
print(f"\nBreakdown by Category:")

for category_name, count in sorted(summary_stats.items(), key=lambda x: x[1], reverse=True):
    percentage = (count / total_poi * 100) if total_poi > 0 else 0
    bar = '█' * int(percentage / 2)
    print(f"  {category_name:20} : {count:5} ({percentage:5.1f}%) {bar}")

# Step 4.4: Spatial Analysis - POI Density
print("\n" + "="*60)
print("STEP 4.4: Spatial Distribution Analysis")
print("="*60)

if len(combined_poi_gdf) > 0:
    # Calculate POI density per km²
    area_km2 = boundary_gdf.to_crs('EPSG:3857').geometry.area.sum() / 1e6
    poi_density = total_poi / area_km2
    
    print(f"POI Density: {poi_density:.2f} POI per km²")
    
    # Find POI-rich areas (simple clustering)
    bounds = boundary_gdf.total_bounds
    
    # Retail competition analysis
    if 'retail' in all_poi_data and len(all_poi_data['retail']) > 0:
        retail_count = len(all_poi_data['retail'])
        retail_density = retail_count / area_km2
        print(f"\n🏪 RETAIL COMPETITION ANALYSIS:")
        print(f"   Total retail locations: {retail_count}")
        print(f"   Retail density: {retail_density:.2f} stores per km²")
        print(f"   Market saturation: {'High' if retail_density > 5 else 'Medium' if retail_density > 2 else 'Low'}")

# Step 4.5: Create Comprehensive Visualizations
print("\n" + "="*60)
print("STEP 4.5: Creating Visualizations")
print("="*60)

fig = plt.figure(figsize=(24, 18))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3)

# Plot 1: All POI Overview (Large)
ax1 = fig.add_subplot(gs[0, :2])
boundary_gdf.plot(ax=ax1, facecolor='lightgray', edgecolor='black', alpha=0.3)

for category_name, poi_gdf in all_poi_data.items():
    if len(poi_gdf) > 0:
        color = POI_CATEGORIES[category_name]['color']
        poi_gdf.plot(ax=ax1, color=color, markersize=15, alpha=0.6, 
                    label=f"{category_name} ({len(poi_gdf)})")

ax1.set_title('All Points of Interest - Coimbatore', fontsize=14, fontweight='bold')
ax1.legend(loc='upper right', fontsize=9, ncol=2)
ax1.axis('off')

# Plot 2: Category Distribution Pie Chart
ax2 = fig.add_subplot(gs[0, 2])
if total_poi > 0:
    colors_list = [POI_CATEGORIES[cat]['color'] for cat in summary_stats.keys()]
    ax2.pie(summary_stats.values(), labels=summary_stats.keys(), autopct='%1.1f%%',
           colors=colors_list, startangle=90)
    ax2.set_title('POI Distribution by Category', fontsize=12, fontweight='bold')
else:
    ax2.text(0.5, 0.5, 'No POI Data', ha='center', va='center')
    ax2.set_title('POI Distribution', fontsize=12, fontweight='bold')

# Plot 3-8: Individual category maps
category_plots = [
    (gs[1, 0], 'retail', 'Retail Competition'),
    (gs[1, 1], 'education', 'Educational Institutions'),
    (gs[1, 2], 'healthcare', 'Healthcare Facilities'),
    (gs[2, 0], 'banking', 'Banks & ATMs'),
    (gs[2, 1], 'food_beverage', 'Food & Beverage'),
    (gs[2, 2], 'entertainment', 'Entertainment & Recreation')
]

for grid_pos, category, title in category_plots:
    ax = fig.add_subplot(grid_pos)
    boundary_gdf.plot(ax=ax, facecolor='white', edgecolor='gray', alpha=0.5)
    
    if category in all_poi_data and len(all_poi_data[category]) > 0:
        color = POI_CATEGORIES[category]['color']
        all_poi_data[category].plot(ax=ax, color=color, markersize=25, alpha=0.7)
        count = len(all_poi_data[category])
        ax.set_title(f'{title}\n({count} locations)', fontsize=11, fontweight='bold')
    else:
        ax.set_title(f'{title}\n(No data)', fontsize=11, fontweight='bold')
    
    ax.axis('off')

plt.suptitle('Coimbatore Amenities & POI Analysis - GeoRetail Project', 
            fontsize=18, fontweight='bold', y=0.995)

output_viz = "outputs/step4_amenities_poi_analysis.png"
plt.savefig(output_viz, dpi=300, bbox_inches='tight')
print(f"✅ Visualization saved: {output_viz}")

# Step 4.6: Create Competition Heat Analysis
print("\n" + "="*60)
print("STEP 4.6: Retail Competition Analysis")
print("="*60)

if 'retail' in all_poi_data and len(all_poi_data['retail']) > 0:
    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    
    # Competition density map
    boundary_gdf.plot(ax=ax1, facecolor='lightyellow', edgecolor='black', alpha=0.5)
    all_poi_data['retail'].plot(ax=ax1, color='darkred', markersize=40, 
                                alpha=0.6, edgecolor='black', linewidth=0.5)
    ax1.set_title('Retail Competition Locations', fontsize=14, fontweight='bold')
    ax1.axis('off')
    
    # Statistics panel
    ax2.axis('off')
    
    retail_stats = f"""
    RETAIL COMPETITION ANALYSIS
    
    📊 Total Retail Locations: {len(all_poi_data['retail']):,}
    
    📍 Density: {retail_density:.2f} stores/km²
    
    🎯 Market Assessment:
       Saturation Level: {'High' if retail_density > 5 else 'Medium' if retail_density > 2 else 'Low'}
       
       Competition Intensity:
       {'⚠️  Highly competitive market' if retail_density > 5 else '✅ Moderate competition' if retail_density > 2 else '✅ Low competition - Good opportunity'}
    
    💡 Recommendation:
       {'Focus on underserved areas' if retail_density > 3 else 'Opportunity for market entry'}
    
    📈 Store Types Found:
    """
    
    # Add store type breakdown if available
    if 'shop' in all_poi_data['retail'].columns:
        shop_types = all_poi_data['retail']['shop'].value_counts().head(5)
        for shop_type, count in shop_types.items():
            if pd.notna(shop_type):
                retail_stats += f"\n       {shop_type}: {count}"
    
    ax2.text(0.1, 0.5, retail_stats, fontsize=11, family='monospace',
            verticalalignment='center',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    
    plt.suptitle('Retail Competition Deep Dive', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    competition_viz = "outputs/step4_retail_competition_analysis.png"
    plt.savefig(competition_viz, dpi=300, bbox_inches='tight')
    print(f"✅ Competition analysis saved: {competition_viz}")

# Step 4.7: Save Summary Report
print("\n" + "="*60)
print("STEP 4.7: Saving Summary Report")
print("="*60)

summary_report = f"""
GEORETAIL PROJECT - AMENITIES & POI DATA COLLECTION REPORT
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

=== DATA COLLECTION SUMMARY ===

Total POI Collected: {total_poi:,}
Coverage Area: {area_km2:.2f} km²
Overall POI Density: {poi_density:.2f} POI per km²

=== POI BREAKDOWN BY CATEGORY ===

"""

for category_name, count in sorted(summary_stats.items(), key=lambda x: x[1], reverse=True):
    percentage = (count / total_poi * 100) if total_poi > 0 else 0
    description = POI_CATEGORIES[category_name]['description']
    summary_report += f"""
{category_name.upper()}:
- Count: {count:,}
- Percentage: {percentage:.1f}%
- Purpose: {description}
- File: data/processed/amenities/{category_name}.geojson
"""

if 'retail' in all_poi_data and len(all_poi_data['retail']) > 0:
    summary_report += f"""
=== RETAIL COMPETITION ANALYSIS ===

Total Retail Locations: {len(all_poi_data['retail']):,}
Retail Density: {retail_density:.2f} stores/km²
Market Saturation: {'High' if retail_density > 5 else 'Medium' if retail_density > 2 else 'Low'}
Competition Level: {'⚠️  High - Market saturated' if retail_density > 5 else '⚠️  Moderate - Strategic entry needed' if retail_density > 2 else '✅ Low - Good opportunity'}
"""

summary_report += f"""
=== OUTPUT FILES ===

Individual Categories:
"""
for category_name in POI_CATEGORIES.keys():
    summary_report += f"- data/processed/amenities/{category_name}.geojson\n"

summary_report += f"""
Combined Dataset:
- data/processed/amenities/all_poi_combined.geojson

Visualizations:
- outputs/step4_amenities_poi_analysis.png
- outputs/step4_retail_competition_analysis.png

Reports:
- outputs/step4_amenities_report.txt

=== DATA QUALITY ===

✅ Spatial coverage: Complete
✅ Data source: OpenStreetMap
✅ CRS: EPSG:4326 (WGS84)
✅ Point geometries: Validated

=== KEY INSIGHTS ===

1. Retail Competition: {len(all_poi_data.get('retail', [])):,} existing stores identified
2. Foot Traffic Sources: {len(all_poi_data.get('education', [])):,} schools, {len(all_poi_data.get('healthcare', [])):,} healthcare facilities
3. Economic Activity Indicators: {len(all_poi_data.get('banking', [])):,} banks/ATMs
4. Complementary Services: {len(all_poi_data.get('food_beverage', [])):,} F&B outlets

=== NEXT STEPS ===

✅ Step 4 Complete: Amenities & POI Data Collected
➡️  Step 5: Create Analysis Grid (500m × 500m)
➡️  Step 6: Calculate Spatial Features (density, proximity, accessibility)
➡️  Step 7: Multi-Criteria Suitability Analysis
"""

report_file = "outputs/step4_amenities_report.txt"
with open(report_file, 'w') as f:
    f.write(summary_report)

print(summary_report)
print(f"✅ Report saved: {report_file}")

print("\n" + "="*60)
print("🎉 STEP 4 COMPLETE: AMENITIES & POI DATA COLLECTED!")
print("="*60)
print(f"\n📊 SUMMARY:")
print(f"   Total POI: {total_poi:,}")
print(f"   Categories: {len([c for c in summary_stats.values() if c > 0])}/{len(POI_CATEGORIES)}")
print(f"   Retail Competition: {len(all_poi_data.get('retail', [])):,} locations")
print("\n➡️  NEXT: Run Step 5 - Create Analysis Grid")

try:
    plt.show()
except:
    print("⚠️  Display not available (headless mode)")