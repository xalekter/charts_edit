# FM-Trace Data Editor

A comprehensive web-based tool for analyzing and editing phenological (seasonal timing) research data with interactive visualizations, species/site filtering, and precision editing capabilities.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Dash](https://img.shields.io/badge/Dash-Latest-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

##  Features

###  **Interactive Data Visualization**
- **Connected trend lines** showing seasonal progression
- **Dual Y-axes** with mean reference levels
- **Real-time statistics** (mean, std dev, range, point count)
- **Professional-grade plots** ready for publication

###  **Advanced Filtering System**
- **Species filtering** (Sc column) - Compare different organisms
- **Site filtering** (SiteC column) - Compare research locations
- **Description filtering** - Focus on specific phenological stages
- **Multi-selection support** with color-coded visualization

### **Phenological Markers**
- **Custom date markers** - Add important DOY (Day of Year) dates
- **Quick presets** - Spring Start, Peak Growing, Autumn Start, Winter Start
- **Color-coded markers** - 8 different colors with visual indicators
- **Vertical reference lines** - Clear seasonal context for data editing

### **Precision Point Editing**
- **Click-to-select** - Click any point to start editing
- **Fine-tune controls** - Arrow buttons for precise adjustments
- **Custom step sizes** - Set exact increment values
- **Add/remove points** - Complete data manipulation capabilities
- **Undo functionality** - Reset to original data anytime

###  **Data Management**
- **Drag & drop upload** - Easy file loading
- **Tab-separated format** - Standard scientific data format
- **20-row preview** - Enhanced data table with filtering
- **Download modified data** - Export your edited datasets

##  Quick Start

### Installation

```bash
# Clone or download the project
git clone https://github.com/xalekter/charts_edit.git
cd charts_edit

# Install required packages
pip install dash plotly pandas

# Run the application
python charts_edit.py
```

### Launch

```bash
python charts_edit.py
```

Open your browser and navigate to: `http://127.0.0.1:8050`

##  Data Format Requirements

Your data file should be a **tab-separated** (.txt) or comma-separated (.csv) file with the following structure:

### Required Columns
- **DOY** - Day of Year (1-365)
- **Numeric columns** - Any measurement data (e.g., leaf_mass, chlorophyll content)

### Optional Columns (for filtering)
- **Sc** - Species codes (e.g., "KS", "Oak", "Pine")
- **SiteC** - Site codes (e.g., "Forest_A", "Field_B", "Plot_1")
- **Description** - Phenological stage descriptions (e.g., "First Buds", "50% Leaf Development")

### Example Data Structure
```
Sc	Date	DOY	Description	leaf_mass	SLW	chlorp3.dat
KS	20/03/2025	80	Spring Start	0.01	0.30	0.5
KS	01/05/2025	121	Peak Growing	0.3	0.70	1.0
Oak	15/06/2025	166	Full Foliage	0.8	0.85	1.2
```

##  Usage Guide

### 1. **Load Your Data**
- Drag and drop your .txt or .csv file into the upload area
- The system automatically detects tab or comma separation
- Column options populate automatically

### 2. **Set Up Filtering** (Optional)
- **Species Filter**: Select one or multiple species to compare
- **Site Filter**: Choose research locations to analyze
- **Description Filter**: Focus on specific phenological stages

### 3. **Add Phenological Markers** (Optional)
- Use quick presets: Spring Start (DOY 80), Peak Growing (DOY 150), etc.
- Add custom markers: Enter DOY + label + color
- Markers appear as vertical lines with labels

### 4. **Create Your Plot**
- Select X-axis (typically DOY) and Y-axis (your measurement)
- Click "Create Plot" to generate interactive visualization
- Connected lines show seasonal progression

### 5. **Edit Your Data**
- **Select points**: Click red circles to select for editing
- **Fine-tune**: Use arrow buttons ( for X,  for Y)
- **Manual edit**: Enter exact values in input fields
- **Add points**: Enter coordinates and click "Add Point"
- **Remove points**: Select point and click "Delete"

### 6. **Download Results**
- Click "Download Modified Data" to save your edited dataset
- File saves in tab-separated format (.txt)

##  Advanced Features

### Multi-Species/Site Comparison
- Select multiple species or sites for overlay comparison
- Each group gets a different color automatically
- Perfect for comparative phenological studies

### Precision Editing Tools
- **Step size control**: Set custom increment values (0.1, 1, 5, etc.)
- **Arrow buttons**: Move points incrementally
- **Direct input**: Enter exact scientific values
- **Real-time updates**: See changes immediately

### Statistical Analysis
- **Live statistics**: Mean, standard deviation, range update automatically
- **Filtered statistics**: Stats calculated only on visible/filtered data
- **Mean reference line**: Green dashed line shows average level
- **Secondary axis**: Mean level in arbitrary units

##  Workflow Examples

### Example 1: Single Species Analysis
1. Load data â Filter by Sc: "Oak" â Select DOY vs leaf_mass
2. Add marker: "Bud Break" at DOY 90
3. Create plot â Edit outliers â Download results

### Example 2: Multi-Site Comparison  
1. Load data â Filter by SiteC: "Forest_A", "Forest_B"
2. Add seasonal markers â Plot DOY vs chlorophyll
3. Compare timing between sites â Edit inconsistencies

### Example 3: Species Comparison
1. Load data â Filter by Sc: "Oak", "Pine", "Birch"
2. Plot DOY vs phenological development
3. Compare species timing â Identify species-specific patterns

## ð ï¸ Troubleshooting

### Common Issues

**"No data matches the selected filters"**
- Check if your filter selections are too restrictive
- Verify column names match exactly (case-sensitive)

**"NameError: name 'dash' is not defined"**
- Install required packages: `pip install dash plotly pandas`

**"Upload failed"**
- Ensure file is tab-separated or comma-separated
- Check for proper encoding (UTF-8 recommended)
- Verify file has header row with column names

**Points not clickable**
- Make sure to click on red circles (editable points)
- Blue line points are for trend display only

### Performance Tips
- For large datasets (>1000 points), use filtering to focus on subsets
- Close browser tabs/restart if performance degrades
- Use Chrome or Firefox for best compatibility

## ð¤ Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
```bash
git clone https://github.com/xalekter/charts_edit.git
cd charts_edit

pip install -r requirements.txt
```

---

**Made for the scientific community to advance phenological research** 
