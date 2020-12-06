import numpy as np
from bokeh.models import ColumnDataSource, Button, Select, Div
from bokeh.sampledata.iris import flowers
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row

# Important: You must also install pandas for the data import.

# calculate the cost of the current medoid configuration
# The cost is the sum of all minimal distances of all points to the closest medoids
def get_cost(meds):
    distsum = 0
    for i in range(data.shape[0]):
        point = np.array(data.iloc[i])
        dist1 = (abs(meds[0] - point)).sum()
        dist2 = (abs(meds[1] - point)).sum()
        dist3 = (abs(meds[2] - point)).sum()

        distsum += min(dist1, min(dist2, dist3))
    return distsum  # total cost

def k_medoids(source):  # dont know if i can add params
    # number of clusters:
    k = 3
    # Use the following medoids if random medoid is set to false in the dashboard. These numbers are indices into the
    # data array.
    random = source.data["Random"][0]
    if random:
        rand1 = np.random.random_integers(data.shape[0])
        rand2 = np.random.random_integers(data.shape[0])
        while rand2 == rand1:
            rand2 = np.random.random_integers(data.shape[0])
        rand3 = np.random.random_integers(data.shape[0])
        while rand3 == rand1 or rand3 == rand2:
            rand3 = np.random.random_integers(data.shape[0])

        medoids = [rand1, rand2, rand3]
        meds = [data.iloc[medoids[y]] for y in range(len(medoids))]

    else:
        medoids = [24, 74, 124]
        meds = [data.iloc[medoids[y]] for y in range(len(medoids))]

    meds = np.array(meds)
    costOld = get_cost(meds)
    better = True
    while better:
        # assigning points to medoids
        Team1 = []
        Team2 = []
        Team3 = []
        for i in range(data.shape[0]):
            point = np.array(data.iloc[i])
            dist1 = (abs(meds[0] - point)).sum()
            dist2 = (abs(meds[1] - point)).sum()
            dist3 = (abs(meds[2] - point)).sum()

            if dist1 < dist2 and dist1 < dist3:
                Team1.append(i)

            elif dist2 < dist1 and dist2 < dist3:
                Team2.append(i)

            else:
                Team3.append(i)

        # recalc the medoids
        # med1
        bestMedi1 = medoids[0]
        bestCost1 = costOld
        for i in range(len(Team1)):
            currcost = get_cost(np.array([data.iloc[Team1[i]], meds[1], meds[2]]))
            if bestCost1 > currcost:
                bestMedi1 = Team1[i]
                bestCost1 = currcost

        # med2
        bestMedi2 = medoids[1]
        bestCost2 = costOld
        for i in range(len(Team2)):
            currcost = get_cost(np.array([meds[0], data.iloc[Team2[i]], meds[2]]))
            if bestCost2 > currcost:
                bestMedi2 = Team2[i]
                bestCost2 = currcost

        # med3
        bestMedi3 = medoids[2]
        bestCost3 = costOld
        for i in range(len(Team3)):
            currcost = get_cost(np.array([meds[0], meds[1], data.iloc[Team3[i]]]))
            if bestCost3 > currcost:
                bestMedi3 = Team3[i]
                bestCost3 = currcost

        if bestCost1 < bestCost2 and bestCost1 < bestCost3:
            medoids = [bestMedi1, medoids[1], medoids[2]]
        elif bestCost2 < bestCost1 and bestCost2 < bestCost3:
            medoids = [medoids[0], bestMedi2, medoids[2]]
        else:
            medoids = [medoids[0], medoids[1], bestMedi3]

        meds = [data.iloc[medoids[y]] for y in range(len(medoids))]
        meds = np.array(meds)

        # check if it got better
        costNew = get_cost(meds)
        if costNew < costOld:
            better = True
        else:
            better = False
        costOld = costNew
        # print(costOld)    # for testing

    newList = [0 for _ in range(data.shape[0])]
    for i in Team1:
        newList[i] = "red"
    for i in Team2:
        newList[i] = "green"
    for i in Team3:
        newList[i] = "blue"
    source.data["colors"] = newList
    return costNew

# read and store the dataset
data = flowers.copy(deep=True)
data = data.drop(['species'], axis=1)

# create a color column in your dataframe and set it to gray on startup
df = data.copy()
df["color"] = "darkgrey"
random = [False for _ in range(data.shape[0])]
# Create a ColumnDataSource from the data
source = ColumnDataSource(data=dict(
    sepalL=df.iloc[:, 0],
    sepalW=df.iloc[:, 1],
    petalL=df.iloc[:, 2],
    petalW=df.iloc[:, 3],
    colors=df.iloc[:, 4],
    Random=random  # just to have a var which can change at runtime
    )
)
# k_medoids(source) # for testing

# Create a select widget, a button, a DIV to show the final clustering cost and two figures for the scatter plots.
p = figure(title='Scatterplot of Flower distribution by petal length and sepal length', x_range=(1, 7))
p.xaxis.axis_label = "Petal length"
p.yaxis.axis_label = "Sepal length"
p.scatter("petalL", "sepalL", fill_color="colors", line_color="colors", fill_alpha=.7, source=source)
# ______________________________________________________________________________________________________________________
select = Select(title="Random Medoids", value="False", options=["True", "False"])

def callback(attr, old, new):
    if select.value == "True":
        source.data["Random"][0] = True

    else:  # False
        source.data["Random"][0] = False

select.on_change("value", callback)
# ______________________________________________________________________________________________________________________
button = Button(label="Cluster Data", button_type="primary")

def handler():
    cost = k_medoids(source)
    div.text = str("The final cost is: %.2f" % cost)

button.on_click(handler)
# ______________________________________________________________________________________________________________________
# text
div = Div(text="""The final cost is: 99999""", width=200, height=100)
# ______________________________________________________________________________________________________________________
p2 = figure(title='Scatterplot of Flower distribution by petal width and petal length', x_range=(0, 2.6))
p2.yaxis.axis_label = "Petal length"
p2.xaxis.axis_label = "Petal width"
p2.scatter("petalW", "petalL", fill_color="colors", line_color="colors", fill_alpha=.7, source=source)
# use curdoc to add your widgets to the document
curdoc().add_root(row(column(select, button, div), p, p2))
curdoc().title = "DVA_ex_3"

# use on of the commands below to start your application
# bokeh serve --show dva_ex3_skeleton_HS20.py
# python -m bokeh serve --show dva_ex3_skeleton_HS20.py
# bokeh serve --dev --show dva_ex3_skeleton_HS20.py
# python -m bokeh serve --dev --show dva_ex3_skeleton_HS20.py