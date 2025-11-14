"""
GeoRetail Project - Step 2: Population Data Collection
Collect and process population data for Coimbatore city
"""

import rasterio
from rasterio.mask import mask
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import requests
import os

print("""
🎯 GEORETAIL PROJECT - STEP 2
📊 Population Data Collection for Coimbatore
📅 {}
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

# Create directories
os.makedirs("data", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Load Coimbatore boundary
print("Loading Coimbatore boundary...")
boundary_gdf = gpd.read_file("data/coimbatore_boundary_clean.geojson")
print(f"✅ Boundary loaded: {boundary_gdf.geometry.area.sum()/1e6:.2f} km²")

# Step 2.1: Download WorldPop Data
print("\n" + "="*60)
print("STEP 2.1: WorldPop Population Data")
print("="*60)

worldpop_url_india = "https://data.worldpop.org/GIS/Population/Global_2000_2020_1km/2020/IND/ind_ppp_2020_1km_Aggregated.tif"

worldpop_file = "data/worldpop_india_2020.tif"

if not os.path.exists(worldpop_file):
    print(f"📥 Downloading WorldPop data for India...")
    print(f"URL: {worldpop_url_india}")
    print("⚠️  This file is ~500MB, may take several minutes...")
    
    try:
        response = requests.get(worldpop_url_india, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(worldpop_file, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rProgress: {percent:.1f}%", end="")
        
        print("\n✅ Download complete!")
    except Exception as e:
        print(f"❌ Download failed: {e}")
        print("\nMANUAL DOWNLOAD INSTRUCTIONS:")
        print("1. Visit: https://hub.worldpop.org/geodata/listing?id=78")
        print("2. Download 'India 2020 1km Population' dataset")
        print(f"3. Save as: {worldpop_file}")
        exit(1)
else:
    print(f"✅ WorldPop file already exists: {worldpop_file}")

# Step 2.2: Clip Population Raster to Coimbatore
print("\n" + "="*60)
print("STEP 2.2: Clip Population Data to Coimbatore")
print("="*60)

output_file = "data/processed/coimbatore_population.tif"

if not os.path.exists(output_file):
    print("Clipping raster to Coimbatore boundary...")
    
    with rasterio.open(worldpop_file) as src:
        print(f"Source raster CRS: {src.crs}")
        print(f"Source raster shape: {src.shape}")
        
        # Reproject boundary to match raster CRS if needed
        if boundary_gdf.crs != src.crs:
            print(f"Reprojecting boundary from {boundary_gdf.crs} to {src.crs}")
            boundary_gdf_proj = boundary_gdf.to_crs(src.crs)
        else:
            boundary_gdf_proj = boundary_gdf
        
        # Clip raster
        out_image, out_transform = mask(
            src, 
            boundary_gdf_proj.geometry, 
            crop=True,
            nodata=src.nodata
        )
        
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform,
            "compress": "lzw"
        })
        
        # Save clipped raster
        with rasterio.open(output_file, "w", **out_meta) as dest:
            dest.write(out_image)
        
        print(f"✅ Clipped population raster saved: {output_file}")
        print(f"Output shape: {out_image.shape}")
else:
    print(f"✅ Clipped population file already exists: {output_file}")

# Step 2.3: Calculate Population Statistics
print("\n" + "="*60)
print("STEP 2.3: Population Statistics")
print("="*60)

with rasterio.open(output_file) as src:
    pop_data = src.read(1)
    
    # Remove nodata values
    pop_data_valid = pop_data[pop_data > 0]
    
    total_population = pop_data_valid.sum()
    mean_density = pop_data_valid.mean()
    max_density = pop_data_valid.max()
    
    print(f"📊 Population Statistics:")
    print(f"Total Population: {total_population:,.0f}")
    print(f"Mean Density: {mean_density:.2f} people/pixel")
    print(f"Max Density: {max_density:.2f} people/pixel")
    print(f"Pixel Resolution: ~{src.res[0]*111:.0f}m × {src.res[1]*111:.0f}m")

# Step 2.4: Visualize Population Data
print("\n" + "="*60)
print("STEP 2.4: Creating Visualizations")
print("="*60)

fig, axes = plt.subplots(2, 2, figsize=(16, 14))

# Plot 1: Population Density Map
with rasterio.open(output_file) as src:
    pop_data = src.read(1)
    pop_data_masked = np.ma.masked_where(pop_data <= 0, pop_data)
    
    im1 = axes[0, 0].imshow(pop_data_masked, cmap='YlOrRd', interpolation='nearest')
    axes[0, 0].set_title('Population Density - Coimbatore', fontsize=14, fontweight='bold')
    plt.colorbar(im1, ax=axes[0, 0], label='People per pixel')
    axes[0, 0].axis('off')

# Plot 2: Population Density with Boundary Overlay
with rasterio.open(output_file) as src:
    from rasterio.plot import show
    show(src, ax=axes[0, 1], cmap='YlOrRd', title='Population with City Boundary')
    
    # Overlay boundary
    boundary_gdf_plot = boundary_gdf.to_crs(src.crs)
    boundary_gdf_plot.boundary.plot(ax=axes[0, 1], color='blue', linewidth=2)
    axes[0, 1].set_title('Population Density with Boundary', fontsize=14, fontweight='bold')

# Plot 3: Population Distribution Histogram
axes[1, 0].hist(pop_data_valid, bins=50, color='steelblue', edgecolor='black', alpha=0.7)
axes[1, 0].set_xlabel('Population per pixel', fontsize=12)
axes[1, 0].set_ylabel('Frequency', fontsize=12)
axes[1, 0].set_title('Population Distribution', fontsize=14, fontweight='bold')
axes[1, 0].grid(True, alpha=0.3)

# Plot 4: Statistics Summary
axes[1, 1].axis('off')
stats_text = f"""
POPULATION DATA SUMMARY

📊 Total Population: {total_population:,.0f}

📈 Density Statistics:
   Mean: {mean_density:.2f} people/pixel
   Max: {max_density:.2f} people/pixel
   Min: {pop_data_valid.min():.2f} people/pixel
   Std Dev: {pop_data_valid.std():.2f}

📐 Data Resolution:
   Pixel size: ~{src.res[0]*111:.0f}m × {src.res[1]*111:.0f}m
   Grid cells: {pop_data.shape[0]} × {pop_data.shape[1]}

✅ Data Source: WorldPop 2020
✅ Coverage: Coimbatore Municipal Corporation
"""

axes[1, 1].text(0.1, 0.5, stats_text, fontsize=11, family='monospace',
               verticalalignment='center',
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))

plt.suptitle('Coimbatore Population Analysis - GeoRetail Project', 
            fontsize=16, fontweight='bold', y=0.98)
plt.tight_layout()

output_viz = "outputs/step2_population_analysis.png"
plt.savefig(output_viz, dpi=300, bbox_inches='tight')
print(f"✅ Visualization saved: {output_viz}")

# Step 2.5: Save Summary Report
print("\n" + "="*60)
print("STEP 2.5: Saving Summary Report")
print("="*60)

summary_report = f"""
GEORETAIL PROJECT - POPULATION DATA COLLECTION REPORT
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

=== DATA COLLECTION SUMMARY ===

1. Data Source: WorldPop 2020 (1km resolution)
2. Coverage Area: Coimbatore Municipal Corporation
3. Total Population: {total_population:,.0f}

=== STATISTICS ===

Population Density:
- Mean: {mean_density:.2f} people/pixel
- Maximum: {max_density:.2f} people/pixel
- Minimum: {pop_data_valid.min():.2f} people/pixel
- Standard Deviation: {pop_data_valid.std():.2f}

Spatial Coverage:
- Raster dimensions: {pop_data.shape[0]} × {pop_data.shape[1]} pixels
- Pixel resolution: ~{src.res[0]*111:.0f}m × {src.res[1]*111:.0f}m
- Total area covered: {boundary_gdf.to_crs('EPSG:3857').geometry.area.sum()/1e6:.2f} km²

=== OUTPUT FILES ===

1. Clipped Population Raster: data/processed/coimbatore_population.tif
2. Visualization: outputs/step2_population_analysis.png
3. This report: outputs/step2_population_report.txt

=== NEXT STEPS ===

✅ Step 2 Complete: Population Data Collected
➡️  Step 3: Road Network & Transportation Data
➡️  Step 4: Amenities & Points of Interest (POI) Data
➡️  Step 5: Create Analysis Grid
➡️  Step 6: Feature Engineering
"""

report_file = "outputs/step2_population_report.txt"
with open(report_file, 'w') as f:
    f.write(summary_report)

print(summary_report)
print(f"✅ Report saved: {report_file}")

print("\n" + "="*60)
print("🎉 STEP 2 COMPLETE: POPULATION DATA COLLECTED!")
print("="*60)
print("\n📋 FILES CREATED:")
print(f"   1. {output_file}")
print(f"   2. {output_viz}")
print(f"   3. {report_file}")
print("\n➡️  NEXT: Run Step 3 - Road Network Collection")

try:
    plt.show()
except:
    print("⚠️  Display not available (headless mode)")