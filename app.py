# -*- coding: utf-8 -*-


import collections

from bokeh.models import LinearColorMapper, ColumnDataSource, ColorBar
from bokeh.palettes import RdBu11, RdBu10, BrBG11, Blues9
from bokeh.plotting import figure, curdoc
from bokeh.layouts import row, column, gridplot
from bokeh.models.widgets import Select, Paragraph, Slider, Div
from bokeh.sampledata.us_states import data as states
from bokeh.themes import built_in_themes
import numpy as np
import pandas as pd

## Load and process data
states = collections.OrderedDict(sorted(states.items()))
states.pop('DC')
states.pop('AK')
states.pop('HI')

dfs = dict()
for year in range(2013, 2018):
    tmp_df = pd.read_csv(f'data/{year}_processed.csv',
                         usecols=['State', 'Year', 'Median AQI', 'prcp', 'tmax'])
    tmp_df = tmp_df[ ~tmp_df['State'].isin(['AK', 'HI'])]
    tmp_df.index = list(range(48))
    dfs[year] = tmp_df

df = pd.concat(dfs, names=['year'])

data_2018 = {}
years = list(range(2013, 2018))
df2 = df.set_index(['State', 'Year'])
for n, state in enumerate(states):
    state_data = {}
    state_data['Year'] = 2018
    state_data['State'] = state
    for dtype in ['tmax', 'prcp', 'Median AQI']:
        fit = np.polyfit(years, df2.loc[state, dtype], 1)
        state_data[dtype] = 2018 * fit[0] + fit[1]
        data_2018[n] = state_data



dfs[2018] = pd.DataFrame(data_2018).T
df = pd.concat(dfs, names=['year'], sort=False)



# Selection box
slider_left = Slider(start=2013, end=2018, value=2013, step=1, title='Comparison Year Left')
slider_right = Slider(start=2013, end=2018, value=2014, step=1, title='Comparison Year Right')

state_xs = [state["lons"] for state in states.values()]
state_ys = [state["lats"] for state in states.values()]
state_names = [state['name'] for state in states.values()]

# get color palletes
Blues9.reverse()
diffs = RdBu11.copy()
diffs_prcp = RdBu11.copy()
diffs_prcp.reverse()
# diffs.reverse()
temp_cmap = LinearColorMapper(palette=RdBu11, low=df['tmax'].min(), high=df['tmax'].max())
diff_cmap = LinearColorMapper(palette=diffs, low=-25, high=25)
diff_cmap_prcp = LinearColorMapper(palette=diffs_prcp, low=-25, high=25)
prcp_cmap = LinearColorMapper(palette=Blues9, low=0, high=df['prcp'].max())
aqi_cmap = LinearColorMapper(palette=BrBG11, low=df['Median AQI'].min(), high=df['Median AQI'].max())

temp_cbar = ColorBar(color_mapper=temp_cmap, label_standoff=12, border_line_color=None, location=(0,0))
prcp_cbar = ColorBar(color_mapper=prcp_cmap, label_standoff=12, border_line_color=None, location=(0,0))
aqi_cbar = ColorBar(color_mapper=aqi_cmap, label_standoff=12, border_line_color=None, location=(0,0))
diff_cbar1 = ColorBar(color_mapper=diff_cmap, label_standoff=12, border_line_color=None, location=(0,0))
diff_cbar2 = ColorBar(color_mapper=diff_cmap_prcp, label_standoff=12, border_line_color=None, location=(0,0))
diff_cbar3 = ColorBar(color_mapper=diff_cmap, label_standoff=12, border_line_color=None, location=(0,0))

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

    tmax_right=(df.loc[2014]['tmax']-df.loc[2013]['tmax'])/df.loc[2013]['tmax']*100,
    prcp_right=(df.loc[2014]['prcp']-df.loc[2013]['prcp'])/df.loc[2013]['prcp']*100,
    aqi_right=(df.loc[2014]['Median AQI']-df.loc[2013]['Median AQI'])/df.loc[2013]['Median AQI']*100,
)

source = ColumnDataSource(data=data)



def make_plot(title, field, cmap, units, cbar=None):


    p = figure(
        title=title,
        x_axis_location=None, y_axis_location=None,
        plot_width=550, plot_height=350,
        x_range=(-125, -65),
        tools=['tap,reset'],
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
    left=slider_left.value
    right=slider_right.value

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

        tmax_right=(df.loc[int(right)]['tmax']-df.loc[int(left)]['tmax'])/df.loc[int(left)]['tmax']*100,
        prcp_right=(df.loc[int(right)]['prcp']-df.loc[int(left)]['prcp'])/df.loc[int(left)]['prcp']*100,
        aqi_right=(df.loc[int(right)]['Median AQI']-df.loc[int(left)]['Median AQI'])/df.loc[int(left)]['Median AQI']*100,
    )
    source.data = data

slider_left.on_change('value', year_change)
slider_right.on_change('value', year_change)


grid = gridplot([[Div(text="<h1>Climate analysis</h1><p>This application visualizes the regional "
                      "temperature, precipitation, and air quality for the contiguous United States."
                      "The values for 2018 are predicted using a simple linear regression."
                      "Individual states can be selected, with the selection reset button in the "
                      "top right.</p>", width=800)],
                 [slider_left, slider_right],
                 [make_plot('Max Temperature (F)', 'tmax_left', temp_cmap, 'F', cbar=temp_cbar),
                  make_plot('', 'tmax_middle', temp_cmap, 'F'),
                  make_plot('Percent Change', 'tmax_right', diff_cmap, '%', cbar=diff_cbar1)],
                 [make_plot('Precipitation (In)', 'prcp_left', prcp_cmap, 'inches', cbar=prcp_cbar),
                  make_plot('', 'prcp_middle', prcp_cmap, 'inches'),
                  make_plot('Percent Change', 'prcp_right', diff_cmap_prcp, '%', cbar=diff_cbar2)],
                 [make_plot('Air Quality Index', 'aqi_left', aqi_cmap, 'AQI', cbar=aqi_cbar),
                  make_plot('', 'aqi_middle', aqi_cmap, 'AQI'),
                  make_plot('Percent Change', 'aqi_right', diff_cmap, '%', cbar=diff_cbar3)],
                 ],
                merge_tools=True,
                )

curdoc().add_root(grid)
