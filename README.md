# GHCN25py: Modernized Weather Station Analysis in Python

A comprehensive Python library for analyzing Global Historical Climatology Network - Daily (GHCN-D) data, modernized for Python 3.x compatibility with enhanced functionality and improved performance.

## 🚀 What's New in GHCN25py

**GHCN25py** is a complete modernization of the original GHCNpy library, updated by **[Shourya Sharma](https://github.com/shourya-sharma-33)** in **2025**. This library provides seamless access to the Global Historical Climatology Network - Daily Database with powerful analysis and visualization capabilities.

### ✨ Key Improvements

- **🐍 Python 3.11+ Compatible**: Fully migrated from Python 2.7 to modern Python
- **⚡ Enhanced Performance**: Optimized data processing with improved memory management  
- **🔧 Robust Error Handling**: Better exception handling and user feedback
- **📦 Modern Dependencies**: Updated to current versions of NumPy, requests, and scientific libraries
- **🌐 Improved Network Operations**: Reliable HTTP requests with better connection handling
- **📊 Better Data Structures**: Optimized NumPy arrays and efficient data manipulation

## 📖 About GHCN-Daily

The Global Historical Climatology Network – Daily (GHCN-D) dataset provides comprehensive daily climate observations from nearly **100,000 stations globally**. It serves as the official archive of daily weather data in the United States, updated nightly with strict quality assurance standards.

### 🌡️ Supported Climate Elements

GHCN25py focuses on the **CORE meteorological elements**:

| Element | Description | Units |
|---------|-------------|-------|
| **TMAX** | Daily Maximum Temperature | °C |
| **TMIN** | Daily Minimum Temperature | °C |
| **TAVG** | Daily Average Temperature | °C |
| **PRCP** | Daily Precipitation | mm |
| **SNOW** | Daily Snowfall | mm |
| **SNWD** | Daily Snow Depth | mm |

## 🛠️ Installation

### Prerequisites

- **Python**: 3.8+ (recommended: 3.11+)
- **Operating Systems**: Windows, macOS, Linux

### Required Dependencies

```bash
pip install numpy netcdf4 geopy requests matplotlib
```

### Install GHCN25py

```bash
git clone https://github.com/shourya-sharma-33/GHCN25py.git
cd GHCN25py
python setup.py install
```

### Verify Installation

```bash
python -c "import ghcn25py as gp; gp.intro()"
```

Expected output:
```
GHCNPy | year 2025 Fixed by Shourya Sharma (github: https://github.com/shourya-sharma-33)
Python 3.11 compatible package to analyze and display weather stations from GHCN-Daily
```

## 🚀 Quick Start

```python
import ghcn25py as gp

# Display library information
gp.intro()

# Get current GHCN-D version
version = gp.get_ghcnd_version()
print(f"Using GHCN-D version: {version}")

# Find stations near coordinates (lat, lon, distance_in_miles)
gp.find_station(40.7589, -73.9851, 25)  # New York City, 25-mile radius

# Get comprehensive station metadata
gp.get_metadata('USC00305798')

# Download and export station data
gp.output_to_csv('USC00305798')  # Export to CSV
```

## 📚 API Reference

### Module: `iotools.py` - Data Input/Output Operations

#### Core Data Retrieval Functions

**`get_ghcnd_version()`**
```python
version = gp.get_ghcnd_version()
```
- Retrieves the current GHCN-D dataset version
- **Returns**: `str` - Version identifier and timestamp
- **Output**: Creates local `ghcnd-version.txt` file

**`get_data_station(station_id)`**
```python
filename = gp.get_data_station('USC00305798')
```
- Downloads individual station data in GHCN-D ASCII format
- **Parameters**: `station_id` (str) - 12-character GHCN-D station identifier
- **Returns**: `str` - Local filename of downloaded `.dly` file
- **Output**: Creates `{station_id}.dly` file

**`get_data_year(year)`**
```python
filename = gp.get_data_year(2024)
```
- Downloads complete yearly dataset in compressed CSV format
- **Parameters**: `year` (int) - Target year for data retrieval
- **Returns**: `str` - Local filename of downloaded `.csv.gz` file
- **Output**: Creates `{year}.csv.gz` file

#### Metadata Retrieval Functions

**`get_ghcnd_stations()`**
```python
stations_array = gp.get_ghcnd_stations()
```
- Downloads complete station metadata file
- **Returns**: `numpy.ndarray` - Structured array with station information
- **Columns**: Station ID, Latitude, Longitude, Elevation, State, Name
- **Output**: Creates local `ghcnd-stations.txt` file

**`get_ghcnd_inventory()`**
```python
inventory_array = gp.get_ghcnd_inventory()
```
- Downloads data availability inventory for all stations
- **Returns**: `numpy.ndarray` - Array with data coverage information  
- **Columns**: Station ID, Latitude, Longitude, Element, First Year, Last Year
- **Output**: Creates local `ghcnd-inventory.txt` file

#### Data Export Functions

**`output_to_csv(station_id)`**
```python
gp.output_to_csv('USC00305798')
```
- Processes and exports station data to CSV format
- **Parameters**: `station_id` (str) - 12-character GHCN-D station identifier
- **Process**: Downloads `.dly` file, parses data, converts units, filters quality
- **Output**: Creates `{station_id}.csv` with columns: YYYY,MM,DD,TMAX,TMIN,PRCP,SNOW,SNWD
- **Features**: 
  - Automatic unit conversion (temperatures: tenths°C → °C, precipitation: tenths mm → mm)
  - Quality flag filtering (excludes flagged/suspect data)
  - Missing data handling (-9999.0 for invalid/missing values)

### Module: `metadata.py` - Station Discovery and Information

#### Station Search Functions

**`find_station(*args)`**

**Search by Name:**
```python
gp.find_station("DENVER")
```
- **Parameters**: `station_name` (str) - Station name (case-insensitive)
- **Output**: Formatted table of matching stations with ID, coordinates, elevation, state, and full name

**Search by Geographic Location:**
```python
gp.find_station(39.7392, -104.9903, 50)  # Denver area, 50-mile radius
```
- **Parameters**: 
  - `latitude` (float) - Decimal degrees
  - `longitude` (float) - Decimal degrees  
  - `distance_limit` (float) - Search radius in miles
- **Output**: Formatted table of stations within specified distance
- **Algorithm**: Uses great circle distance calculation via GeoPy

#### Station Metadata Functions

**`get_metadata(station_id)`**
```python
gp.get_metadata('USC00305798')
```
- Retrieves comprehensive station information from multiple sources
- **Parameters**: `station_id` (str) - 12-character GHCN-D station identifier
- **Data Sources**:
  - **GHCN-D Stations File**: Basic geographic and identification info
  - **HOMR (Historical Observing Metadata Repository)**: Extended administrative details
- **Output Information**:
  - Station coordinates (latitude/longitude) and elevation
  - Station name (processed and standardized)
  - Administrative details (state, county, climate division)
  - Network identifiers (COOP ID, WBAN ID)
  - National Weather Service office assignment
- **Error Handling**: Gracefully handles missing HOMR data, displays "N/A" for unavailable fields

## 🎯 Usage Examples

### Basic Weather Data Workflow

```python
import ghcn25py as gp

# 1. Find stations in your area of interest
print("Finding stations near Chicago...")
gp.find_station(41.8781, -87.6298, 30)

# 2. Get detailed information about a specific station
print("\nGetting metadata for Chicago O'Hare...")
gp.get_metadata('USW00094846')

# 3. Download and process the data
print("\nDownloading station data...")
station_file = gp.get_data_station('USW00094846')

# 4. Export to CSV for analysis
print("\nExporting to CSV format...")
gp.output_to_csv('USW00094846')

# 5. Check data version for documentation
version = gp.get_ghcnd_version()
print(f"\nUsing GHCN-D version: {version}")
```

### Climate Research Workflow

```python
import ghcn25py as gp
import pandas as pd

# Download multiple years of data for trend analysis
for year in range(2020, 2025):
    yearly_file = gp.get_data_year(year)
    print(f"Downloaded {yearly_file}")

# Process station data for specific analysis
stations_of_interest = ['USC00305798', 'USW00094846', 'USC00042294']

for station in stations_of_interest:
    print(f"\nProcessing station: {station}")
    gp.get_metadata(station)
    gp.output_to_csv(station)
    
    # Load processed CSV for further analysis
    df = pd.read_csv(f"{station}.csv")
    print(f"Data range: {df['YYYY'].min()}-{df['YYYY'].max()}")
    print(f"Total records: {len(df)}")
```

### Regional Station Discovery

```python
import ghcn25py as gp

# Define a geographic region (e.g., Colorado)
colorado_center = (39.0, -105.5)  # Approximate center of Colorado
search_radius = 200  # miles

print("Colorado Weather Stations:")
gp.find_station(colorado_center[0], colorado_center[1], search_radius)

# Get inventory to check data availability
inventory = gp.get_ghcnd_inventory()
print(f"\nTotal stations in inventory: {len(inventory)}")
```

## 🔧 Technical Implementation Details

### Python 2.7 → 3.11+ Migration Highlights

**Core Language Updates:**
- **Print Statements**: Converted all `print "text"` to `print("text")`
- **String Handling**: Updated to Python 3 Unicode standards and f-string formatting
- **Division Operations**: Implemented explicit true division (`/`) vs floor division (`//`)
- **Iterator Methods**: Replaced deprecated `dict.iteritems()` with `dict.items()`
- **Exception Handling**: Modernized `except Exception, e:` to `except Exception as e:`

**Library Modernization:**
- **HTTP Operations**: Migrated from `urllib2` to modern `requests` library with better error handling
- **File I/O**: Implemented context managers (`with` statements) for safer file operations
- **NumPy Integration**: Updated array operations and improved memory efficiency
- **Data Processing**: Enhanced string processing with modern regex and JSON handling

**Performance Improvements:**
- **Memory Management**: Optimized NumPy array allocation and reduced memory footprint
- **Network Efficiency**: Improved download mechanisms with proper connection handling
- **Error Recovery**: Better exception handling prevents crashes on network issues

### Data Processing Pipeline

1. **Download**: HTTP requests to NOAA servers with retry logic
2. **Parse**: Custom ASCII format parsing for `.dly` files
3. **Validate**: Quality flag checking and data validation
4. **Transform**: Unit conversions and missing data handling
5. **Export**: Structured output to CSV with proper formatting

## 🌟 Future Development Roadmap

### Planned Enhancements

- **📊 Advanced Analytics**: Statistical analysis tools and climate indices calculation
- **🗄️ Database Integration**: Local SQLite caching for improved performance
- **🌐 Web API**: RESTful service integration and real-time data access  
- **📈 Extended Visualizations**: Interactive plotting capabilities with modern libraries
- **🔍 Enhanced Search**: Fuzzy matching and advanced filtering options
- **📱 Jupyter Integration**: Interactive notebooks and tutorial development
- **⚡ Parallel Processing**: Multi-threaded downloads and concurrent data processing
- **🛠️ CLI Tools**: Command-line interface for batch operations

### Extended GHCN-D Elements Support

Future versions will include additional meteorological variables:
- Wind speed and direction
- Weather type observations  
- Extreme temperature indicators
- Derived climate indices (heating/cooling degree days)

## 🤝 Contributing

We welcome contributions to GHCN25py! Here's how you can help:

### Ways to Contribute
- **🐛 Bug Reports**: Submit issues with detailed reproduction steps
- **💡 Feature Requests**: Suggest new functionality or improvements
- **📝 Documentation**: Improve examples, tutorials, or API documentation
- **🧪 Testing**: Add test cases or validate functionality across platforms
- **💻 Code Contributions**: Submit pull requests with enhancements

### Development Setup
```bash
git clone https://github.com/shourya-sharma-33/GHCN25py.git
cd GHCN25py
pip install -r requirements-dev.txt
python -m pytest tests/
```

## 📄 License & Credits

### Credits
- **Original GHCNpy**: Developed by Jared Rennie for Python 2.7
- **GHCN25py Modernization**: [Shourya Sharma](https://github.com/shourya-sharma-33) (2025)
- **Data Provider**: NOAA National Centers for Environmental Information
- **Dataset**: Global Historical Climatology Network - Daily (GHCN-D)

### Acknowledgments
This project builds upon the foundational work of the original GHCNpy library while extending its capabilities for modern Python environments. Special thanks to NOAA NCEI for maintaining the GHCN-D dataset and providing public access to this valuable climate resource.

### License
This project maintains the open-source spirit of the original GHCNpy library. See `LICENSE` file for details.

***

## 📞 Contact & Support

- **Developer**: [Shourya Sharma](https://github.com/shourya-sharma-33)
- **GitHub Issues**: [Report bugs or request features](https://github.com/shourya-sharma-33/GHCN25py/issues)
- **LeetCode**: [shourya-sharma-3](https://leetcode.com/profile/shourya-sharma-3)

For questions about GHCN-Daily data format and content, visit the [official GHCN-D documentation](ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/).

***

*GHCN25py - Making climate data accessible for the Python 3+ era* 🌡️📊🐍

[1](https://github.com/shourya-sharma-33)