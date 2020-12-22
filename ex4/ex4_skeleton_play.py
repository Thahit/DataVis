import numpy as np
import pandas as pd
import geopandas as gpd
from datetime import datetime, timedelta

import bokeh.palettes as bp
from bokeh.plotting import figure,curdoc
from bokeh.transform import linear_cmap
from bokeh.layouts import column, row
from bokeh.models import (CDSView,
						HoverTool,ColorBar,
						GeoJSONDataSource,
						Patches,		# non capitalized version in text
						RadioButtonGroup,
						DateSlider,
						Button)

# ====================================================================
# Goal: Visualize demographics and daily new cases statistics in Switzerland

# The visualization output contains 2 parts:

# Part 1: add a map view and the color encodes the Density and BedsPerCapita,
# with a RadioButtonGroup which controls which aspect to show.


# Part 2: add a circle in each canton on the map, size of circle represents the current daily new cases per capita,
# add a timeline slider, add callback function controlling the slider and changing the size of the circle on the map when dragging the time slider.
# Additionally, a "Play" button can animate the slider as well as circles on the map.

# Reference link
# https://towardsdatascience.com/walkthrough-mapping-basics-with-bokeh-and-geopandas-in-python-43f40aa5b7e9

# ====================================================================

### Task 1: Data Preprocessing

## T1.1 Read and filter data
# Four data sources:
# Demographics.csv: the statistics data about population density and hospital beds per capita in each canton
# covid_19_cases_switzerland_standard_format.csv: the location(longitude, latitude) of the capital city in each canton
# covid19_cases_switzerland_openzh-phase2.csv: same as in ex2, daily new cases in each canton
# gadm36_CHE_1.shp: the shape file contains geometry data of swiss cantons, and is provided in the "data" folder.
# Please do not submit any data file with your solution, and you can asssume your solution is at the same directory as data

demo_url = 'https://github.com/daenuprobst/covid19-cases-switzerland/blob/master/demographics.csv?raw=true'
local_url = 'https://github.com/daenuprobst/covid19-cases-switzerland/blob/master/covid_19_cases_switzerland_standard_format.csv?raw=true'
case_url = 'https://github.com/daenuprobst/covid19-cases-switzerland/blob/master/covid19_cases_switzerland_openzh-phase2.csv?raw=true'
shape_dir = 'data/gadm36_CHE_1.shp'

# Read from demo_url into a dataframe using pandas
demo_raw = pd.read_csv(demo_url, index_col="Canton")	# I prefer canton as index

# Read from local_url into a dataframe using pandas
local_raw = pd.read_csv(local_url)

# Extract unique 'abbreviation_canton','lat','long' combinations from local_raw
canton_point = local_raw[['abbreviation_canton','lat','long']].drop_duplicates()

# Read from case_url into a dataframe using pandas
case_raw = pd.read_csv(case_url)
# Create a date list from case_raw and convert to datetime form
case_raw["Date"] = list(pd.to_datetime(case_raw['Date'], format='%Y-%m-%d'))
dates = list(case_raw["Date"])
dates_raw = dates

# Read shape file from shape_dir using geopandas
shape_raw = gpd.read_file(shape_dir)

# Extract canton name abbreviations from the attribute 'HASC_1', e.g. CH.AG --> AG, CH.ZH --> ZH
# And save into a new column named 'Canton'
shape_raw['Canton'] = shape_raw["HASC_1"].str.split('.', expand=True)[1]
canton_poly = shape_raw[['geometry', 'Canton']]

## T1.2 Merge data and build a GeoJSONDataSource

# Merge canton_poly with demo_raw on attribute name 'Canton' into dataframe merged,
# then merge the result with canton_point on 'Canton' and 'abbreviation_canton' respectively

# Potential issue:
# https://stackoverflow.com/questions/57045479/is-there-a-way-to-fix-maximum-recursion-level-in-python-3
merged = canton_poly.merge(demo_raw, how = "right", left_on="Canton", right_on=demo_raw.index)
merged.drop(26, inplace=True)	# drop CH

merged = merged.merge(canton_point, how = "right", left_on="Canton", right_on="abbreviation_canton")
# For each date, extract a list of daily new cases per capita from all cantons(e.g. 'AG_diff_pc', 'AI_diff_pc', etc.), and add as a new column in merged
# For instance, in the column['2020-10-31'], there are: [0.0005411327220155498, nan, nan, 0.000496300306803826, ...]

for i, d in enumerate(dates_raw):	# d=  date, i = idx

	x = pd.DataFrame(case_raw.loc[case_raw['Date'] == d])
	x = x[["AG_diff_pc", "AI_diff_pc", "AR_diff_pc", "BE_diff_pc", "BL_diff_pc",
				  "BS_diff_pc", "FR_diff_pc", "GE_diff_pc", "GL_diff_pc", "GR_diff_pc",
				  "JU_diff_pc", "LU_diff_pc", "NE_diff_pc",  "NW_diff_pc", "OW_diff_pc",
				  "SG_diff_pc", "SH_diff_pc",  "SO_diff_pc", "SZ_diff_pc", "TG_diff_pc",
				  "TI_diff_pc",  "UR_diff_pc", "VD_diff_pc", "VS_diff_pc", "ZG_diff_pc",
				  "ZH_diff_pc"]]
	# x.fillna(0,inplace=True) # if you want all cities
	k = d.strftime('%Y-%m-%d')	# for uniformity
	merged[str(k)] = pd.Series(x.values[0]) # string because otherwise we cant transform to json

# Calculate circle sizes that are proportional to dnc per capita
# Set the latest dnc as default

merged['size'] = merged.iloc[:, -1]*1e5/5+10
merged['dnc'] = merged.iloc[:, -2]

# for geosource df needs to be json
jsonMerged = merged.to_json()

# Build a GeoJSONDataSource from merged
geosource = GeoJSONDataSource(geojson=jsonMerged)

# Task 2: Data Visualization

# T2.1 Create linear color mappers for 2 attributes in demo_raw: population density, hospital beds per capita
# Map their maximum values to the high, and mimimum to the low
labels = ['Density', 'BedsPerCapita']

mappers = {}
mappers['Density'] = linear_cmap(demo_raw.Density, palette=bp.Inferno256,
								low=demo_raw.Density.min(), high=demo_raw.Density.max())
mappers['BedsPerCapita'] = linear_cmap(demo_raw.BedsPerCapita, palette=bp.Inferno256,
									   low=demo_raw.BedsPerCapita.min(), high=demo_raw.BedsPerCapita.max())

# ______________________________________________________________________________________________________________________
# T2.2 Draw a Switzerland Map on canton level

# Define a figure
p1 = figure(title='Demographics in Switzerland',
			plot_height=600,
			plot_width=950,
			toolbar_location='above',
			tools="pan, wheel_zoom, box_zoom, reset")

p1.xgrid.grid_line_color = None
p1.ygrid.grid_line_color = None

ColorVal='Density'
TsansVal=mappers['Density']['transform']
# Plot the map using patches, set the fill_color as mappers['Density']
cantons = p1.patches('xs', 'ys', source=geosource, name="grid",
					fill_color ={"field": ColorVal,
                                 "transform" : TsansVal},
          fill_alpha=0.5,  line_color="gray", line_width=2)

# ______________________________________________________________________________________________________________________
# Create a colorbar with mapper['Density'] and add it to above figure
color_bar = ColorBar(color_mapper=mappers['Density']['transform'], width=20, title_text_align='left',
					 location=(0, 0), title='Density', title_text_font='10')
p1.add_layout(color_bar, 'right')

# ______________________________________________________________________________________________________________________
# Add a hovertool to display canton, density, bedspercapita and dnc
hover = HoverTool(tooltips=[('Canton', '@Canton'),
							('Population Density', '@Density'),
							('Beds Per Capita', '@BedsPerCapita'),
							('Daily new Cases per Capita', '@dnc')],
				  			renderers=[cantons])

p1.add_tools(hover)

# ______________________________________________________________________________________________________________________
# T2.3 Add circles at the locations of capital cities for each canton, and the sizes are proportional to daily new cases per capita

sites = p1.circle("long", "lat", source=geosource, color='blue', size="size", alpha=0.7)

# ______________________________________________________________________________________________________________________
# T2.4 Create a radio button group with labels 'Density', and 'BedsPerCapita'
buttons = RadioButtonGroup(labels=labels)

# Define a function to update color mapper used in both patches and colorbar
def update_bar(new):
	for i,d in enumerate(labels):# ined, name
		if i == new:
			ColorVal = d
			TsansVal = mappers[d]['transform']
			cantons.glyph.fill_color = {"field": ColorVal,
                                 "transform" : TsansVal}
			color_bar.color_mapper = mappers[d]["transform"]

buttons.on_click(update_bar)

# ______________________________________________________________________________________________________________________
# T2.5 Add a dateslider to control which per capita daily new cases information to display

# Define a dateslider using maximum and mimimum dates, set value to be the latest date

timeslider = DateSlider(start=dates[0], end=dates[-1],value=dates[-1],  title="Date", step=1)# maybe change to datetime

# Complete the callback function
# Hints:
# 	convert the timestamp value from the slider to datetime and format it in the form of '%Y-%m-%d'
#	update columns 'size', 'dnc' with the column named '%Y-%m-%d' in merged
#	update geosource with new merged

def callback(attr, old, new):
	# Convert timestamp to datetime
	# https://stackoverflow.com/questions/9744775/how-to-convert-integer-timestamp-to-python-datetime

	date = datetime.fromtimestamp(new / 1e3)
	i = date.strftime('%Y-%m-%d')
	merged.size = merged[str(i)] * 1e5 / 5 + 10
	merged.dnc = merged[str(i)]

	geosource.geojson = merged.to_json()

# Circles change on mouse move
timeslider.on_change("value", callback)

# ______________________________________________________________________________________________________________________
# T2.6 Add a play button to change slider value and update the map plot dynamically
# https://stackoverflow.com/questions/46420606/python-bokeh-add-a-play-button-to-a-slider
# https://stackoverflow.com/questions/441147/how-to-subtract-a-day-from-a-date

# Update the slider value with one day before current date
def animate_update_slider():
	# Extract date from slider's current value
	date = timeslider.value
	date = datetime.fromtimestamp(date / 1e3)

	# Subtract one day from date and do not exceed the allowed date range
	day = timedelta(1)
	if (date - day) > dates[0]:
		newDay = date - day
		timeslider.value = newDay
	else:
		return

# Define the callback function of button
def animate():
	global callback_id
	if button.label == '► Play':
		button.label = '❚❚ Pause'
		callback_id = curdoc().add_periodic_callback(animate_update_slider, 500)
	else:
		button.label = '► Play'
		curdoc().remove_periodic_callback(callback_id)

button = Button(label='► Play', width=80, height=40)
button.on_click(animate)

curdoc().add_root(column(p1, buttons, row(timeslider, button)))

# bokeh serve --show ex4_skeleton_play.py