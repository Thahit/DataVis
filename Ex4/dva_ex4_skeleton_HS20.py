import numpy as np
import os

import bokeh
from bokeh.layouts import layout, row
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColorBar, LinearColorMapper, BasicTicker
from colorcet import CET_L16

from colorsys import hsv_to_rgb

output_file('DVA_ex4.html')
color = CET_L16

def to_bokeh_image(rgba_uint8):
    if len(rgba_uint8.shape) > 2 \
            and int(bokeh.__version__.split(".")[0]) >= 2 \
            and int(bokeh.__version__.split(".")[1]) >= 2:
        np_img2d = np.zeros(shape=rgba_uint8.shape[:2], dtype=np.uint32)
        view = np_img2d.view(dtype=np.uint8).reshape(rgba_uint8.shape)
        view[:] = rgba_uint8[:]
    else:
        np_img2d = rgba_uint8
    return [np_img2d]

def get_divergence(vx_wind, vy_wind):
    # Use np.gradient to calculate the gradient of a vector field. Find out what exactly the return values represent and
    # use the appropriate elements for your calculations
    grad1x, grad1y, grad1z = np.gradient(vx_wind)
    grad2x, grad2y, grad2z = np.gradient(vy_wind)

    div_v = np.add(grad1x, grad2y)

    return div_v

def get_vorticity(vx_wind, vy_wind):
    # Calculate the gradient again and use the appropriate results to calculate the vorticity. Think about what happens
    # to the z-component and the derivatives with respect to z for a two dimensional vector field.
    # (You can save the gradient in the divergence calculations or recalculate it here. Since the gradient function is
    # fast and we have rather small data slices the impact of recalculating it is negligible.)

    grad1x, grad1y, grad1z = np.gradient(vx_wind)
    grad2x, grad2y, grad2z = np.gradient(vy_wind)

    vort_v = np.subtract(grad2x, grad1y)

    return vort_v

# Calculates the HSV colors of the xy-windspeed vectors and maps them to RGBA colors
def angle(vector):  #https://stackoverflow.com/questions/64561040/finding-angle-between-the-x-axis-and-a-vector-on-the-unit-circle
    vector_2 = [1,0]
    vector1 = vector / np.linalg.norm(vector)
    vector2 = vector_2 / np.linalg.norm(vector_2)
    dot_product = np.dot(vector1, vector2)
    angle = np.arccos(dot_product)
    return angle

def vector_color_coding(vx_wind, vy_wind):
    # Calculate the hue (H) as the angle between the vector and the positive x-axis
    xv_wind = vx_wind[:, :, 20]
    yv_wind = vy_wind[:, :, 20]

    H = np.zeros((len(vx_wind), len(vx_wind[0])))

    for i in range(len(xv_wind)):
        for j in range(len(xv_wind[0])):
            H[i, j] = np.arctan2(xv_wind[i, j], yv_wind[i, j])
    # print(H.max(), H.min())# between -pi and pi
    # print(H.shape)

    # Saturation (S) can be set to 1
    S = 1

    # The brightness value (V) is set on the normalized magnitude of the vector

    V = np.sqrt(xv_wind ** 2 + yv_wind ** 2)    # 500 x 500
    V = (V - np.min(V)) / (np.max(V) - np.min(V))
    V = V*255
    # print(V.max(), V.min())# between -pi and pi
    # print(V.shape)

    # normalize
    H = H+np.pi
    H = H/(2*np.pi)
    # print(H.shape)
    # print(H.max(), H.min())  # 0.9999990652763828 6.702438916249953e-06

    # Either use colorsys.hsv_to_rgb or implement the color conversion yourself using the
    # algorithm for the HSV to RGB conversion, see https://www.rapidtables.com/convert/color/hsv-to-rgb.html
    rgba_colors = np.zeros((len(V), len(V[0]), 4))

    for i in range(len(V)):
        for j in range(len(V[0])):
            rgba_colors[i, j,0], rgba_colors[i, j,1], rgba_colors[i, j, 2] = hsv_to_rgb(H[i, j], S, V[i, j])
            rgba_colors[i, j, 3] = 255    #probl.


    # rgba_colors=rgba_colors.astype(int)
    # print(rgba_colors.max(), rgba_colors.min())
    # print(rgba_colors)
    # print(rgba_colors.shape) # (500, 500, 4)

    # The RGBA colors have to be saved as uint8 for the bokeh plot to properly work
    return rgba_colors.astype('uint8')

# Load and process the required data
print('processing data')
xWind_file = 'Uf24.bin'
xWind_path = os.path.abspath(os.path.dirname(xWind_file))
xWind_data = np.fromfile(os.path.join(xWind_path, xWind_file), dtype=np.dtype('>f'))
xWind_data = np.reshape(xWind_data, [500, 500, 100], order='F')
xWind_data = np.flipud(xWind_data)

# Replace the missing "no data" values with the average of the dataset
filtered_average = np.average(xWind_data[xWind_data < 1e35])
xWind_data[xWind_data == 1e35] = filtered_average

yWind_file = 'Vf24.bin'
yWind_path = os.path.abspath(os.path.dirname(yWind_file))
yWind_data = np.fromfile(os.path.join(yWind_path, yWind_file), dtype=np.dtype('>f'))
yWind_data = np.reshape(yWind_data, [500, 500, 100], order='F')
yWind_data = np.flipud(yWind_data)

# Replace the missing "no data" values with the average of the dataset
filtered_average = np.average(yWind_data[yWind_data < 1e35])
yWind_data[yWind_data == 1e35] = filtered_average

wind_vcc = vector_color_coding(xWind_data, yWind_data)
wind_divergence = get_divergence(xWind_data, yWind_data)
wind_vorticity = get_vorticity(xWind_data, yWind_data)
print('data processing completed')

fig_args = {'x_range': (0,500), 'y_range': (0,500), 'width': 500, 'height': 400, 'toolbar_location': None, 'active_scroll': 'wheel_zoom'}
img_args = {'dh': 500, 'dw': 500, 'x': 0, 'y': 0}
cb_args = {'ticker': BasicTicker(), 'label_standoff': 12, 'border_line_color': None, 'location': (0,0)}

# Create x wind speed plot
color_mapper_xWind = LinearColorMapper(palette=CET_L16, low=np.amin(xWind_data), high=np.amax(xWind_data))
xWind_plot = figure(title="x-Wind speed (West - East)", **fig_args)
xWind_plot.image(image=to_bokeh_image(xWind_data[:,:,20]), color_mapper=color_mapper_xWind, **img_args)
xWind_color_bar = ColorBar(color_mapper=color_mapper_xWind, **cb_args)
xWind_plot.add_layout(xWind_color_bar, 'right')

# Create y wind speed plot
color_mapper_yWind = LinearColorMapper(palette=CET_L16, low=np.amin(yWind_data), high=np.amax(yWind_data))
yWind_plot = figure(title="y-Wind speed South - North", **fig_args)
yWind_plot.image(image=to_bokeh_image(yWind_data[:,:,20]), color_mapper=color_mapper_yWind, **img_args)
yWind_color_bar = ColorBar(color_mapper=color_mapper_yWind, **cb_args)
yWind_plot.add_layout(yWind_color_bar, 'right')

# _____________________________________________________________________________________________________________________
# Create divergence plot
color_mapper_DivWind = LinearColorMapper(palette=CET_L16, low=np.amin(wind_divergence[:, :, 20]), high=np.amax(wind_divergence[:, :, 20]))
divergence_plot = figure(title="Divergence", **fig_args)
divergence_plot.image(image=to_bokeh_image(wind_divergence[:, :, 20]), color_mapper=color_mapper_DivWind, **img_args)
DivWind_color_bar = ColorBar(color_mapper=color_mapper_DivWind, **cb_args)
divergence_plot.add_layout(DivWind_color_bar, 'right')

# Create vorticity plot
color_mapper_VolWind = LinearColorMapper(palette=CET_L16, low=np.amin(wind_vorticity[:, :, 20]), high=np.amax(wind_vorticity[:, :, 20]))
vorticity_plot = figure(title="Vorticity", **fig_args)
vorticity_plot.image(image=to_bokeh_image(wind_vorticity[:, :, 20]), color_mapper=color_mapper_VolWind, **img_args)
VolWind_color_bar = ColorBar(color_mapper=color_mapper_VolWind, **cb_args)
vorticity_plot.add_layout(DivWind_color_bar, 'right')

# Create vector color coding plot
# Use the bokeh image_rgba function for the plotting
vcc_plot = figure(title="Vector Color Coding", **fig_args)
vcc_plot.image_rgba(image=to_bokeh_image(wind_vcc), **img_args)

# Create and show plot layout
final_layout = layout(row(xWind_plot, yWind_plot), row(divergence_plot, vorticity_plot, vcc_plot))
show(final_layout)