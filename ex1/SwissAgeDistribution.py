#!/usr/bin/env python
# coding: utf-8


import pandas as pd 
from math import pi
from bokeh.io import output_file, show, save, output_notebook
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool,FactorRange,CustomJS
# import bokeh.palettes as bp # uncomment it if you need special colors that are pre-defined
print("Imports complete.")


### Task 1: Data Preprocessing
# ?raw=true at the end of the link
original_url = 'https://github.com/daenuprobst/covid19-cases-switzerland/blob/master/demographics_switzerland_bag.csv?raw=true'
df=pd.read_csv(original_url)
# print(df.tail())




## T1.2 Prepare data for a grouped vbar_stack plot
# Reference link, read first before starting: 
# https://docs.bokeh.org/en/latest/docs/user_guide/categorical.html#stacked-and-grouped
df=df.loc[df.canton!="CH"]


canton=df.canton.unique()
# print(canton)
age_group = df.age_group.unique()
# print(age_group)
sex = df.sex.unique()
# print(sex)


factors=[]
for c in canton:
    for a in age_group:
        factors.append((c,a))
# print(factors) 




# Use genders as stack names
stacks = ['male','female']

# Calculate total population size as the value for each stack identified by canton,age_group and sex
stackM=[]
stackF=[]
for c in canton:
    for a in age_group:
        stackF.append(df.loc[df.canton==c].loc[df.sex=="Weiblich"].loc[df.age_group==a].pop_size.sum())
        stackM.append(df.loc[df.canton==c].loc[df.sex=="Männlich"].loc[df.age_group==a].pop_size.sum())
stack_val = [stackM,stackF]

# Build a ColumnDataSource using above information
source = ColumnDataSource(data=dict(
    factors=factors,
    male=stackM,
    female=stackF,
))


### Task 2: Data Visualization


## T2.1: Visualize the data using bokeh plot functions

p=figure(x_range=FactorRange(*factors), plot_height=500, plot_width=800, title='Canton Population Visualization')
p.xaxis.major_label_orientation = "vertical"
p.yaxis.axis_label = "Population Size"
p.xaxis.axis_label = "Canton"
p.sizing_mode = "stretch_both"
p.xgrid.grid_line_color = None

p.vbar_stack(stacks, x='factors', width=0.9, alpha=0.5, color=["blue", "red"],legend_label=stacks, source=source)

## T2.2 Add the hovering tooltips to the plot using HoverTool
# To be specific, the hover tooltips should display “gender”, canton, age group”, and “population” when hovering.
# https://docs.bokeh.org/en/latest/docs/user_guide/tools.html#hovertool
# read more if you want to create fancy hover text: https://stackoverflow.com/questions/58716812/conditional-tooltip-bokeh-stacked-chart

p.legend.location = "top_left"
hover = HoverTool(tooltips = [
    ("gender", "$name"),
    ("canton, age_group", '@factors'),
    ("population", "@$name")
    ])
p.add_tools(hover)
show(p)

# # optional task 3
# # i decided to use a subset containing "my" canton
# startCanton=5
# startScope=9*startCanton
# cantonsNr=6
# endScope =startScope+cantonsNr*9
# factors2=factors[startScope:endScope]
# stackM2=stackM[startScope:endScope]
# stackF2=stackF[startScope:endScope]
#
# source2 = ColumnDataSource(data=dict(
#     factors=factors2,
#     male=stackM2,
#     female=stackF2,
# ))
#
# # zoomed in Part
# p2=figure(x_range=FactorRange(*factors2), plot_height=500, plot_width=800, title='Canton Population Visualization, Zoomed In')
# p2.xaxis.major_label_orientation = "vertical"
# p2.yaxis.axis_label = "Population Size"
# p2.xaxis.axis_label = "Canton"
# p2.sizing_mode = "stretch_both"
# p2.xgrid.grid_line_color = None
#
# p2.vbar_stack(stacks, x='factors', width=0.9, alpha=0.5, color=["blue", "red"], source=source2, legend_label=stacks)
#
# hover = HoverTool(tooltips = [
#     ("gender", "$name"),
#     ("canton, age_group", '@factors'),
#     ("population", "@$name")
#     ])
# p2.legend.location = "top_left"
# p2.add_tools(hover)
# show(p2)

