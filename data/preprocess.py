# -*- coding: utf-8 -*-

import csv
import pandas as pd
from IPython import embed

def main():
    # load state data
    with open('states.csv') as state_file:
        states = dict([line.strip().split(',') for line in state_file])

    # load station data
    stations = {}
    with open('ghcnd-stations.txt', 'r') as station_file:
        for line in station_file.readlines():
            station, lat, lon, _, state = line.split(maxsplit=4)
            state = state.split(maxsplit=1)[0]
            if len(state.strip()) != 2:
                continue

            if state.upper() not in states.values():
                continue

            stations[station] = state

    def get_station_state(station):
        try:
            return stations[station]
        except KeyError:
            return None


    def get_state_abbr(state):
        try:
            return states[state]
        except KeyError:
            return None

    data = {}
    for year in range(2013,2018):
        # Load air quality data
        df_aqi = pd.read_csv('annual_aqi_by_county_%s.csv' % year)
        df_aqi['State'] = df_aqi['State'].apply(get_state_abbr)
        df_aqi = df_aqi.loc[df_aqi['State'].notnull()]
        df = df_aqi.groupby('State').mean()

        # load climate data
        df_a = pd.read_csv('%s_tp.csv' % year, header=None, names=['station','dtype','value'], usecols=[0,2,3])
        df_a['state'] = df_a['station'].apply(get_station_state)
        df_a = df_a.loc[ df_a['state'].notnull() ]
        df_a = df_a.groupby(['dtype', 'state']).mean()

        prcp = df_a.loc['PRCP']
        tmax = df_a.loc['TMAX']
        prcp.rename({'value': 'prcp'}, axis=1, inplace=True)
        tmax.rename({'value': 'tmax'}, axis=1, inplace=True)

        df = df.join(prcp, on='State')
        df = df.join(tmax, on='State')

        df.to_csv('%s_processed.csv' % year)

        # embed()
        # break



if __name__ == "__main__":
    main()
