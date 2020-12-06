import pandas as pd
from bokeh.layouts import row
from bokeh.models import ColumnDataSource, HoverTool, Select
from bokeh.plotting import figure
from bokeh.io import output_file, curdoc
# import warnings
# warnings. filterwarnings("ignore")  # i decided to not show warnings because everything is intended that way


# This exercise will be graded using the following Python and library versions:
###############
# Python 3.8
# Bokeh 2.2.1
# Pandas 1.1.2
###############
# output_notebook()
# define your callback function of the Select widget here. Only do this once you've followed the rest of the
# instructions below and you actually reach the part where you have to add and configure the Select widget.
# the general idea is to set the data attribute of the plots ColumnDataSource to the data entries of the different
# ColumnDataSources you construct during the data processing. This data change should then automatically be displayed
# in the plot. Take care that the bar-labels on the y axis also reflect this change.

# read data from .csv file
df = pd.read_csv('AZA_MLE_Jul2018_utf8.csv', encoding='utf-8')
# construct list of indizes to remove unnecessary columns
cols = [1, 3]
cols.extend([i for i in range(7, 15)])
df.drop(df.columns[cols], axis=1, inplace=True)

# task 1

# rename the columns of the data frame according to the following mapping:
# 'Species Common Name': 'species'
# 'TaxonClass': 'taxon_class'
# 'Overall CI - lower': 'ci_lower'
# 'Overall CI - upper': 'ci_upper'
# 'Overall MLE': 'mle'
# 'Male Data Deficient': 'male_deficient'
# 'Female Data Deficient': 'female_deficient'
df.rename(columns={'Species Common Name': 'species',
'TaxonClass': 'taxon_class',
'Overall CI - lower': 'ci_lower',
'Overall CI - upper': 'ci_upper',
'Overall MLE': 'mle',
'Male Data Deficient': 'male_deficient',
'Female Data Deficient': 'female_deficient'}, inplace=True)

# There's an entry in the aves dataframe with a species named 'Penguin, Northern & Southern Rockhopper (combined)'.
# Rename that species to 'Penguin, Rockhopper'
df.loc[df.species == "Penguin, Northern & Southern Rockhopper"].species='Penguin, Rockhopper'


# df=df.loc[(df["taxon_class"]=='Mammalia') | (df["taxon_class"]=='Aves')| (df["taxon_class"]=='Reptilia')]
dfMam=df.loc[(df.male_deficient != "yes") & (df.female_deficient != "yes") & (df.taxon_class == "Mammalia") ]
dfAves=df.loc[(df.male_deficient != "yes") & (df.female_deficient != "yes") & (df.taxon_class == "Aves") ]
dfRept=df.loc[(df.male_deficient != "yes") & (df.female_deficient != "yes") & (df.taxon_class == "Reptilia") ]


# Remove outliers, split the dataframe by taxon_class and and construct a ColumnDataSource from the clean DataFrames
# hints:
# we only use the following three taxon classes: 'Mammalia', 'Aves', 'Reptilia'
# use dataframe.loc to access subsets of the original dataframe and to remove the outliers
# each time you sort the dataframe reset its index
# outliers are entries which have male and/or female data deficient set to yes
# reference dataframe: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html
# reference columndatasource: https://bokeh.pydata.org/en/latest/docs/reference/models/sources.html
# construct three independent dataframes based on the aforementioned taxon classes and remove the outliers
# sort the dataframes by 'mle' in descending order and then reset the index
# reduce each dataframe to contain only the 10 species with the highest 'mle'



dfMam.sort_values(by=['mle'],ascending=False, inplace=True)
dfMam.reset_index(drop=True, inplace=True)
dfMam=dfMam[:10]
dfAves.sort_values(by=['mle'],ascending=False, inplace=True)
dfAves.reset_index(drop=True,inplace=True)
dfAves=dfAves[:10]
dfRept.sort_values(by=['mle'],ascending=False, inplace=True)
dfRept.reset_index(drop=True,inplace=True)
dfRept=dfRept[:10]
# sort the dataframe in the correct order to display it in the plot and reset the index again.
# hint: the index decides the y location of the bars in the plot. You might have to modify it to have a visually
# appealing barchart
dfMam.sort_values(by=['mle'],ascending=True, inplace=True)
dfMam.reset_index(drop=True, inplace=True)
dfAves.sort_values(by=['mle'],ascending=True, inplace=True)
dfAves.reset_index(drop=True,inplace=True)
dfRept.sort_values(by=['mle'],ascending=True, inplace=True)
dfRept.reset_index(drop=True,inplace=True)

# construct a ColumDataSource for each of the dataframes
sourceMam=ColumnDataSource(data=dict(
    left=dfMam.ci_lower,
    right=dfMam.ci_upper,
    y=dfMam.species,
))
sourceAves=ColumnDataSource(data=dict(
    left=dfAves.ci_lower,
    right=dfAves.ci_upper,
    y=dfAves.species,
))
sourceRept=ColumnDataSource(data=dict(
    left=dfRept.ci_lower,
    right=dfRept.ci_upper,
    y=dfRept.species,
))

source=ColumnDataSource(data=dict(
    left=dfMam.ci_lower,
    right=dfMam.ci_upper,
    y=dfMam.species,
))


group = source.data["y"]
p = figure(y_range=group, x_range=(0,50), plot_width=800, plot_height=550, toolbar_location=None,
           title="Medium Life Expectancy of Animals in Zoos")
p.hbar(y="y", left='left', right='right', height=0.4, source=source)

p.ygrid.grid_line_color = "grey"
p.xaxis.axis_label = "Medium life expectancy"
p.yaxis.axis_label = "species"

# Create a dropdown
select = Select(title="TaxonClass", value="Mammalia", options=["Mammalia", "Reptilia", "Aves"])


def callback(attr, old, new):

    if select.value == "Mammalia":
        new_data = dict(
        left = sourceMam.data['left'],
        right = sourceMam.data['right'],
        y = sourceMam.data['y'])


    elif select.value == "Reptilia":
        new_data = dict(
        left = sourceRept.data['left'],
        right = sourceRept.data['right'],
        y = sourceRept.data['y'])


    else:
        new_data = dict(
        left = sourceAves.data['left'],
        right = sourceAves.data['right'],
        y = sourceAves.data['y'])

    source.data = new_data
    p.y_range.factors=list(source.data["y"])



# task 2:

# configure mouse hover tool
# reference: https://bokeh.pydata.org/en/latest/docs/user_guide/categorical.html#hover-tools
# your tooltip should contain the data of 'ci_lower' and 'ci_upper' named 'low' and 'high' in the visualization

# construct a figure with the correct title, axis labels, x and y range, add the hover tool and disable the toolbar

# add the horizontal bar chart to the figure and configure it correctly
# the lower limit of the bar should be ci_lower and the upper limit ci_upper

# add a Select tool (dropdown selection) and configure its 'on_change' callback. Define the callback function in the
# beginning of the document and write it such that the user can choose which taxon_class is visualized in the plot.
# the default visualization at startup should be 'Mammalia'

# use curdoc to add your plot and selection widget such that you can start a bokeh server and an interactive plotting
# session.
# you should be able to start a plotting session executing one of the following commands in a terminal:
# (if you're using a virtual environment you first have to activate it before using these commands. You have to be in
# the same folder as your dva_hs20_ex1_skeleton.py file.)
# Interactive session: bokeh serve --show dva_hs20_ex1_skeleton.py
# If the above doesn't work use the following: python -m bokeh serve --show dva_hs20_ex1_skeleton.py
# For interactive debugging sessions you can use one of the two commands below. As long as you don't close your last
# browser tab you can save your changes in the python file and the bokeh server will automatically reload your file,
# reflecting the changes you just made. Be aware that after changes leading to errors you usually have to restart
# the bokeh server by interrupting it in your terminal and executing the command again.
# bokeh serve --dev --show dva_hs20_ex1_skeleton.py
# python -m bokeh serve --dev --show dva_hs20_ex1_skeleton.py

hover = HoverTool(tooltips = [
("low", "@left"),
("high", '@right')
])

select.on_change("value", callback)
p.add_tools(hover)
curdoc().add_root(row(p, select))

curdoc().title = 'dva_ex1'