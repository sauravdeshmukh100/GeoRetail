
# GeoRetail - Coimbatore Retail Site Selection

Data-driven retail location analysis using open-source geospatial data and multi-criteria decision analysis.

## 📊 Project Overview

**Analysis Date**: October 03, 2025
**Study Area**: Coimbatore Municipal Corporation, Tamil Nadu, India
**Coverage**: 450.5 km² (1,802 grid cells)
**Population Analyzed**: 1,579,442

## 🎯 Key Results

- **Top Suitability Score**: 65.6/100
- **Top 20 Locations Identified**
- **104 Underserved Market Opportunities**
- **1,266 Areas with Zero Competition**

## 📁 Repository Structure

```
georetail_project/
├── data/
│   ├── coimbatore_boundary_clean.geojson
│   └── processed/
│       ├── coimbatore_population.tif
│       ├── coimbatore_roads.geojson
│       ├── amenities/
│       │   ├── retail.geojson
│       │   ├── education.geojson
│       │   ├── healthcare.geojson
│       │   └── banking.geojson
│       └── grid/
│           ├── analysis_grid_wgs84.geojson
│           ├── top_20_locations.geojson
│           └── underserved_areas.geojson
│
├── outputs/
│   ├── final/
│   │   ├── maps/
│   │   │   └── georetail_interactive_map.html ⭐
│   │   ├── documentation/
│   │   │   ├── 00_Quick_Start.txt
│   │   │   ├── 01_Executive_Summary.txt
│   │   │   ├── 02_Technical_Methodology.txt
│   │   │   └── 03_User_Guide.txt
│   │   ├── top_20_locations.csv
│   │   ├── suitability_analysis_final.png
│   │   └── top_locations_criteria_analysis.png
│   │
│   ├── step2_population_analysis.png
│   ├── step3_road_network_analysis.png
│   ├── step4_amenities_poi_analysis.png
│   └── step5_grid_features_analysis.png
│
├── dashboard_app.py
└── README.md (this file)
```

## 🚀 Quick Start

### View Interactive Map
```bash
# Open in browser
open outputs/final/maps/georetail_interactive_map.html
```

### Run Dashboard
```bash
# Install dependencies
pip install dash plotly geopandas pandas

# Run dashboard
python dashboard_app.py

# Open browser to http://127.0.0.1:8050/
```

### View Results
```bash
# Top locations (spreadsheet)
open outputs/final/top_20_locations.csv

# Read documentation
cat outputs/final/documentation/00_Quick_Start.txt
```

## 📋 Top 5 Recommended Locations

1. **Rank #1** - Score: 65.6/100
   - Population Density: 78,046 people/km²
   - Competition: 25 stores
   - Rating: Very Good

2. **Rank #2** - Score: 61.2/100
   - Population Density: 72,483 people/km²
   - Competition: 0 stores
   - Rating: Very Good

3. **Rank #3** - Score: 61.0/100
   - Population Density: 74,363 people/km²
   - Competition: 0 stores
   - Rating: Very Good

4. **Rank #4** - Score: 56.9/100
   - Population Density: 59,914 people/km²
   - Competition: 15 stores
   - Rating: Good

5. **Rank #5** - Score: 56.1/100
   - Population Density: 62,044 people/km²
   - Competition: 0 stores
   - Rating: Good

## 🛠️ Methodology

### Data Sources (100% Free/Open)
- **Population**: WorldPop 2020 (1km resolution)
- **Roads**: OpenStreetMap via OSMnx
- **POIs**: OpenStreetMap (retail, education, healthcare, banking)
- **Boundaries**: Custom digitized

### Analysis Framework
- **Grid Size**: 500m × 500m cells
- **Analysis Method**: Multi-Criteria Decision Analysis (MCDA)
- **Criteria Weights**:
  - Population Density: 30%
  - Road Accessibility: 20%
  - Competition Level: 15% (inverse)
  - Amenity Proximity: 20%
  - Economic Activity: 15%

### Key Features Calculated
- 27 features per grid cell
- Population density and totals
- Road network accessibility
- Competition intensity
- Amenity proximity scores
- Economic activity indicators

## 📚 Documentation

- **Quick Start**: `outputs/final/documentation/00_Quick_Start.txt`
- **Executive Summary**: `outputs/final/documentation/01_Executive_Summary.txt`
- **Technical Methodology**: `outputs/final/documentation/02_Technical_Methodology.txt`
- **User Guide**: `outputs/final/documentation/03_User_Guide.txt`

## 🎨 Visualizations

- Interactive HTML Map (Folium)
- Web Dashboard (Plotly Dash)
- Static Analysis Maps (PNG)
- Charts and Graphs (PNG)

## 💻 Requirements

```
python >= 3.7
geopandas
pandas
numpy
matplotlib
rasterio
osmnx
folium
dash
plotly
```

## 📊 Key Statistics

- **Grid Cells**: 1,802
- **Coverage Area**: 450.5 km²
- **Population**: 1,579,442
- **Mean Suitability**: 28.5/100
- **Underserved Areas**: 104
- **High Competition Cells**: 175
- **Zero Retail Cells**: 1,266

## 🎯 Next Steps

1. **Week 1**: Review analysis and share with stakeholders
2. **Week 2**: Field verification of top 5 locations
3. **Week 3**: Detailed feasibility studies
4. **Week 4**: Make go/no-go decisions

## 📧 Support

For questions or issues:
- Review documentation in `outputs/final/documentation/`
- Check methodology details
- Verify data file locations

## 📄 License

This analysis uses open-source data and tools:
- WorldPop: CC BY 4.0
- OpenStreetMap: ODbL
- Python libraries: Various open-source licenses

## 🙏 Acknowledgments

- WorldPop for population data
- OpenStreetMap contributors for spatial data
- OSMnx, GeoPandas, and other open-source projects

---

**Generated**: October 03, 2025 at 03:39 AM
