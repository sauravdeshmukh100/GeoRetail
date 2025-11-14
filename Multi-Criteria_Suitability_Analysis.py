"""
GeoRetail Project - Step 6: Multi-Criteria Suitability Analysis
Calculate retail site suitability scores and identify top locations
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
import os
import warnings
warnings.filterwarnings('ignore')

print("""
🎯 GEORETAIL PROJECT - STEP 6
🏆 Multi-Criteria Suitability Analysis
📅 {}
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

# Create directories
os.makedirs("outputs/final", exist_ok=True)

# Step 6.1: Load Analysis Grid
print("\n" + "="*60)
print("STEP 6.1: Loading Analysis Grid")
print("="*60)

grid_gdf = gpd.read_file("data/processed/grid/analysis_grid_wgs84.geojson")
print(f"✅ Loaded grid: {len(grid_gdf)} cells with {len(grid_gdf.columns)} features")

# Display key statistics
print(f"\nKey Statistics:")
print(f"  Population: {grid_gdf['population'].sum():,.0f} total")
print(f"  Retail locations: {grid_gdf['retail_count_1km'].sum():.0f} total")
print(f"  High competition cells: {(grid_gdf['competition_score'] > 5).sum()}")

# Step 6.2: Define Suitability Criteria & Weights
print("\n" + "="*60)
print("STEP 6.2: Define Suitability Criteria")
print("="*60)

# Multi-Criteria Decision Analysis (MCDA) weights
criteria_weights = {
    'population_density': {
        'weight': 0.30,
        'direction': 'maximize',  # Higher is better
        'description': 'Market size potential'
    },
    'road_accessibility': {
        'weight': 0.20,
        'direction': 'maximize',  # Higher density + lower distance to highway
        'description': 'Customer accessibility'
    },
    'competition_level': {
        'weight': 0.15,
        'direction': 'minimize',  # Lower competition is better
        'description': 'Market saturation'
    },
    'amenity_proximity': {
        'weight': 0.20,
        'direction': 'maximize',  # More amenities = more foot traffic
        'description': 'Foot traffic potential'
    },
    'economic_activity': {
        'weight': 0.15,
        'direction': 'maximize',  # Banking presence indicates affluence
        'description': 'Purchasing power proxy'
    }
}

print("Suitability Criteria:")
for criterion, info in criteria_weights.items():
    print(f"  {criterion:25} : {info['weight']:.0%} ({info['description']})")

total_weight = sum([c['weight'] for c in criteria_weights.values()])
print(f"\nTotal weight: {total_weight:.0%}")

# Step 6.3: Normalize Features
print("\n" + "="*60)
print("STEP 6.3: Normalizing Features (0-1 scale)")
print("="*60)

scaler = MinMaxScaler()

# Population density (maximize)
grid_gdf['pop_density_norm'] = scaler.fit_transform(
    grid_gdf[['pop_density']]
).flatten()

# Road accessibility (composite: high density + low distance to highway)
# Normalize road density (maximize)
grid_gdf['road_density_norm'] = scaler.fit_transform(
    grid_gdf[['road_density_km_per_km2']]
).flatten()

# Normalize distance to highway (minimize - invert)
grid_gdf['highway_proximity_norm'] = 1 - scaler.fit_transform(
    grid_gdf[['dist_to_major_road_m']]
).flatten()

# Combine into single accessibility score
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

# Economic activity (banking as proxy - maximize)
grid_gdf['economic_activity_norm'] = scaler.fit_transform(
    grid_gdf[['banking_count_1km']]
).flatten()

print("✅ All features normalized to 0-1 scale")

# Step 6.4: Calculate Suitability Score
print("\n" + "="*60)
print("STEP 6.4: Calculating Overall Suitability Score")
print("="*60)

grid_gdf['suitability_score'] = (
    criteria_weights['population_density']['weight'] * grid_gdf['pop_density_norm'] +
    criteria_weights['road_accessibility']['weight'] * grid_gdf['road_accessibility_norm'] +
    criteria_weights['competition_level']['weight'] * grid_gdf['competition_norm'] +
    criteria_weights['amenity_proximity']['weight'] * grid_gdf['amenity_proximity_norm'] +
    criteria_weights['economic_activity']['weight'] * grid_gdf['economic_activity_norm']
)

# Convert to 0-100 scale for easier interpretation
grid_gdf['suitability_score_100'] = grid_gdf['suitability_score'] * 100

print(f"✅ Suitability scores calculated")
print(f"\nScore Distribution:")
print(f"  Mean: {grid_gdf['suitability_score_100'].mean():.2f}")
print(f"  Median: {grid_gdf['suitability_score_100'].median():.2f}")
print(f"  Max: {grid_gdf['suitability_score_100'].max():.2f}")
print(f"  Min: {grid_gdf['suitability_score_100'].min():.2f}")
print(f"  Std Dev: {grid_gdf['suitability_score_100'].std():.2f}")

# Step 6.5: Classify Suitability Levels
print("\n" + "="*60)
print("STEP 6.5: Classifying Suitability Levels")
print("="*60)

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

class_counts = grid_gdf['suitability_class'].value_counts()
print("Suitability Classification:")
for class_name in ['Excellent', 'Very Good', 'Good', 'Moderate', 'Low']:
    count = class_counts.get(class_name, 0)
    percentage = (count / len(grid_gdf)) * 100
    print(f"  {class_name:12} : {count:4} cells ({percentage:5.1f}%)")

# Step 6.6: Identify Top Locations
print("\n" + "="*60)
print("STEP 6.6: Identifying Top Retail Locations")
print("="*60)

# Get top 20 locations
top_locations = grid_gdf.nlargest(20, 'suitability_score_100').copy()

# Add rank
top_locations['rank'] = range(1, len(top_locations) + 1)

print(f"🏆 TOP 20 RETAIL SITE RECOMMENDATIONS:\n")
print(f"{'Rank':<6}{'Score':<8}{'Pop Density':<12}{'Competition':<12}{'Amenities':<10}{'Class':<12}")
print("-" * 70)

for idx, row in top_locations.iterrows():
    print(f"{row['rank']:<6}{row['suitability_score_100']:>6.1f}  "
          f"{row['pop_density']:>10.0f}  {row['competition_score']:>10.0f}  "
          f"{row['amenity_score']:>8.1f}  {row['suitability_class']:<12}")

# Save top locations
top_locations_file = "data/processed/grid/top_20_locations.geojson"
top_locations.to_file(top_locations_file, driver="GeoJSON")
print(f"\n✅ Top 20 locations saved: {top_locations_file}")

# Also save as CSV for easy viewing
top_locations_csv = top_locations[[
    'rank', 'cell_id', 'suitability_score_100', 'suitability_class',
    'population', 'pop_density', 'competition_score', 'amenity_score',
    'road_density_km_per_km2', 'banking_count_1km'
]].drop(columns=['geometry'], errors='ignore')

csv_file = "outputs/final/top_20_locations.csv"
top_locations_csv.to_csv(csv_file, index=False)
print(f"✅ Top 20 locations CSV saved: {csv_file}")

# Step 6.7: Market Gap Analysis
print("\n" + "="*60)
print("STEP 6.7: Market Gap Analysis")
print("="*60)

# Identify underserved areas (high population, low competition, good accessibility)
grid_gdf['market_gap_score'] = (
    grid_gdf['pop_density_norm'] * 0.4 +
    grid_gdf['competition_norm'] * 0.4 +
    grid_gdf['road_accessibility_norm'] * 0.2
) * 100

underserved_areas = grid_gdf[
    (grid_gdf['market_gap_score'] > 60) &
    (grid_gdf['competition_score'] < 3) &
    (grid_gdf['population'] > 1000)
].copy()

print(f"🎯 UNDERSERVED MARKET OPPORTUNITIES:")
print(f"   Total underserved cells: {len(underserved_areas)}")
print(f"   Total underserved population: {underserved_areas['population'].sum():,.0f}")
print(f"   Mean competition in these areas: {underserved_areas['competition_score'].mean():.2f}")

if len(underserved_areas) > 0:
    underserved_file = "data/processed/grid/underserved_areas.geojson"
    underserved_areas.to_file(underserved_file, driver="GeoJSON")
    print(f"✅ Underserved areas saved: {underserved_file}")

# Step 6.8: Create Comprehensive Visualizations
print("\n" + "="*60)
print("STEP 6.8: Creating Final Visualizations")
print("="*60)

# Load boundary for overlay
boundary_gdf = gpd.read_file("data/coimbatore_boundary_clean.geojson")

# Visualization 1: Suitability Score Map with Top Locations
fig, axes = plt.subplots(2, 2, figsize=(20, 18))

# Plot 1: Overall Suitability Score
ax1 = axes[0, 0]
grid_gdf.plot(column='suitability_score_100', ax=ax1, cmap='RdYlGn',
             legend=True, legend_kwds={'label': 'Suitability Score (0-100)', 'shrink': 0.8},
             edgecolor='gray', linewidth=0.1, alpha=0.8)
boundary_gdf.boundary.plot(ax=ax1, color='black', linewidth=2)

# Overlay top 5 locations
top_5 = top_locations.head(5)
top_5_centroids = top_5.geometry.centroid
ax1.scatter(top_5_centroids.x, top_5_centroids.y, c='red', s=300, marker='*',
           edgecolor='black', linewidth=2, zorder=5, label='Top 5 Sites')

# Label top 5
for idx, row in top_5.iterrows():
    centroid = row.geometry.centroid
    ax1.annotate(f"#{row['rank']}", (centroid.x, centroid.y),
                fontsize=12, fontweight='bold', ha='center', va='center',
                bbox=dict(boxstyle='circle', facecolor='yellow', alpha=0.8))

ax1.set_title('Retail Site Suitability Score', fontsize=14, fontweight='bold')
ax1.legend(loc='upper right')
ax1.axis('off')

# Plot 2: Suitability Classification
ax2 = axes[0, 1]
class_colors = {'Excellent': '#2d7f3e', 'Very Good': '#74c476', 
                'Good': '#fed976', 'Moderate': '#feb24c', 'Low': '#fc4e2a'}
grid_gdf.plot(column='suitability_class', ax=ax2, categorical=True,
             legend=True, cmap='RdYlGn',
             edgecolor='gray', linewidth=0.1, alpha=0.8)
boundary_gdf.boundary.plot(ax=ax2, color='black', linewidth=2)
ax2.set_title('Suitability Classification', fontsize=14, fontweight='bold')
ax2.axis('off')

# Plot 3: Market Gap Opportunities
ax3 = axes[1, 0]
grid_gdf.plot(column='market_gap_score', ax=ax3, cmap='YlOrRd',
             legend=True, legend_kwds={'label': 'Market Gap Score', 'shrink': 0.8},
             edgecolor='gray', linewidth=0.1, alpha=0.8)
boundary_gdf.boundary.plot(ax=ax3, color='black', linewidth=2)

# Highlight underserved areas
if len(underserved_areas) > 0:
    underserved_areas.boundary.plot(ax=ax3, color='blue', linewidth=2, 
                                    label='Underserved Areas')
    ax3.legend(loc='upper right')

ax3.set_title('Market Gap Analysis\n(High Demand, Low Competition)', 
             fontsize=14, fontweight='bold')
ax3.axis('off')

# Plot 4: Top 20 Locations Detail
ax4 = axes[1, 1]
grid_gdf.plot(ax=ax4, facecolor='lightgray', edgecolor='gray', 
             linewidth=0.1, alpha=0.3)
boundary_gdf.boundary.plot(ax=ax4, color='black', linewidth=2)

# Plot top 20 with color gradient
top_20_centroids = top_locations.geometry.centroid
scatter = ax4.scatter(top_20_centroids.x, top_20_centroids.y,
                     c=top_locations['rank'], cmap='RdYlGn_r',
                     s=top_locations['suitability_score_100'] * 5,
                     edgecolor='black', linewidth=2, alpha=0.8)

# Label top 10
for idx, row in top_locations.head(10).iterrows():
    centroid = row.geometry.centroid
    ax4.annotate(f"#{row['rank']}", (centroid.x, centroid.y),
                fontsize=10, fontweight='bold', ha='center', va='center',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

plt.colorbar(scatter, ax=ax4, label='Rank (1=Best)', shrink=0.6)
ax4.set_title('Top 20 Recommended Locations', fontsize=14, fontweight='bold')
ax4.axis('off')

plt.suptitle('Coimbatore Retail Site Suitability Analysis - Final Results', 
            fontsize=18, fontweight='bold', y=0.995)
plt.tight_layout()

output_viz1 = "outputs/final/suitability_analysis_final.png"
plt.savefig(output_viz1, dpi=300, bbox_inches='tight')
print(f"✅ Main visualization saved: {output_viz1}")

# Visualization 2: Criteria Breakdown for Top 5 Locations
fig2, axes2 = plt.subplots(1, 2, figsize=(18, 8))

# Radar chart for top 5 locations
ax_radar = axes2[0]
categories = ['Population\nDensity', 'Road\nAccessibility', 
              'Low\nCompetition', 'Amenity\nProximity', 'Economic\nActivity']

angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
angles += angles[:1]

ax_radar = plt.subplot(121, projection='polar')
colors_radar = plt.cm.Set3(np.linspace(0, 1, 5))

for i, (idx, row) in enumerate(top_5.iterrows()):
    values = [
        row['pop_density_norm'],
        row['road_accessibility_norm'],
        row['competition_norm'],
        row['amenity_proximity_norm'],
        row['economic_activity_norm']
    ]
    values += values[:1]
    
    ax_radar.plot(angles, values, 'o-', linewidth=2, label=f"Rank #{row['rank']}", 
                 color=colors_radar[i])
    ax_radar.fill(angles, values, alpha=0.15, color=colors_radar[i])

ax_radar.set_xticks(angles[:-1])
ax_radar.set_xticklabels(categories, size=10)
ax_radar.set_ylim(0, 1)
ax_radar.set_title('Top 5 Locations - Criteria Comparison', 
                  fontsize=14, fontweight='bold', pad=20)
ax_radar.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
ax_radar.grid(True)

# Bar chart comparison
ax_bar = axes2[1]
top_10_for_bar = top_locations.head(10)

x = np.arange(len(top_10_for_bar))
width = 0.15

bars1 = ax_bar.bar(x - 2*width, top_10_for_bar['pop_density_norm'], 
                   width, label='Population', color='#e74c3c')
bars2 = ax_bar.bar(x - width, top_10_for_bar['road_accessibility_norm'], 
                   width, label='Accessibility', color='#3498db')
bars3 = ax_bar.bar(x, top_10_for_bar['competition_norm'], 
                   width, label='Low Competition', color='#2ecc71')
bars4 = ax_bar.bar(x + width, top_10_for_bar['amenity_proximity_norm'], 
                   width, label='Amenities', color='#f39c12')
bars5 = ax_bar.bar(x + 2*width, top_10_for_bar['economic_activity_norm'], 
                   width, label='Economic', color='#9b59b6')

ax_bar.set_xlabel('Location Rank', fontsize=12, fontweight='bold')
ax_bar.set_ylabel('Normalized Score', fontsize=12, fontweight='bold')
ax_bar.set_title('Top 10 Locations - Criteria Breakdown', 
                fontsize=14, fontweight='bold')
ax_bar.set_xticks(x)
ax_bar.set_xticklabels([f"#{row['rank']}" for _, row in top_10_for_bar.iterrows()])
ax_bar.legend()
ax_bar.grid(True, alpha=0.3, axis='y')

plt.tight_layout()

output_viz2 = "outputs/final/top_locations_criteria_analysis.png"
plt.savefig(output_viz2, dpi=300, bbox_inches='tight')
print(f"✅ Criteria analysis saved: {output_viz2}")

# Step 6.9: Generate Final Report
print("\n" + "="*60)
print("STEP 6.9: Generating Final Report")
print("="*60)

final_report = f"""
╔═══════════════════════════════════════════════════════════════╗
║     GEORETAIL PROJECT - FINAL SUITABILITY ANALYSIS REPORT     ║
║                  Coimbatore, Tamil Nadu, India                 ║
╚═══════════════════════════════════════════════════════════════╝

Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Analysis Coverage: {len(grid_gdf):,} grid cells ({grid_gdf.to_crs('EPSG:3857').geometry.area.sum()/1e6:.2f} km²)
Total Population Analyzed: {grid_gdf['population'].sum():,.0f}

═══════════════════════════════════════════════════════════════

📊 SUITABILITY SCORE DISTRIBUTION

Mean Score: {grid_gdf['suitability_score_100'].mean():.2f}/100
Median Score: {grid_gdf['suitability_score_100'].median():.2f}/100
Top Score: {grid_gdf['suitability_score_100'].max():.2f}/100

Classification Breakdown:
"""

for class_name in ['Excellent', 'Very Good', 'Good', 'Moderate', 'Low']:
    count = class_counts.get(class_name, 0)
    percentage = (count / len(grid_gdf)) * 100
    bar = '█' * int(percentage / 2)
    final_report += f"  {class_name:12} : {count:4} cells ({percentage:5.1f}%) {bar}\n"

final_report += f"""
═══════════════════════════════════════════════════════════════

🏆 TOP 10 RECOMMENDED RETAIL LOCATIONS

{'Rank':<6}{'Score':<8}{'Pop/km²':<12}{'Competition':<13}{'Amenities':<10}{'Class':<12}
{'-'*70}
"""

for idx, row in top_locations.head(10).iterrows():
    final_report += f"{row['rank']:<6}{row['suitability_score_100']:>6.1f}  {row['pop_density']:>10,.0f}  {row['competition_score']:>11.0f}  {row['amenity_score']:>8.1f}  {row['suitability_class']:<12}\n"

final_report += f"""
═══════════════════════════════════════════════════════════════

🎯 MARKET GAP ANALYSIS

Underserved Market Opportunities:
- Total underserved cells: {len(underserved_areas):,}
- Population in underserved areas: {underserved_areas['population'].sum():,.0f}
- Average competition: {underserved_areas['competition_score'].mean():.2f} stores/cell
- Market potential: HIGH ✅

═══════════════════════════════════════════════════════════════

📈 KEY INSIGHTS & RECOMMENDATIONS

1. MARKET CONCENTRATION
   - {(grid_gdf['competition_score'] > 5).sum():,} cells have high retail concentration (>5 stores)
   - {(grid_gdf['competition_score'] == 0).sum():,} cells have NO retail presence
   - Opportunity: Focus on underserved high-population areas

2. POPULATION HOTSPOTS
   - Peak density: {grid_gdf['pop_density'].max():,.0f} people/km²
   - {(grid_gdf['pop_density'] > 5000).sum():,} cells with >5000 people/km²
   - These areas show strong market demand

3. ACCESSIBILITY
   - {(grid_gdf['dist_to_major_road_m'] < 500).sum():,} cells within 500m of major roads
   - Good accessibility across {(grid_gdf['road_density_km_per_km2'] > 15).sum():,} cells
   - Road network supports retail distribution

4. FOOT TRAFFIC
   - Top amenity cluster score: {grid_gdf['amenity_score'].max():.1f}
   - {(grid_gdf['amenity_score'] > 10).sum():,} cells with high foot traffic potential
   - Education & healthcare drive consistent traffic

═══════════════════════════════════════════════════════════════

💡 STRATEGIC RECOMMENDATIONS

Priority 1: IMMEDIATE OPPORTUNITIES (Top 5 Locations)
→ Locations ranked #1-#5 offer optimal balance of:
  • High population density
  • Moderate competition
  • Excellent accessibility
  • Strong amenity presence

Priority 2: MARKET GAP OPPORTUNITIES
→ {len(underserved_areas):,} underserved locations with:
  • Population: {underserved_areas['population'].sum():,.0f}
  • Low competition: Avg {underserved_areas['competition_score'].mean():.1f} competitors
  • Growth potential: HIGH

Priority 3: COMPETITIVE ENTRY
→ Enter established markets (#6-#10) with:
  • Differentiated offerings
  • Superior service quality
  • Strategic positioning

═══════════════════════════════════════════════════════════════

📁 OUTPUT FILES

Analysis Results:
✅ data/processed/grid/top_20_locations.geojson
✅ data/processed/grid/underserved_areas.geojson
✅ outputs/final/top_20_locations.csv

Visualizations:
✅ outputs/final/suitability_analysis_final.png
✅ outputs/final/top_locations_criteria_analysis.png

Reports:
✅ outputs/final/georetail_final_report.txt

═══════════════════════════════════════════════════════════════

✅ PROJECT COMPLETE: GeoRetail Suitability Analysis

Next Steps:
1. Field verification of top 5 locations
2. Detailed market research for shortlisted sites
3. Real estate feasibility assessment
4. Business plan development

═══════════════════════════════════════════════════════════════
"""

report_file = "outputs/final/georetail_final_report.txt"
with open(report_file, 'w') as f:
    f.write(final_report)

print(final_report)
print(f"\n✅ Final report saved: {report_file}")

print("\n" + "="*60)
print("🎉🎉🎉 PROJECT COMPLETE! 🎉🎉🎉")
print("="*60)
print("\n📦 ALL DELIVERABLES READY:")
print("   • Suitability maps with top 20 locations")
print("   • Market gap analysis")
print("   • Detailed criteria breakdowns")
print("   • Comprehensive final report")
print("\n🎯 You now have data-driven retail site recommendations!")

try:
    plt.show()
except:
    print("⚠️  Display not available (headless mode)")