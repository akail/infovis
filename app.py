# -*- coding: utf-8 -*-


import collections

from bokeh.models import LinearColorMapper, ColumnDataSource, ColorBar
from bokeh.palettes import RdBu11, BrBG11, Blues9
from bokeh.plotting import figure, curdoc
from bokeh.layouts import row, column, gridplot
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


# Selection box
year_select_left = Select(value='2013', options=list(map(str, range(2013,2018))))
year_select_right = Select(value='2014', options=list(map(str, range(2013,2018))))

state_xs = [state["lons"] for state in states.values()]
state_ys = [state["lats"] for state in states.values()]
state_names = [state['name'] for state in states.values()]

# get color palletes
# note to selv, low and high can be set for the color mappers
Blues9.reverse()
diffs = RdBu11.copy()
diffs.reverse()
temp_cmap = LinearColorMapper(palette=RdBu11)
diff_cmap = LinearColorMapper(palette=diffs)
prcp_cmap = LinearColorMapper(palette=Blues9)
aqi_cmap = LinearColorMapper(palette=BrBG11)

temp_cbar = ColorBar(color_mapper=temp_cmap, label_standoff=12, border_line_color=None, location=(0,0))
prcp_cbar = ColorBar(color_mapper=prcp_cmap, label_standoff=12, border_line_color=None, location=(0,0))
aqi_cbar = ColorBar(color_mapper=aqi_cmap, label_standoff=12, border_line_color=None, location=(0,0))

data=dict(
    x=state_xs,
    y=state_ys,
    name=state_names,
    tmax_left=df.loc[2013]['tmax'],
    prcp_left=df.loc[2013]['prcp'],
    aqi_left=df.loc[2013]['Median AQI'],

    tmax_middle=df.loc[2014]['tmax'],
    prcp_middle=df.loc[2014]['prcp'],
    aqi_middle=df.loc[2014]['Median AQI'],

    tmax_right=df.loc[2014]['tmax']-df.loc[2013]['tmax'],
    prcp_right=df.loc[2014]['prcp']-df.loc[2013]['prcp'],
    aqi_right=df.loc[2014]['Median AQI']-df.loc[2013]['Median AQI'],
)

source = ColumnDataSource(data=data)



def make_plot(title, field, cmap, units, cbar=None):


    p = figure(
        title=title,
        x_axis_location=None, y_axis_location=None,
        plot_width=550, plot_height=350,
        x_range=(-180, -50),
        tooltips=[
            ("Name", "@name"), (field, f"@{field} {units}"), ("(Long, Lat)", "($x, $y)")
        ])


    p.grid.grid_line_color = None
    p.hover.point_policy = "follow_mouse"

    p.patches('x', 'y', source=source,
              fill_color={'field': field, 'transform': cmap},
              fill_alpha=0.7, line_color="white", line_width=0.5,
              )
    if cbar:
        p.add_layout(cbar, 'right')
    return p

def year_change(attrname, old, new):
    left = year_select_left.value
    right = year_select_right.value

    data=dict(
        x=state_xs,
        y=state_ys,
        name=state_names,
        tmax=df.loc[int(new)]['tmax'],
        prcp=df.loc[int(new)]['prcp'],
        aqi=df.loc[int(new)]['Median AQI'],

        tmax_left=df.loc[int(left)]['tmax'],
        prcp_left=df.loc[int(left)]['prcp'],
        aqi_left=df.loc[int(left)]['Median AQI'],

        tmax_middle=df.loc[int(right)]['tmax'],
        prcp_middle=df.loc[int(right)]['prcp'],
        aqi_middle=df.loc[int(right)]['Median AQI'],

        tmax_right=df.loc[int(right)]['tmax']-df.loc[int(left)]['tmax'],
        prcp_right=df.loc[int(right)]['prcp']-df.loc[int(left)]['prcp'],
        aqi_right=df.loc[int(right)]['Median AQI']-df.loc[int(left)]['Median AQI'],
    )
    source.data = data

year_select_left.on_change('value', year_change)
year_select_right.on_change('value', year_change)


grid = gridplot([[year_select_left, year_select_right, None],
                 [make_plot('Average Max Temperature', 'tmax_left', temp_cmap, 'F', cbar=temp_cbar),
                  make_plot('Average Max Temperature', 'tmax_middle', temp_cmap, 'F'),
                  make_plot('Average Max Temperature', 'tmax_right', diff_cmap, 'F')],
                 [make_plot('Precipitation', 'prcp_left', prcp_cmap, 'inches', cbar=prcp_cbar),
                  make_plot('Precipitation', 'prcp_middle', prcp_cmap, 'inches'),
                  make_plot('Precipitation', 'prcp_right', diff_cmap, 'inches')],
                 [make_plot('Air Quality Index', 'aqi_left', aqi_cmap, 'AQI', cbar=aqi_cbar),
                  make_plot('Air Quality Index', 'aqi_middle', aqi_cmap, 'AQI'),
                  make_plot('Air Quality Index', 'aqi_right', diff_cmap, 'AQI')],
                 ],
                merge_tools=True,
                )

curdoc().add_root(grid)
