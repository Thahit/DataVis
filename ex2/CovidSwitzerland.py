#!/usr/bin/env python
# coding: utf-8


import pandas as pd 
from math import pi
import numpy as np
from bokeh.io import output_file, show, save
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool,FactorRange
from bokeh.palettes import viridis
# import bokeh.palettes as bp
 
# Goal: Draw a line chart displaying averaged daily new cases for all cantons in Switzerland.
# Dataset: covid19_cases_switzerland_openzh-phase2.csv
# Interpretation: value on row i, column j is either the cumulative covid-19 case number of canton j on date i or null value




### Task 1: Data Preprocessing


## T1.1 Read data into a dataframe, set column "Date" to be the index 

url = 'https://github.com/daenuprobst/covid19-cases-switzerland/blob/master/covid19_cases_switzerland_openzh-phase2.csv?raw=true'

raw = pd.read_csv(url, index_col="Date", usecols=range(0,27))


# Initialize the first row with zeros, and remove the last column 'CH' from dataframe
# raw=raw.drop("CH",axis=1) # not used anymore
raw.iloc[0,:] =0


# Fill null with the value of previous date from same canton
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.fillna.html
raw.fillna(method="ffill",inplace=True) #=forwardfill



## T1.2 Calculate and smooth daily case changes

# Compute daily new cases (dnc) for each canton, e.g. new case on Tuesday = case on Tuesday - case on Monday;
# Fill null with zeros as well

dnc = raw.diff()
dnc.fillna(0)



# Smooth daily new case by the average value in a rolling window, and the window size is defined by step
# Why do we need smoothing? How does the window size affect the result?
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.rolling.html
step = 3
dnc_avg = dnc.rolling(step).mean()  
# is was not specified, if the rolling was centered centered=False



# dnc_avg.fillna(0) # was not specified to fill with 0 again, but i guess it makes sense



## T1.3 Build a ColumnDataSource 

# Extract all canton names and dates
# NOTE: be careful with the format of date when it is used as x input for a plot
cantons = dnc_avg.columns
date = pd.to_datetime(raw.index.tolist())

# Create a color list to represent different cantons in the plot, you can either construct your own color patette or use the Bokeh color pallete
color_palette = viridis(26)




# Build a dictionary with date and each canton name as a key, i.e., {'date':[], 'AG':[], ..., 'ZH':[]}
# For each canton, the value is a list containing the averaged daily new cases
source_dict = {"date":date
}
for c in cantons:
    source_dict[c]=list(dnc_avg[c])
source = ColumnDataSource(data=source_dict)



### Task 2: Data Visualization

## T2.1: Draw a group of lines, each line represents a canton, using date, dnc_avg as x,y. Add proper legend.
# https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/line.html?highlight=line#bokeh.models.glyphs.Line
# https://docs.bokeh.org/en/latest/docs/user_guide/interaction/legends.html

p = figure(plot_width=1000, plot_height=800, x_axis_type="datetime")
p.title.text = 'Daily New Cases in Switzerland'

for canton,color in zip(cantons,color_palette): 
    p.line("date",canton, color=color, legend_label=canton, source=source, name=canton)


## T2.2 Add hovering tooltips to display date, canton and averaged daily new case

# (Hovertip doc) https://docs.bokeh.org/en/latest/docs/user_guide/tools.html#hovertool
# (Date hover)https://stackoverflow.com/questions/41380824/python-bokeh-hover-date-time

hover = HoverTool(
    tooltips = [
        ("date", "$x{%F}"),
        ("canton", "$name"),
        ("cases", "$y{int}"),
    ],
    formatters={
        '$x': 'datetime'
    },
)

p.add_tools(hover)



output_file("dvc_ex2.html")
p.legend.location = "top_left"
p.legend.click_policy="hide"
show(p)

# save(p)

