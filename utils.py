import pandas as pd
import numpy as np
from datetime import datetime
from geopy.distance import great_circle
BoT = datetime(2007,1,1).date()


def read_basic_dataset():
    def closer_weather_station(row):
        if (great_circle((row['Latitude'], row['Longitude']), (41.995, -87.933)).meters > 
            great_circle((row['Latitude'], row['Longitude']), (41.786, -87.752)).meters):
            return 2
        return 1
    def past_n_days(row, daycnt, qty, wdf, func):
        reldf = wdf[(wdf['Station'] == row['Station'])
                    & (wdf['ddate'] <= row['ddate']) 
                    & (wdf['ddate'] >= row['ddate'] - daycnt)]
        if func == 'max':
            return reldf[qty].max()
        elif func == 'min':
            return reldf[qty].min()
        elif func == 'avg':
            return reldf[qty].mean()
        elif func == 'sum':
            return reldf[qty].sum()
        
    train_df = pd.read_csv('west_nile/input/train.csv')
    test_df = pd.read_csv('west_nile/input/test.csv')
    weather_df = pd.read_csv('west_nile/input/weather.csv')
    weather_df.replace(['  T'], [0.001], inplace=True) # Trace = very little
    weather_df.replace(['M'], [np.nan], inplace=True) # Missing = nan (pad using filla)
    weather_df.replace(['-'], [np.nan], inplace=True) # 
    weather_df['PrecipTotal'] = pd.to_numeric(weather_df['PrecipTotal'])
    weather_df['Tavg'] = pd.to_numeric(weather_df['Tavg'])
    weather_df['DewPoint'] = pd.to_numeric(weather_df['DewPoint'])
    weather_df['StnPressure'] = pd.to_numeric(weather_df['StnPressure'])
    weather_df.fillna(method='backfill', inplace=True)   # replace all missing values of 2d station with values of 1st station
    weather_df['ddate'] = weather_df.Date.apply(lambda _: (datetime.strptime(_,'%Y-%m-%d').date() - BoT).days)
    cwdf = weather_df.copy()
    
    weather_df['10dtmax_avg'] = weather_df.apply(lambda _: past_n_days(_, 10, 'Tmax', cwdf, 'avg'), axis=1)
    weather_df['10dtmax_max'] = weather_df.apply(lambda _: past_n_days(_, 10, 'Tmax', cwdf, 'max'), axis=1)
    weather_df['10dtmax_min'] = weather_df.apply(lambda _: past_n_days(_, 10, 'Tmax', cwdf, 'min'), axis=1)
    weather_df['10dtmin_avg'] = weather_df.apply(lambda _: past_n_days(_, 10, 'Tmin', cwdf, 'avg'), axis=1)
    weather_df['10dtmin_max'] = weather_df.apply(lambda _: past_n_days(_, 10, 'Tmin', cwdf, 'max'), axis=1)
    weather_df['10dtmin_min'] = weather_df.apply(lambda _: past_n_days(_, 10, 'Tmin', cwdf, 'min'), axis=1)
    weather_df['10dtavg_avg'] = weather_df.apply(lambda _: past_n_days(_, 10, 'Tavg', cwdf, 'avg'), axis=1)
    weather_df['10dtavg_max'] = weather_df.apply(lambda _: past_n_days(_, 10, 'Tavg', cwdf, 'max'), axis=1)
    weather_df['10dtavg_min'] = weather_df.apply(lambda _: past_n_days(_, 10, 'Tavg', cwdf, 'min'), axis=1)
    weather_df['10dpcp_tot'] = weather_df.apply(lambda _: past_n_days(_, 10, 'PrecipTotal', cwdf, 'sum'), axis=1)
    weather_df['10ddwp_avg'] = weather_df.apply(lambda _: past_n_days(_, 10, 'DewPoint', cwdf, 'avg'), axis=1)
    weather_df['10dprs_avg'] = weather_df.apply(lambda _: past_n_days(_, 10, 'StnPressure', cwdf, 'avg'), axis=1)

    
    train_df['station'] = train_df.apply(closer_weather_station, axis=1)
    test_df['station'] = test_df.apply(closer_weather_station, axis=1)

    
    train_with_weather_df = pd.merge(left=train_df, right=weather_df, how='inner', 
                                     left_on=['Date', 'station'], right_on=['Date','Station'])
    train_with_weather_df['year'] = train_with_weather_df.apply(lambda _: datetime.strptime(_['Date'], '%Y-%m-%d')
                                                                 .date().year, axis=1)
    train_with_weather_df['month'] = train_with_weather_df.apply(lambda _: datetime.strptime(_['Date'], '%Y-%m-%d')
                                                                 .date().month, axis=1)
    train_with_weather_df['week'] = train_with_weather_df.apply(lambda _: datetime.strptime(_['Date'], 
                                                                                            '%Y-%m-%d').date().isocalendar()[1], 
                                                                axis=1)
    test_with_weather_df = pd.merge(left=test_df, right=weather_df, how='inner', 
                                     left_on=['Date', 'station'], right_on=['Date','Station'])
    test_with_weather_df['year'] = test_with_weather_df.apply(lambda _: datetime.strptime(_['Date'], '%Y-%m-%d')
                                                               .date().year, axis=1)
    test_with_weather_df['month'] = test_with_weather_df.apply(lambda _: datetime.strptime(_['Date'], '%Y-%m-%d')
                                                               .date().month, axis=1)
    test_with_weather_df['week'] = test_with_weather_df.apply(lambda _: datetime.strptime(_['Date'], 
                                                                                            '%Y-%m-%d').date().isocalendar()[1], 
                                                                axis=1)
    train_target_df = train_with_weather_df[['WnvPresent']]
    return train_with_weather_df, train_target_df, test_with_weather_df