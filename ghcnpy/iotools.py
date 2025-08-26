# Import Modules
import re
import os
import sys
import requests
import datetime
from datetime import date
import pandas as pd
import numpy as np
import netCDF4 as nc

import ghcnpy as gp

#################################################
# MODULE: get_ghcnd_version
# Get which version of GHCN-D we are using
#################################################
def get_ghcnd_version():
    url = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-version.txt"
    r = requests.get(url)
    with open("ghcnd-version.txt", "wb") as f:
        f.write(r.content)
    try:
        with open("ghcnd-version.txt", "r") as myfile:
            ghcnd_version = myfile.read().replace('\n', '')
    except:
        print("Version file does not exist: ghcnd-version.txt")
        sys.exit()
    return ghcnd_version

#################################################
# MODULE: get_data_station
# Fetch Individual station (.dly ASCII format)
#################################################
def get_data_station(station_id):
    print("\nGETTING DATA FOR STATION: ", station_id)
    url = f"https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/all/{station_id}.dly"
    r = requests.get(url)
    with open(f"{station_id}.dly", "wb") as f:
        f.write(r.content)
    outfile = f"{station_id}.dly"
    return outfile

#################################################
# MODULE: get_data_year
# Fetch 1 Year of Data (.csv ASCII format)
#################################################
def get_data_year(year):
    print("\nGETTING DATA FOR YEAR: ", year)
    url = f"https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/by_year/{year}.csv.gz"
    r = requests.get(url)
    with open(f"{year}.csv.gz", "wb") as f:
        f.write(r.content)
    outfile = f"{year}.csv.gz"
    return outfile

#################################################
# MODULE: get_ghcnd_stations
# Get ghcnd-stations.txt file
#################################################
def get_ghcnd_stations():
    print("\nGRABBING LATEST STATION METADATA FILE")
    url = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"
    r = requests.get(url)
    with open("ghcnd-stations.txt", "wb") as f:
        f.write(r.content)
    ghcnd_stnfile = "ghcnd-stations.txt"
    ghcnd_stations = np.genfromtxt(ghcnd_stnfile, delimiter=(11,9,10,7,4,30), dtype=str)
    return ghcnd_stations

#################################################
# MODULE: get_ghcnd_inventory
# Get ghcnd-inventory.txt file
#################################################
def get_ghcnd_inventory():
    print("\nGRABBING LATEST STATION INVENTORY FILE")
    url = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-inventory.txt"
    r = requests.get(url)
    with open("ghcnd-inventory.txt", "wb") as f:
        f.write(r.content)
    ghcnd_invfile = "ghcnd-inventory.txt"
    ghcnd_inventory = np.genfromtxt(ghcnd_invfile, delimiter=(11,9,11,4), dtype=str)
    return ghcnd_inventory

#################################################
# MODULE: output_to_csv
# Output to csv (one station per csv)
#################################################
def output_to_csv(station_id):
    print("\nOUTPUTTING TO CSV: ", station_id, ".csv")

    # 5 Elements of GHCN-D
    num_elements = 5
    tmax = 0
    tmin = 1
    prcp = 2
    snow = 3
    snwd = 4

    # Grab Data
    gp.get_data_station(station_id)

    # Read in GHCN-D Data
    infile = station_id + ".dly"
    with open(infile, 'r') as file_handle:
        ghcnd_contents = file_handle.readlines()

    # Get Year Start and End of File for time dimensions
    ghcnd_begin_year = int(ghcnd_contents[0][11:15])
    ghcnd_end_year = int(ghcnd_contents[len(ghcnd_contents) - 1][11:15])
    num_years = int((ghcnd_end_year - ghcnd_begin_year) + 1)

    # Go through GHCN-D Data
    ghcnd_data = np.zeros((num_years,12,31,num_elements),dtype='f')-(9999.0)

    for counter in range(len(ghcnd_contents)):
        element = ghcnd_contents[counter][17:21]
        if element in ["TMAX", "TMIN", "PRCP", "SNOW", "SNWD"]:
            if element == "TMAX":
                element_counter = tmax
                divisor = 10.0
            if element == "TMIN":
                element_counter = tmin
                divisor = 10.0
            if element == "PRCP":
                element_counter = prcp
                divisor = 10.0
            if element == "SNOW":
                element_counter = snow
                divisor = 1.0
            if element == "SNWD":
                element_counter = snwd
                divisor = 1.0

            year = int(ghcnd_contents[counter][11:15])
            year_counter = int(year - ghcnd_begin_year)
            month = int(ghcnd_contents[counter][15:17])
            month_counter = int(month - 1)

            char = 21
            for day_counter in range(0, 31):
                if ghcnd_contents[counter][char:char+5] != "-9999" and ghcnd_contents[counter][char+6:char+7].strip() == "":
                    ghcnd_data[year_counter,month_counter,day_counter,element_counter] = float(ghcnd_contents[counter][char:char+5]) / divisor
                char = char + 8

    # Output data to csv file
    outfile_data = station_id + '.csv'
    with open(outfile_data,'w') as out_data:
        out_data.write("YYYY,MM,DD,TMAX,TMIN,PRCP,SNOW,SNWD\n")
        for year_counter in range(0, num_years):
            for month_counter in range(0, 12):
                for day_counter in range(0, 31):
                    # Output
                    if (ghcnd_data[year_counter,month_counter,day_counter,tmax] != -9999. or
                        ghcnd_data[year_counter,month_counter,day_counter,tmin] != -9999. or
                        ghcnd_data[year_counter,month_counter,day_counter,prcp] != -9999. or
                        ghcnd_data[year_counter,month_counter,day_counter,snow] != -9999. or
                        ghcnd_data[year_counter,month_counter,day_counter,snwd] != -9999.):
                        out_data.write("%04i,%02i,%02i,%7.1f,%7.1f,%7.1f,%7.1f,%7.1f\n" %
                            (year_counter+ghcnd_begin_year, month_counter+1, day_counter+1,
                             ghcnd_data[year_counter,month_counter,day_counter,tmax],
                             ghcnd_data[year_counter,month_counter,day_counter,tmin],
                             ghcnd_data[year_counter,month_counter,day_counter,prcp],
                             ghcnd_data[year_counter,month_counter,day_counter,snow],
                             ghcnd_data[year_counter,month_counter,day_counter,snwd]))
    return None

# The rest of your output_to_netcdf function: just replace any `xrange` with `range` similarly.
def to_datastructure(station_id):
    print("\nOUTPUTTING TO DATA STRUCTURE: ", station_id)

    # 5 Elements of GHCN-D
    num_elements = 5
    tmax = 0
    tmin = 1
    prcp = 2
    snow = 3
    snwd = 4

    # Grab Data
    gp.get_data_station(station_id)

    # Read in GHCN-D Data
    infile = station_id + ".dly"
    with open(infile, 'r') as file_handle:
        ghcnd_contents = file_handle.readlines()

    # Get Year Start and End of File for time dimensions
    ghcnd_begin_year = int(ghcnd_contents[0][11:15])
    ghcnd_end_year = int(ghcnd_contents[len(ghcnd_contents) - 1][11:15])
    num_years = int((ghcnd_end_year - ghcnd_begin_year) + 1)

    # Go through GHCN-D Data
    ghcnd_data = np.zeros((num_years,12,31,num_elements),dtype='f')-(9999.0)

    for counter in range(len(ghcnd_contents)):
        element = ghcnd_contents[counter][17:21]
        if element in ["TMAX", "TMIN", "PRCP", "SNOW", "SNWD"]:
            if element == "TMAX":
                element_counter = tmax
                divisor = 10.0
            if element == "TMIN":
                element_counter = tmin
                divisor = 10.0
            if element == "PRCP":
                element_counter = prcp
                divisor = 10.0
            if element == "SNOW":
                element_counter = snow
                divisor = 1.0
            if element == "SNWD":
                element_counter = snwd
                divisor = 1.0

            year = int(ghcnd_contents[counter][11:15])
            year_counter = int(year - ghcnd_begin_year)
            month = int(ghcnd_contents[counter][15:17])
            month_counter = int(month - 1)

            char = 21
            for day_counter in range(0, 31):
                if ghcnd_contents[counter][char:char+5] != "-9999" and ghcnd_contents[counter][char+6:char+7].strip() == "":
                    ghcnd_data[year_counter,month_counter,day_counter,element_counter] = float(ghcnd_contents[counter][char:char+5]) / divisor
                char = char + 8

    # Return data as list of arrays instead of writing to CSV
    data_list = []
    
    for year_counter in range(0, num_years):
        for month_counter in range(0, 12):
            for day_counter in range(0, 31):
                # Check if there's any valid data for this date
                if (ghcnd_data[year_counter,month_counter,day_counter,tmax] != -9999. or
                    ghcnd_data[year_counter,month_counter,day_counter,tmin] != -9999. or
                    ghcnd_data[year_counter,month_counter,day_counter,prcp] != -9999. or
                    ghcnd_data[year_counter,month_counter,day_counter,snow] != -9999. or
                    ghcnd_data[year_counter,month_counter,day_counter,snwd] != -9999.):
                    
                    # Create array for this date: [YYYY, MM, DD, TMAX, TMIN, PRCP, SNOW, SNWD]
                    date_array = [
                        year_counter + ghcnd_begin_year,
                        month_counter + 1,
                        day_counter + 1,
                        ghcnd_data[year_counter,month_counter,day_counter,tmax],
                        ghcnd_data[year_counter,month_counter,day_counter,tmin],
                        ghcnd_data[year_counter,month_counter,day_counter,prcp],
                        ghcnd_data[year_counter,month_counter,day_counter,snow],
                        ghcnd_data[year_counter,month_counter,day_counter,snwd]
                    ]
                    data_list.append(date_array)
    
    return data_list
def get_stations_in_datastructure():
    print("\nGRABBING LATEST STATION METADATA FILE")
    url = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"
    r = requests.get(url)
    with open("ghcnd-stations.txt", "wb") as f:
        f.write(r.content)
    
    # Read the station data and return as data structure with index
    stations_list = []
    
    with open("ghcnd-stations.txt", 'r') as file_handle:
        station_lines = file_handle.readlines()
    
    for index, line in enumerate(station_lines):
        # Parse fixed-width format based on GHCN-D station file specification
        station_id = line[0:11].strip()
        latitude = float(line[12:20].strip())
        longitude = float(line[21:30].strip())
        elevation = float(line[31:37].strip())
        station_name = line[41:71].strip()
        
        # Optional fields (may be empty)
        gsn_flag = line[72:75].strip() if len(line) > 72 else ""
        wmo_id = line[80:85].strip() if len(line) > 80 else ""
        
        # Create array for this station with index as first element
        station_array = [
            index,                # Index in the file (0, 1, 2, ...)
            station_id,          # Station ID
            latitude,            # Latitude
            longitude,           # Longitude  
            elevation,           # Elevation in meters
            station_name,        # Station name
            gsn_flag,            # GSN flag (if applicable)
            wmo_id               # WMO ID (if applicable)
        ]
        
        stations_list.append(station_array)
    
    return stations_list
