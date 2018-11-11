# -*- coding: utf-8 -*-


import collections

from bokeh.models import LogColorMapper, ColumnDataSource
from bokeh.palettes import Viridis6 as palette
from bokeh.plotting import figure, curdoc
from bokeh.layouts import row, column
from bokeh.models.widgets import Select
from bokeh.sampledata.us_states import data as states
import pandas as pd

## Load and process data
states = collections.OrderedDict(sorted(states.items()))
states.pop('DC')

dfs = dict()
for year in range(2013, 2018):
    dfs[year] = pd.read_csv(f'data/{year}_processed.csv')


df = pd.concat(dfs)
df.head()

# Selection box
year_select = Select(value='2013', options=list(map(str, range(2013,2018))))

state_xs = [state["lons"] for state in states.values()]
state_ys = [state["lats"] for state in states.values()]
state_names = [state['name'] for state in states.values()]
palette.reverse()
color_mapper = LogColorMapper(palette=palette)

data=dict(
    x=state_xs,
    y=state_ys,
    name=state_names,
    tmax=df.loc[2013]['tmax'],
    prcp=df.loc[2013]['prcp'],
    aqi=df.loc[2013]['Median AQI'],
)
source = ColumnDataSource(data=data)



def make_plot(field='tmax'):



    TOOLS = "pan,wheel_zoom,reset,hover,save"

    p = figure(
        title="Test Map", tools=TOOLS,
        x_axis_location=None, y_axis_location=None,
        plot_width=550, plot_height=350,
        x_range=(-180, -50),
        tooltips=[
            ("Name", "@name"), (field, f"@{field}%"), ("(Long, Lat)", "($x, $y)")
        ])
    p.grid.grid_line_color = None
    p.hover.point_policy = "follow_mouse"

    p.patches('x', 'y', source=source,
              fill_color={'field': field, 'transform': color_mapper},
              fill_alpha=0.7, line_color="white", line_width=0.5)
    return p

def year_change(attrname, old, new):

    data=dict(
        x=state_xs,
        y=state_ys,
        name=state_names,
        tmax=df.loc[int(new)]['tmax'],
        prcp=df.loc[int(new)]['prcp'],
        aqi=df.loc[int(new)]['Median AQI'],
    )
    source.data = data

year_select.on_change('value', year_change)

# show(column(year_select,p))
row_1 = year_select
row_2 = row(make_plot('tmax'), make_plot('prcp'))
row_3 = make_plot('aqi')

curdoc().add_root(column(row_1, row_2, row_3))

# curdoc().add_root(column(year_select, make_plot('prcp')))
