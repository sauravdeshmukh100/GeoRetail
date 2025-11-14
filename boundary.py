import geopandas as gpd
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime
from shapely.geometry import shape
import numpy as np

print("""
🎯 LOADING CUSTOM COIMBATORE CITY BOUNDARY
📅 {}
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

# Your custom boundary GeoJSON
custom_boundary_geojson = {
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "name": "Expanded Coimbatore City Boundary"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [76.920, 11.121],
            [76.969, 11.130],
            [77.001, 11.121],
            [77.031, 11.133],
            [77.060, 11.109],
            [77.078, 11.077],
            [77.074, 11.036],
            [77.086, 11.000],
            [77.051, 10.963],
            [77.014, 10.931],
            [76.980, 10.916],
            [76.940, 10.915],
            [76.911, 10.944],
            [76.883, 10.982],
            [76.868, 11.020],
            [76.877, 11.066],
            [76.901, 11.097],
            [76.920, 11.121]
          ]
        ]
      }
    }
  ]
}

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Save the GeoJSON to file
geojson_path = "data/gemini_coimbatore_city_boundary.geojson"
with open(geojson_path, 'w') as f:
    json.dump(custom_boundary_geojson, f, indent=2)

print(f"✅ Saved custom boundary to: {geojson_path}")

# Load it as a GeoDataFrame
coimbatore_gdf = gpd.read_file(geojson_path)

# Set CRS to WGS84 if not already set
if coimbatore_gdf.crs is None:
    coimbatore_gdf = coimbatore_gdf.set_crs("EPSG:4326")

print(f"✅ Loaded as GeoDataFrame")
print(f"📊 CRS: {coimbatore_gdf.crs}")
print(f"📏 Geometry type: {coimbatore_gdf.geometry.type.iloc[0]}")

# Calculate statistics
area_km2 = coimbatore_gdf.to_crs('EPSG:3857').geometry.area.iloc[0] / 1e6
bounds = coimbatore_gdf.total_bounds
perimeter_km = coimbatore_gdf.to_crs('EPSG:3857').geometry.length.iloc[0] / 1000
centroid = coimbatore_gdf.geometry.centroid.iloc[0]

print(f"\n📈 BOUNDARY STATISTICS:")
print(f"Area: {area_km2:.2f} km²")
print(f"Perimeter: {perimeter_km:.2f} km")
print(f"Centroid: {centroid.y:.4f}°N, {centroid.x:.4f}°E")
print(f"Bounds:")
print(f"  North: {bounds[3]:.4f}°")
print(f"  South: {bounds[1]:.4f}°")
print(f"  East: {bounds[2]:.4f}°")
print(f"  West: {bounds[0]:.4f}°")
print(f"Width: {(bounds[2] - bounds[0]) * 111:.2f} km")
print(f"Height: {(bounds[3] - bounds[1]) * 111:.2f} km")

# Key zones for verification
COIMBATORE_ZONES = {
    'Gandhipuram': (11.0168, 76.9558),
    'RS Puram': (11.0041, 76.9520),
    'Peelamedu': (11.0296, 76.9376),
    'Singanallur': (11.0516, 76.9661),
    'Saibaba Colony': (11.0078, 76.9733),
    'Vadavalli': (11.0021, 76.9021),
    'Kuniyamuthur': (10.9913, 76.9173),
    'Thudiyalur': (11.0670, 76.9440)
}

# Verify zones
print(f"\n🏙️  ZONE COVERAGE CHECK:")
from shapely.geometry import Point

inside_count = 0
for zone_name, (lat, lng) in COIMBATORE_ZONES.items():
    point = Point(lng, lat)
    is_inside = coimbatore_gdf.contains(point).iloc[0]
    status = "✅ Inside" if is_inside else "⚠️  Outside"
    print(f"{zone_name:15} ({lat:.4f}, {lng:.4f}): {status}")
    if is_inside:
        inside_count += 1

print(f"\nZone coverage: {inside_count}/{len(COIMBATORE_ZONES)} zones inside boundary")

# Create comprehensive visualization
fig = plt.figure(figsize=(20, 12))

# Create grid for subplots
gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
ax1 = fig.add_subplot(gs[0, :2])
ax2 = fig.add_subplot(gs[0, 2])
ax3 = fig.add_subplot(gs[1, 0])
ax4 = fig.add_subplot(gs[1, 1])
ax5 = fig.add_subplot(gs[1, 2])

# Plot 1: Main boundary with zones (large)
coimbatore_gdf.plot(ax=ax1, facecolor='lightblue', edgecolor='darkblue', alpha=0.7, linewidth=2)

# Add zone markers
zone_colors = plt.cm.Set3(np.linspace(0, 1, len(COIMBATORE_ZONES)))
for i, (zone_name, (lat, lng)) in enumerate(COIMBATORE_ZONES.items()):
    point = Point(lng, lat)
    is_inside = coimbatore_gdf.contains(point).iloc[0]
    marker = 'o' if is_inside else 'x'
    markersize = 150 if is_inside else 100
    
    ax1.scatter(lng, lat, c=[zone_colors[i]], s=markersize, marker=marker, 
               edgecolor='black', linewidth=2)
    ax1.annotate(zone_name, (lng, lat), xytext=(7, 7), textcoords='offset points',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.9, edgecolor='black'))

# Add centroid
ax1.scatter(centroid.x, centroid.y, c='red', s=300, marker='*', 
           edgecolor='black', linewidth=2, label='City Center', zorder=5)

ax1.set_title('Coimbatore City - Expanded Boundary\nwith Key Areas', 
             fontsize=16, fontweight='bold', pad=15)
ax1.set_xlabel('Longitude', fontsize=12)
ax1.set_ylabel('Latitude', fontsize=12)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.legend(loc='upper left', fontsize=10)

# Plot 2: Boundary vertices
coords = list(coimbatore_gdf.geometry.iloc[0].exterior.coords)
lons = [c[0] for c in coords]
lats = [c[1] for c in coords]

coimbatore_gdf.plot(ax=ax2, facecolor='lightgreen', edgecolor='darkgreen', alpha=0.5, linewidth=2)
ax2.plot(lons, lats, 'ro-', markersize=6, linewidth=1.5, label='Boundary vertices')

# Label some vertices
for i in range(0, len(coords)-1, 3):
    ax2.annotate(f'{i}', (lons[i], lats[i]), fontsize=8, 
                bbox=dict(boxstyle='circle', facecolor='yellow', alpha=0.7))

ax2.set_title('Boundary Vertices', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend()

# Plot 3: Northern section detail
north_bounds = [bounds[0], 11.05, bounds[2], bounds[3]]
coimbatore_gdf.plot(ax=ax3, facecolor='lightyellow', edgecolor='orange', alpha=0.7, linewidth=2)
ax3.set_xlim(north_bounds[0], north_bounds[2])
ax3.set_ylim(north_bounds[1], north_bounds[3])
ax3.set_title('Northern Section Detail', fontsize=11, fontweight='bold')
ax3.grid(True, alpha=0.3)

# Plot 4: Southern section detail
south_bounds = [bounds[0], bounds[1], bounds[2], 10.98]
coimbatore_gdf.plot(ax=ax4, facecolor='lightcoral', edgecolor='darkred', alpha=0.7, linewidth=2)
ax4.set_xlim(south_bounds[0], south_bounds[2])
ax4.set_ylim(south_bounds[1], south_bounds[3])
ax4.set_title('Southern Section Detail', fontsize=11, fontweight='bold')
ax4.grid(True, alpha=0.3)

# Plot 5: Statistics display
ax5.axis('off')
stats_text = f"""
BOUNDARY SUMMARY

📊 Area: {area_km2:.2f} km²
📏 Perimeter: {perimeter_km:.2f} km

📍 Center:
   {centroid.y:.4f}°N
   {centroid.x:.4f}°E

🗺️  Extent:
   N: {bounds[3]:.4f}°
   S: {bounds[1]:.4f}°
   E: {bounds[2]:.4f}°
   W: {bounds[0]:.4f}°

📐 Dimensions:
   Width: {(bounds[2] - bounds[0]) * 111:.2f} km
   Height: {(bounds[3] - bounds[1]) * 111:.2f} km

🏙️  Zones:
   {inside_count}/{len(COIMBATORE_ZONES)} zones covered

📝 Vertices: {len(coords)-1}
"""

ax5.text(0.1, 0.5, stats_text, fontsize=11, family='monospace',
        verticalalignment='center',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.suptitle('Coimbatore City - Custom Boundary Analysis', 
            fontsize=18, fontweight='bold', y=0.98)

plt.savefig('coimbatore_custom_boundary_analysis.png', dpi=300, bbox_inches='tight')
print(f"\n✅ Visualization saved: coimbatore_custom_boundary_analysis.png")

# Save cleaned version with metadata
coimbatore_gdf['area_km2'] = area_km2
coimbatore_gdf['perimeter_km'] = perimeter_km
coimbatore_gdf['created_date'] = datetime.now().strftime("%Y-%m-%d")
coimbatore_gdf['source'] = 'custom_polygon'

final_path = "data/gemini_coimbatore_boundary_clean.geojson"
coimbatore_gdf.to_file(final_path, driver="GeoJSON")
print(f"✅ Final boundary saved: {final_path}")

print(f"\n{'='*60}")
print("🎉 CUSTOM BOUNDARY LOADED SUCCESSFULLY!")
print(f"{'='*60}")
print(f"✅ Ready for use in clipping operations")
print(f"✅ Compatible with raster clipping")
print(f"✅ All standard zones covered: {inside_count}/{len(COIMBATORE_ZONES)}")

try:
    plt.show()
except:
    print("⚠️  Display not available (running in headless mode)")