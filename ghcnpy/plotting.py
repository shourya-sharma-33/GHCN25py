# Import Modules
from datetime import datetime, date
import calendar
import re
import gzip

import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.colors as colors
import pylab
from mpl_toolkits.basemap import Basemap

import ghcnpy as gp

#################################################
# MODULE: plot_temperature
# Plot Temperature Data for a given station
#################################################
def plot_temperature(station_id, begin_date, end_date):
    print("\nPLOTTING TEMPERATURE DATA FOR STATION: ", station_id)

    # Declare Other Variables
    begin_year = 1895
    num_elements = 2  # TMAX/TMIN
    tmax = 0
    tmin = 1
    end_year = datetime.now().year
    num_years = (end_year - begin_year) + 1

    # Get station metadatafile
    ghcnd_stations = gp.get_ghcnd_stations()
    ghcnd_meta = ghcnd_stations[ghcnd_stations[:, 0] == station_id]
    ghcnd_id = ghcnd_meta[0][0]
    ghcnd_lat = float(ghcnd_meta[0][1])
    ghcnd_lon = float(ghcnd_meta[0][2])
    ghcnd_alt = float(ghcnd_meta[0][3])
    ghcnd_name = ghcnd_meta[0][5]
    ghcnd_name = ghcnd_name.strip()
    ghcnd_name = re.sub(' +', ' ', ghcnd_name)
    ghcnd_name = ghcnd_name.replace(" ", "_")

    # Grab Data
    gp.get_data_station(station_id)

    #################################################
    # Read in GHCN-D Data (Original, QC'd data removed)
    infile = station_id + ".dly"
    ghcnd_value = np.zeros((num_years, 12, 31, num_elements), dtype='f') - (9999.0)

    with open(infile, 'r') as file_handle:
        contents = file_handle.readlines()

    for counter in range(len(contents)):
        element = contents[counter][17:21]

        if element in ("TMAX", "TMIN"):
            element_counter = tmax if element == "TMAX" else tmin

            year = int(contents[counter][11:15])
            year_counter = year - begin_year

            month = int(contents[counter][15:17])
            month_counter = month - 1

            char = 21
            for day_counter in range(0, 31):
                if contents[counter][char:char + 5] != "-9999" and contents[counter][char + 6:char + 7] == " ":
                    ghcnd_value[year_counter][month_counter][day_counter][element_counter] = float(contents[counter][char:char + 5]) / 10.0
                char += 8

    # Mask Missing, convert from C to F
    ghcnd_nonmiss = ma.masked_values(ghcnd_value, -9999.)
    ghcnd_nonmiss = (ghcnd_nonmiss * 1.8) + 32

    # Get Record / Average Values for every day in year; averaging period 1981-2010
    record_max_ghcnd = np.zeros((12, 31), dtype='f') - (9999.0)
    record_min_ghcnd = np.zeros((12, 31), dtype='f') - (9999.0)
    average_max_ghcnd = np.zeros((12, 31), dtype='f') - (9999.0)
    average_min_ghcnd = np.zeros((12, 31), dtype='f') - (9999.0)
    for month_counter in range(0, 12):
        for day_counter in range(0, 31):
            record_max_ghcnd[month_counter, day_counter] = ma.max(ghcnd_nonmiss[:, month_counter, day_counter, tmax])
            record_min_ghcnd[month_counter, day_counter] = ma.min(ghcnd_nonmiss[:, month_counter, day_counter, tmin])
            average_max_ghcnd[month_counter, day_counter] = ma.average(
                ghcnd_nonmiss[(1980-begin_year):(2010-begin_year), month_counter, day_counter, tmax])
            average_min_ghcnd[month_counter, day_counter] = ma.average(
                ghcnd_nonmiss[(1980-begin_year):(2010-begin_year), month_counter, day_counter, tmin])

    #################################################
    # Gather Data Based Upon Date Requested
    begin_yy, begin_mm, begin_dd = int(begin_date[0:4]), int(begin_date[4:6]), int(begin_date[6:8])
    end_yy, end_mm, end_dd = int(end_date[0:4]), int(end_date[4:6]), int(end_date[6:8])

    num_days = (date(end_yy, end_mm, end_dd) - date(begin_yy, begin_mm, begin_dd)).days + 1
    num_months = ((date(end_yy, end_mm, end_dd).year - date(begin_yy, begin_mm, begin_dd).year)*12 +
                  date(end_yy, end_mm, end_dd).month - date(begin_yy, begin_mm, begin_dd).month) + 1

    record_max = np.zeros((num_days), dtype='f') - (9999.0)
    record_min = np.zeros((num_days), dtype='f') - (9999.0)
    average_max = np.zeros((num_days), dtype='f') - (9999.0)
    average_min = np.zeros((num_days), dtype='f') - (9999.0)
    raw_max = np.zeros((num_days), dtype='f') - (9999.0)
    raw_min = np.zeros((num_days), dtype='f') - (9999.0)

    month_pos = np.zeros((num_months), dtype='i') - (9999.0)
    month_names = np.empty((num_months), dtype='S7')

    day_index = 0
    month_index = 0
    for year_counter in range(begin_yy, end_yy + 1):
        if year_counter == begin_yy:
            start_month, end_month = begin_mm, 12
        elif year_counter == end_yy:
            start_month, end_month = 1, end_mm
        else:
            start_month, end_month = 1, 12
        for month_counter in range(start_month, end_month + 1):
            month_pos[month_index] = day_index
            month_names[month_index] = calendar.month_name[month_counter][0:3] + " '" + str(year_counter)[2:4]
            for day_counter in range(begin_dd, end_dd + 1):
                try:
                    # Check if date is valid
                    datetime(year=year_counter, month=month_counter, day=day_counter)
                    record_max[day_index] = record_max_ghcnd[month_counter - 1, day_counter - 1]
                    record_min[day_index] = record_min_ghcnd[month_counter - 1, day_counter - 1]
                    average_max[day_index] = average_max_ghcnd[month_counter - 1, day_counter - 1]
                    average_min[day_index] = average_min_ghcnd[month_counter - 1, day_counter - 1]
                    raw_max[day_index] = ghcnd_nonmiss[year_counter - begin_year, month_counter - 1, day_counter - 1, tmax]
                    raw_min[day_index] = ghcnd_nonmiss[year_counter - begin_year, month_counter - 1, day_counter - 1, tmin]
                    day_index += 1
                except:
                    pass
            month_index += 1

    x_axis = range(num_days)

    #################################################
    # PLOT
    fig, ax1 = plt.subplots(figsize=(15, 8), edgecolor='white', facecolor='white', dpi=300)

    # Add grid lines
    plt.grid(color='black', linestyle='--', linewidth=0.5, alpha=0.3)

    # Plot Record TMAX/TMIN
    plt.bar(x_axis, record_max - record_min, bottom=record_min, edgecolor='none', color='#c3bba4', width=1, label="Record Max/Min")

    # Plot Average TMAX/TMIN
    plt.bar(x_axis, average_max - average_min, bottom=average_min, edgecolor='none', color='#9a9180', width=1, label="Average Max/Min")

    # Plot Raw TMAX/TMIN
    plt.bar(x_axis, raw_max - raw_min, bottom=raw_min, edgecolor='black', linewidth=0.5, color='#5a3b49', width=1, label="Actual Max/Min")

    # Find New Max/Min Records
    new_max_records = raw_max[raw_max >= record_max]
    new_min_records = raw_min[raw_min <= record_min]

    # Plot New Max/Min Records
    plt.scatter(np.where(raw_max >= record_max)[0] + 0.5, new_max_records + 1.25, s=15, zorder=10, color='#d62728', alpha=0.75, linewidth=0, label="New Max Record")
    plt.scatter(np.where(raw_min <= record_min)[0] + 0.5, new_min_records - 1.25, s=15, zorder=10, color='#1f77b4', alpha=0.75, linewidth=0, label="New Min Record")

    # Plot Legend
    plt.legend(bbox_to_anchor=(0., -.102, 1., -1.02), loc=3, ncol=5, mode="expand", borderaxespad=0., fontsize=12)

    # Plot X/Y Limits
    ymin = int(5 * round(float((min(record_min) - 10)) / 5))
    ymax = int(5 * round(float((max(record_max) + 10)) / 5))
    plt.ylim(ymin, ymax)
    plt.xlim(-5, num_days)

    # Plot Y-Axis Label
    plt.yticks(range(ymin, ymax, 10), [r'{}$^\circ$'.format(x) for x in range(ymin, ymax, 10)], fontsize=10)
    plt.ylabel(r'Temperature ($^\circ$F)', fontsize=12)

    # Plot X-Axis Label
    plt.xticks(month_pos, month_names, fontsize=10)

    # Plot 2nd Y Axis Labels
    ax3 = ax1.twinx()
    plt.yticks(range(ymin, ymax, 10), [r'{}$^\circ$'.format(x) for x in range(ymin, ymax, 10)], fontsize=10)
    plt.ylim(ymin, ymax)

    # Plot Title/Subtitle
    plt.suptitle(f"{station_id}: {ghcnd_name}", fontsize=20)
    plt.title(f"LAT= {ghcnd_lat} | LON= {ghcnd_lon} | ELEV= {int(ghcnd_alt * 3.2808399)}'", fontsize=15)

    # Save Figure
    plt.savefig(f"{station_id}_temperature.png", dpi=300)
    plt.clf()
    return None

#################################################
# MODULE: plot_precipitation
# Plot Accum. Precip Data for a given station
#################################################
def plot_precipitation(station_id):
    print("\nPLOTTING PRECIPITATION DATA FOR STATION: ", station_id)

    # Declare Other Variables
    begin_year = 1895
    num_elements = 1 # PRCP
    prcp = 0
    num_days = 366

    end_year = datetime.now().year
    num_years = (end_year - begin_year) + 1

    # Get station metadatafile
    ghcnd_stations = gp.get_ghcnd_stations()

    ghcnd_meta = ghcnd_stations[ghcnd_stations[:, 0] == station_id]
    ghcnd_id = ghcnd_meta[0][0]
    ghcnd_lat = float(ghcnd_meta[0][1])
    ghcnd_lon = float(ghcnd_meta[0][2])
    ghcnd_alt = float(ghcnd_meta[0][3])
    ghcnd_name = ghcnd_meta[0][5]
    ghcnd_name = ghcnd_name.strip()
    ghcnd_name = re.sub(' +', ' ', ghcnd_name)
    ghcnd_name = ghcnd_name.replace(" ", "_")

    # Grab Data
    gp.get_data_station(station_id)

    #################################################
    # Read in GHCN-D Data (Original, QC'd data removed)
    infile = f"{station_id}.dly"
    ghcnd_value = np.zeros((num_years, 12, 31, num_elements), dtype='f')

    with open(infile, 'r') as file_handle:
        contents = file_handle.readlines()

    valid_end = -9999
    valid_begin = 9999
    for counter in range(len(contents)):
        element = contents[counter][17:21]

        if element == "PRCP":
            element_counter = prcp

            year = int(contents[counter][11:15])
            year_counter = year - begin_year
            valid_begin = min(valid_begin, year)
            valid_end = max(valid_end, year)

            month = int(contents[counter][15:17])
            month_counter = month - 1

            char = 21
            for day_counter in range(0, 31):
                if contents[counter][char:char+5] != "-9999" and contents[counter][char+6:char+7] == " ":
                    ghcnd_value[year_counter][month_counter][day_counter][element_counter] = float(contents[counter][char:char+5]) / 10.0
                    last_day = day_counter + 1
                char = char + 8

    # Get day of year for last day with valid data
    last_day = datetime(year, month, last_day).timetuple().tm_yday

    # Convert from mm to inch
    ghcnd_value = (ghcnd_value * 0.0393701)

    # Get Record / Average Values for every day in year
    average_prcp = np.zeros((num_days), dtype='f') - (9999.0)
    day_of_year = 0
    day_before = 0
    for month_counter in range(0, 12):
        for day_counter in range(0, 31):
            try:
                # Check if leap-year date is valid
                datetime(year=2012, month=month_counter+1, day=day_counter+1)

                average_prcp[day_of_year] = day_before + ma.average(ghcnd_value[(valid_begin-begin_year):(valid_end-begin_year), month_counter, day_counter, prcp])
                day_before = average_prcp[day_of_year]

                day_of_year += 1
            except:
                pass

    #################################################
    # Create Accumulations
    prcp_accum = np.zeros((num_years, num_days), dtype='f')
    total_accum = np.zeros((num_years), dtype='f')
    for year_counter in range(0, num_years):
        day_of_year = 0
        day_before = 0
        for month_counter in range(0, 12):
            for day_counter in range(0, 31):
                try:
                    # Check if date is valid
                    datetime(year=year_counter+begin_year, month=month_counter+1, day=day_counter+1)
                    prcp_accum[year_counter][day_of_year] = day_before + ghcnd_value[year_counter, month_counter, day_counter, prcp]
                    total_accum[year_counter] = prcp_accum[year_counter][day_of_year]
                    day_before = prcp_accum[year_counter][day_of_year]

                    day_of_year += 1
                except:
                    pass

    #################################################
    # PLOT

    # Mask Zero Data before plotting
    prcp_accum = ma.masked_values(prcp_accum, 0.)
    total_accum = ma.masked_values(total_accum, 0.)

    # Get Some Stats Needed For Plotting
    x_axis = range(num_days)
    x_axis_end = range(last_day)

    # Current Year
    current_loc = num_years - 1
    current_prcp = "%6.2f" % total_accum[current_loc]
    current_year = current_loc + begin_year
    current_data = prcp_accum[current_loc, 0:last_day]
    current_last = prcp_accum[current_loc, last_day]

    max_prcp = "%6.2f" % np.max(total_accum)
    max_loc = np.argmax(total_accum)
    max_year = max_loc + begin_year

    min_prcp = "%6.2f" % np.min(total_accum[np.where(total_accum != 0)])
    min_loc = np.nanargmin(total_accum)
    min_year = min_loc + begin_year

    # Average Year
    avg_prcp = "%6.2f" % average_prcp[365]

    # Create Figure
    fig, ax1 = plt.subplots(figsize=(15, 8), edgecolor='white', facecolor='white', dpi=300)

    # Add grid lines
    plt.grid(color='black', linestyle='--', linewidth=0.5, alpha=0.3)

    # Plot Accumulated PRCP (Sort by end of year accumulation and plot by range of color)
    order = np.argsort(prcp_accum[:, 364])
    color_pos = np.linspace(0.5, 1, num_years)
    order_counter = 0
    color_counter = 0
    for year_counter in range(0, num_years):
        pos = order[order_counter]
        if pos != (num_years - 1):
            plt.plot(x_axis, prcp_accum[pos, :], linewidth=0.5, color=colors.rgb2hex(pylab.cm.GnBu(color_pos[color_counter])[0:3]))
            color_counter += 1
        order_counter += 1

    # Overlay Record Max Prcp Year
    if max_loc == current_loc:
        plt.plot(x_axis_end, prcp_accum[max_loc, 0:last_day], color='#084081', linewidth=3, label='Max (' + str(max_year) + ': ' + str(max_prcp) + '")')
    else:
        plt.plot(x_axis, prcp_accum[max_loc, :], color='#084081', linewidth=3, label='Max (' + str(max_year) + ': ' + str(max_prcp) + '")')

    # Overlay Record Min Prcp Year
    if min_loc == current_loc:
        plt.plot(x_axis_end, prcp_accum[min_loc, 0:last_day], color='#66ff99', linewidth=3, label='Min (' + str(min_year) + ': ' + str(min_prcp) + '")')
    else:
        plt.plot(x_axis, prcp_accum[min_loc, :], color='#66ff99', linewidth=3, label='Min (' + str(min_year) + ': ' + str(min_prcp) + '")')

    # Overlay Average PRCP
    plt.plot(x_axis, average_prcp[:], color='#e6b800', linewidth=3, markeredgecolor='white', label='Avg (' + str(avg_prcp) + '")')

    # Overlay Current Prcp Year
    plt.plot(x_axis_end, current_data, color='black', linewidth=3, label='Current (' + str(current_year) + ': ' + str(current_prcp) + '")')
    plt.plot(x_axis_end[last_day - 1], current_last, marker='o', color='black', markersize=10)

    # Plot Legend
    plt.legend(bbox_to_anchor=(0., -.102, 1., -1.02), loc=3, ncol=4, mode="expand", borderaxespad=0., fontsize=12)

    # Plot X/Y Limits
    ymin = 0
    ymax = int(5 * round(float((np.max(prcp_accum) + 10)) / 5))
    plt.ylim(ymin, ymax)
    plt.xlim(-5, num_days)

    # Plot Y-Axis Label
    plt.yticks(range(ymin, ymax, 10), [r'{}"'.format(x) for x in range(ymin, ymax, 10)], fontsize=10)
    plt.ylabel(r'Accumulated Precip (inches)', fontsize=12)

    # Plot X-Axis Label
    month_pos = [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    plt.xticks(month_pos, month_names, fontsize=10)

    # Plot 2nd Y Axis Labels
    ax3 = ax1.twinx()
    plt.yticks(range(ymin, ymax, 10), [r'{}"'.format(x) for x in range(ymin, ymax, 10)], fontsize=10)
    plt.ylim(ymin, ymax)

    # Plot Title/Subtitle
    plt.suptitle(station_id + ': ' + ghcnd_name, fontsize=20)
    plt.title('LAT= ' + str(ghcnd_lat) + ' | LON= ' + str(ghcnd_lon) + ' | ELEV= ' + str(int(ghcnd_alt * 3.2808399)) + '\'', fontsize=15)

    # Save Figure
    plt.savefig(station_id + '_precipitation.png', dpi=300)
    plt.clf()
    return None
# Import Modules
from datetime import datetime, date
import calendar
import re
import gzip

import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.colors as colors
import pylab
from mpl_toolkits.basemap import Basemap

import ghcnpy as gp

#################################################
# MODULE: plot_snowfall
# Plot Accum. Snow Data for a given station
#################################################
def plot_snowfall(station_id):
    print("\nPLOTTING SNOWFALL DATA FOR STATION: ", station_id)

    # Declare Other Variables
    begin_year = 1895
    num_elements = 1  # SNOW
    snow = 0
    num_days = 366

    end_year = datetime.now().year
    num_years = (end_year - begin_year) + 1

    # Get station metadatafile
    ghcnd_stations = gp.get_ghcnd_stations()

    ghcnd_meta = ghcnd_stations[ghcnd_stations[:, 0] == station_id]
    ghcnd_id = ghcnd_meta[0][0]
    ghcnd_lat = float(ghcnd_meta[0][1])
    ghcnd_lon = float(ghcnd_meta[0][2])
    ghcnd_alt = float(ghcnd_meta[0][3])
    ghcnd_name = ghcnd_meta[0][5]
    ghcnd_name = ghcnd_name.strip()
    ghcnd_name = re.sub(' +', ' ', ghcnd_name)
    ghcnd_name = ghcnd_name.replace(" ", "_")

    # Grab Data
    gp.get_data_station(station_id)

    #################################################
    # Read in GHCN-D Data (Original, QC'd data removed)
    infile = station_id + ".dly"
    ghcnd_value = np.zeros((num_years, 12, 31, num_elements), dtype='f')

    with open(infile, 'r') as file_handle:
        contents = file_handle.readlines()

    valid_end = -9999
    valid_begin = 9999
    for counter in range(len(contents)):

        element = contents[counter][17:21]

        if element == "SNOW":
            element_counter = snow

            year = int(contents[counter][11:15])
            year_counter = year - begin_year
            valid_begin = min(valid_begin, year)
            valid_end = max(valid_end, year)

            month = int(contents[counter][15:17])
            month_counter = month - 1

            char = 21
            for day_counter in range(0, 31):
                if contents[counter][char:char + 5] != "-9999" and contents[counter][char + 6:char + 7] == " ":
                    ghcnd_value[year_counter][month_counter][day_counter][element_counter] = float(contents[counter][char:char + 5])
                    last_day = day_counter + 1
                char = char + 8

    # Get day of year for last day with valid data
    last_day = datetime(year, month, last_day).timetuple().tm_yday
    last_day = last_day + 92  # Shift three months
    if last_day >= 365:
        last_day = last_day - 365

    # Convert from mm to inch
    ghcnd_value = (ghcnd_value * 0.0393701)

    # Get Record / Average Values for every day in year
    average_snow = np.zeros((num_days), dtype='f') - (9999.0)
    day_of_year = 0
    day_before = 0
    for month_counter in [9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
        for day_counter in range(0, 31):
            try:
                # Check if leap-year date is valid
                datetime(year=2012, month=month_counter + 1, day=day_counter + 1)

                average_snow[day_of_year] = day_before + ma.average(
                    ghcnd_value[(valid_begin - begin_year):(valid_end - begin_year), month_counter, day_counter, snow])
                day_before = average_snow[day_of_year]

                day_of_year = day_of_year + 1
            except:
                pass

    #################################################
    # Create Accumulations
    new_year_counter = 0
    snow_accum = np.zeros((num_years + 1, num_days), dtype='f')
    total_accum = np.zeros((num_years + 1), dtype='f')
    for year_counter in range(0, num_years):
        for month_counter in range(0, 12):
            if month_counter == 9:  # Month Begins in Oct
                new_year_counter = year_counter + 1
                day_of_year = 0
                day_before = 0
            for day_counter in range(0, 31):
                try:
                    # Check if date is valid
                    datetime(year=year_counter + begin_year, month=month_counter + 1, day=day_counter + 1)
                    snow_accum[new_year_counter][day_of_year] = day_before + ghcnd_value[year_counter, month_counter, day_counter, snow]
                    total_accum[new_year_counter] = snow_accum[new_year_counter][day_of_year]
                    day_before = snow_accum[new_year_counter][day_of_year]
                    day_of_year = day_of_year + 1
                except:
                    pass
            if month_counter + 1 == 12 and snow_accum[year_counter][365] == 0:
                snow_accum[year_counter][365] = snow_accum[year_counter][364]

    #################################################
    # PLOT
    # Mask Zero Data before plotting
    # snow_accum = ma.masked_values(snow_accum, 0.)  # commented to avoid errors
    total_accum = ma.masked_values(total_accum, 0.)

    # Get Some Stats Needed For Plotting
    x_axis = range(num_days)
    x_axis_end = range(last_day)

    current_loc = num_years - 1
    current_snow = "%6.2f" % total_accum[current_loc]
    current_year = current_loc + begin_year
    current_data = snow_accum[current_loc, 0:last_day]
    current_last = snow_accum[current_loc, last_day]

    max_snow = "%6.2f" % np.max(total_accum)
    max_loc = np.argmax(total_accum)
    max_year = max_loc + begin_year

    min_snow = "%6.2f" % np.min(total_accum[np.where(total_accum != 0)])
    min_loc = np.nanargmin(total_accum)
    min_year = min_loc + begin_year

    avg_snow = "%6.2f" % average_snow[365]

    # Create Figure
    fig, ax1 = plt.subplots(figsize=(15, 8), edgecolor='white', facecolor='white', dpi=300)

    # Add grid lines
    plt.grid(color='black', linestyle='--', linewidth=0.5, alpha=0.3)

    # Plot Accumulated SNOW (Sort by end of year accumulation and plot by range of color)
    order = np.argsort(snow_accum[:, 364])
    color_pos = np.linspace(0.5, 1, num_years)
    order_counter = 0
    color_counter = 0
    for year_counter in range(0, num_years):
        pos = order[order_counter]
        if pos != (num_years - 1):
            plt.plot(x_axis, snow_accum[pos, :], linewidth=0.5,
                     color=colors.rgb2hex(pylab.cm.GnBu(color_pos[color_counter])[0:3]))
            color_counter = color_counter + 1
        order_counter = order_counter + 1

    # Overlay Record Max Snow Year
    if max_loc == current_loc:
        plt.plot(x_axis_end, snow_accum[max_loc, 0:last_day], color='#084081', linewidth=3,
                 label='Max (' + str(max_year - 1) + '-' + str(max_year) + ': ' + str(max_snow) + '")')
    else:
        plt.plot(x_axis, snow_accum[max_loc, :], color='#084081', linewidth=3,
                 label='Max (' + str(max_year - 1) + '-' + str(max_year) + ': ' + str(max_snow) + '")')

    # Overlay Record Min Snow Year
    if min_loc == current_loc:
        plt.plot(x_axis_end, snow_accum[min_loc, 0:last_day], color='#66ff99', linewidth=3,
                 label='Min (' + str(min_year - 1) + '-' + str(min_year) + ': ' + str(min_snow) + '")')
    else:
        plt.plot(x_axis, snow_accum[min_loc, :], color='#66ff99', linewidth=3,
                 label='Min (' + str(min_year - 1) + '-' + str(min_year) + ': ' + str(min_snow) + '")')

    # Overlay Average SNOW
    plt.plot(x_axis, average_snow[:], color='#e6b800', linewidth=3, markeredgecolor='white',
             label='Avg (' + str(avg_snow) + '")')

    # Overlay Current Snow Year
    plt.plot(x_axis_end, current_data, color='black', linewidth=3,
             label='Current (' + str(current_year - 1) + '-' + str(current_year) + ': ' + str(current_snow) + '")')
    plt.plot(x_axis_end[last_day - 1], current_last, marker='o', color='black', markersize=10)

    # Plot Legend
    plt.legend(bbox_to_anchor=(0., -.102, 1., -1.02), loc=3, ncol=4, mode="expand", borderaxespad=0., fontsize=12)

    # Plot X/Y Limits
    ymin = 0
    ymax = int(5 * round(float((np.max(snow_accum) + 10)) / 5))
    plt.ylim(ymin, ymax)
    plt.xlim(-5, num_days)

    # Plot Y-Axis Label
    plt.yticks(range(ymin, ymax, 10), [r'{}"'.format(x) for x in range(ymin, ymax, 10)], fontsize=10)
    plt.ylabel(r'Accumulated Snowfall (inches)', fontsize=12)

    # Plot X-Axis Label
    month_pos = [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
    month_names = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"]
    plt.xticks(month_pos, month_names, fontsize=10)

    # Plot 2nd Y Axis Labels
    ax3 = ax1.twinx()
    plt.yticks(range(ymin, ymax, 10), [r'{}"'.format(x) for x in range(ymin, ymax, 10)], fontsize=10)
    plt.ylim(ymin, ymax)

    # Plot Title/Subtitle
    plt.suptitle(station_id + ': ' + ghcnd_name, fontsize=20)
    plt.title('LAT= ' + str(ghcnd_lat) + ' | LON= ' + str(ghcnd_lon) + ' | ELEV= ' + str(int(ghcnd_alt * 3.2808399)) + '\'',
              fontsize=15)

    # Save Figure
    plt.savefig(station_id + '_snowfall.png', dpi=300)
    plt.clf()
    return None
