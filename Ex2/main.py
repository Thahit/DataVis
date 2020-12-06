import glob
import os
import numpy as np
from PIL import Image

from sklearn.manifold import TSNE
from sklearn.decomposition import PCA

from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, ImageURL
from bokeh.layouts import layout,row
from bokeh.io import output_file, show, save
# Dependencies

# Only do this once you've followed the rest of the instructions below and you actually reach the part where you have to
# configure the callback of the lasso select tool. The ColumnDataSource containing the data from the dimensionality
# reduction has an on_change callback routine that is triggered when certain parts of it are selected with the lasso
# tool. More specifically, a ColumnDataSource has a property named selected, which has an on_change routine that can be
# set to react to its "indices" attribute and will call a user defined callback function. Connect the on_change routine
# to the "indices" attribute and an update function you implement here. (This is similar to the last exercise but this
# time we use the on_change function of the "selected" attribute of the ColumnDataSource instead of the on_change
# function of the select widget).
# In simpler terms, each time you select a subset of image glyphs with the lasso tool, you want to adjust the source
# of the channel histogram plot based on this selection.
# Useful information:
# https://docs.bokeh.org/en/latest/docs/reference/models/sources.html
# https://docs.bokeh.org/en/latest/docs/reference/models/tools.html
# https://docs.bokeh.org/en/latest/docs/reference/models/selections.html#bokeh.models.selections.Selection


# Fetch the number of images using glob or some other path analyzer
N = len(glob.glob("static/*.jpg"))

# Find the root directory of your app to generate the image URL for the bokeh server
ROOT = os.path.split(os.path.abspath("."))[1] + "/"

# Number of bins per color for the 3D color histograms
N_BINS_COLOR = 16
# Number of bins per channel for the channel histograms
N_BINS_CHANNEL = 50

# Define an array containing the 3D color histograms. We have one histogram per image each having N_BINS_COLOR^3 bins.
# i.e. an N * N_BINS_COLOR^3 array
# array=[[[[0 for _ in range(N_BINS_COLOR)]for _ in range(N_BINS_COLOR)]for _ in range(N_BINS_COLOR)]for img in range(N)]
array=[[0 for _ in range(N_BINS_COLOR**3)]for img in range(N)]
ColorHistList=np.array(array)
# ColorHistList=array

# Define an array containing the channel histograms, there is one per image each having 3 channel and N_BINS_CHANNEL
# bins i.e an N x 3 x N_BINS_CHANNEL array
array2=[[[0 for _ in range(N_BINS_CHANNEL)]for _ in range(3)] for img in range(N)]
ChannelHistList=np.array(array2)

# initialize an empty list for the image file paths
URLList=[]
# the instructions are very unclaer, I can't even get to the visualisation because of it


# Compute the color and channel histograms
for idx, f in enumerate(glob.glob("static/*.jpg")):
    # open image using PILs Image package
    im = Image.open(f)
    # Convert the image into a numpy array and reshape it such that we have an array with the dimensions (N_Pixel, 3)
    nArray=np.array(im)     # dim 288, 640,3
    ordered=np.reshape(nArray, (-1,3))
    # Compute a multi dimensional histogram for the pixels, which returns a cube        ## 3d? r,g,b
    # reference: https://numpy.org/doc/stable/reference/generated/numpy.histogramdd.html

    # MultiDimHist, edges=np.histogramdd(ordered, bins=(N_BINS_COLOR,N_BINS_COLOR,N_BINS_COLOR)) #wrong bin nr probl.
    MultiDimHist, edges = np.histogramdd(ordered, bins=(N_BINS_COLOR))

    # However, later used methods do not accept multi dimensional arrays, so reshape it to only have columns and rows
    # (N_Images, N_BINS^3) and add it to the color_histograms array you defined earlier# (N, N_BINS_COLOR^3)
    ColorHistList[idx] = np.reshape(MultiDimHist, (1, N_BINS_COLOR ** 3))
    # reference: https://numpy.org/doc/stable/reference/generated/numpy.reshape.html

    # Append the image url to the list for the server
    url = ROOT + f
    URLList.append(url)
    # Compute a "normal" histogram for each color channel (rgb)
    # reference: https://numpy.org/doc/stable/reference/generated/numpy.histogram.html
    ordered=np.array(ordered).T.tolist()# transpose

    r, edges=np.histogram(ordered[0],bins=N_BINS_CHANNEL, range=(0, 255))
    g, edges=np.histogram(ordered[1], bins=N_BINS_CHANNEL, range=(0, 255))
    b, edges=np.histogram(ordered[2], bins=N_BINS_CHANNEL, range=(0, 255))
    # and add them to the channel_histograms
    ChannelHistList[idx][0]=r
    ChannelHistList[idx][1] = g
    ChannelHistList[idx][2] = b

# Calculate the indicated dimensionality reductions
# references:
# https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html

X_embedded = TSNE(n_components=2).fit_transform(ColorHistList)

# https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html
pca = PCA(n_components=2)
pca.fit_transform(ColorHistList)
array=pca.transform(ColorHistList)

# Construct a data source containing the dimensional reduction result for both the t-SNE and the PCA and the image paths

source = ColumnDataSource(data=dict(
    TSNE1=[X_embedded[n][0] for n in range(121)],
    TSNE2=[X_embedded[n][1] for n in range(121)],
    PCA1=[array[n][0] for n in range(121)],
    PCA2=[array[n][1] for n in range(121)],
    Paths=URLList,
    )
)
#_____________________________________________________________________________________________________________________________________________________________________
# Create a first figure for the t-SNE data. Add the lasso_select, wheel_zoom, pan and reset tools to it.
TOOLS = "box_select,lasso_select,wheel_zoom,pan,reset,help"
p=figure(title='t-sne',tools=TOOLS)
p.yaxis.axis_label = "y"
p.xaxis.axis_label = "x"

# image1 = ImageURL(url=URLList[0], x=X_embedded[0][0], y=X_embedded[0][1], w=300, h=300, anchor="center")
image = ImageURL(url="Paths", x="TSNE1", y="TSNE2", w=100, h=80, anchor="center",h_units="screen",w_units="screen")
p.add_glyph(source, image)

p.sizing_mode = "stretch_both"


# And use bokehs image_url to plot the images as glyphs
# reference: https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/image_url.html

# Since the lasso tool isn't working with the image_url glyph you have to add a second renderer (for example a circle
# glyph) and set it to be completely transparent. If you use the same source for this renderer and the image_url,
# the selection will also be reflected in the image_url source and the circle plot will be completely invisible.
p.circle(x="TSNE1", y="TSNE2",size=1,fill_color="white",fill_alpha=0,line_alpha=0, source=source)

#____________________________________________________________________________________________________________________________________________________________________________
# Create a second plot for the PCA result. As before, you need a second glyph renderer for the lasso tool.
# Add the same tools as in figure 1
TOOLS = "box_select,lasso_select,wheel_zoom,pan,reset,help"
p2=figure(title='PCA',tools=TOOLS)
p2.yaxis.axis_label = "y"
p2.xaxis.axis_label = "x"

image2 = ImageURL(url="Paths", x="PCA1", y="PCA2", w=80, h=60, anchor="center",h_units="screen",w_units="screen")
p2.add_glyph(source, image2)

p2.sizing_mode = "stretch_both"
p2.circle(x="PCA1", y="PCA2",size=1,fill_color="white",fill_alpha=0,line_alpha=0, source=source)
#____________________________________________________________________________________________________________________________________________________________________________
# Construct a datasource containing the channel histogram data. Default value should be the selection of all images.
# Think about how you aggregate the histogram data of all images to construct this data source
ImUntalented=[]
for i in range(1,51):
    ImUntalented.append(i)

rAgg=np.zeros((N_BINS_CHANNEL))
for i in range(1,N):
    for y in range(N_BINS_CHANNEL):
        if ChannelHistList[i][0][y]>0:
            # rAgg[y] +=1
            rAgg[y]+=ChannelHistList[i][0][y]

gAgg=np.zeros((N_BINS_CHANNEL))
for i in range(1,N):
    for y in range(N_BINS_CHANNEL):
        if ChannelHistList[i][1][y]>0:
            # gAgg[y] +=1
            gAgg[y]+=ChannelHistList[i][1][y]

bAgg=np.zeros((N_BINS_CHANNEL))
for i in range(0,N):
    for y in range(N_BINS_CHANNEL):
        if ChannelHistList[i][2][y]>0:
            # bAgg[y] +=1
            bAgg[y]+=ChannelHistList[i][2][y]

sourceHist = ColumnDataSource(data=dict(
    x=ImUntalented,
    r=np.divide(rAgg, max(rAgg.max(),max(bAgg.max(),gAgg.max()))),
    g=np.divide(gAgg,  max(rAgg.max(),max(bAgg.max(),gAgg.max()))),
    b=np.divide(bAgg,  max(rAgg.max(),max(bAgg.max(),gAgg.max())))
))
# Construct a histogram plot with three lines.
# First define a figure and then make three line plots on it, one for each color channel.
# Add the wheel_zoom, pan and reset tools to it.
TOOLS = "box_select,lasso_select,wheel_zoom,pan,reset,help"
p3=figure(title='Channel Histogram',tools=TOOLS)
p3.yaxis.axis_label = "Frequenzy"
p3.xaxis.axis_label = "Bins"

p3.line(y="r",x="x",color="red", source=sourceHist)
p3.line(y="g",x="x",color= "green", source=sourceHist)
p3.line(y="b",x="x",color= "blue", source=sourceHist)
p3.sizing_mode = "stretch_both"

# Connect the on_change routine of the selected attribute of the dimensionality reduction ColumnDataSource with a
# callback/update function to recompute the channel histogram. Also read the topmost comment for more information.

# Construct a layout and use curdoc() to add it to your document.
curdoc().add_root(row(p, p2, p3))

# You can use the command below in the folder of your python file to start a bokeh directory app.
# Be aware that your python file must be named main.py and that your images have to be in a subfolder name "static"

# bokeh serve --show .
# python -m bokeh serve --show .
#
# dev option:
# bokeh serve --dev --show .
# python -m bokeh serve --dev --show .