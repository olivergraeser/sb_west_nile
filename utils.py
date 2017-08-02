import pandas as pd
from datetime import datetime
BoT = datetime(2007,1,1).date()
cwdf = weather_df.copy()


def read_basic_dataset():
    def closer_weather_station(row):
        if (great_circle((row['Latitude'], row['Longitude']), (41.995, -87.933)).meters > 
            great_circle((row['Latitude'], row['Longitude']), (41.786, -87.752)).meters):
            return 2
        return 1
    train_df = pd.read_csv('west_nile/input/train.csv')
    test_df = pd.read_csv('west_nile/input/test.csv')
    weather_df = pd.read_csv('west_nile/input/weather.csv')
    weather_df.replace(['  T'], [0.001], inplace=True) # Trace = very little
    weather_df.replace(['M'], [np.nan], inplace=True) # Missing = nan (pad using filla)
    weather_df.replace(['-'], [np.nan], inplace=True) # 
    weather_df.fillna(method='backfill', inplace=True)   # replace all missing values of 2d station with values of 1st station

    weather_df['ddate'] = weather_df.Date.apply(lambda _: (datetime.strptime(_,'%Y-%m-%d').date() - BoT).days)
    
    weather_df['10dtmax_avg'] = weather_df.apply(lambda _: past_n_days(_, 10, 'Tmax', cwdf, 'avg'), axis=1)
    weather_df['10dtmax_max'] = weather_df.apply(lambda _: past_n_days(_, 10, 'Tmax', cwdf, 'max'), axis=1)
    weather_df['10dtmax_min'] = weather_df.apply(lambda _: past_n_days(_, 10, 'Tmax', cwdf, 'min'), axis=1)
    weather_df['10dtmin_avg'] = weather_df.apply(lambda _: past_n_days(_, 10, 'Tmin', cwdf, 'avg'), axis=1)
    weather_df['10dtmin_max'] = weather_df.apply(lambda _: past_n_days(_, 10, 'Tmin', cwdf, 'max'), axis=1)
    weather_df['10dtmin_min'] = weather_df.apply(lambda _: past_n_days(_, 10, 'Tmin', cwdf, 'min'), axis=1)
    weather_df['10dtmin_avg'] = weather_df.apply(lambda _: past_n_days(_, 10, 'Tmin', cwdf, 'avg'), axis=1)
    weather_df['10dtmin_max'] = weather_df.apply(lambda _: past_n_days(_, 10, 'Tmin', cwdf, 'max'), axis=1)
    weather_df['10dtmin_min'] = weather_df.apply(lambda _: past_n_days(_, 10, 'Tmin', cwdf, 'min'), axis=1)
    
    train_df['station'] = train_df.apply(closer_weather_station, axis=1)
    test_df['station'] = test_df.apply(closer_weather_station, axis=1)

    
    train_with_weather_df = pd.merge(left=train_df, right=weather_df, how='inner', 
                                     left_on=['Date', 'station'], right_on=['Date','station'])
    train_with_weather_df['month'] = train_with_weather_df.apply(lambda _: datetime.strptime(_['Date'], '%Y-%m-%d')
                                                                 .date().month, axis=1)
    train_with_weather_df['week'] = train_with_weather_df.apply(lambda _: _['month'] * 4 
                                                                + datetime.strptime(_['Date'], '%Y-%m-%d').date().day / 7, axis=1)
    test_with_weather_df = pd.merge(left=test_df, right=weather_df, how='inner', 
                                     left_on=['Date', 'station'], right_on=['Date','station'])
    test_with_weather_df['month'] = test_with_weather_df.apply(lambda _: datetime.strptime(_['Date'], '%Y-%m-%d')
                                                               .date().month, axis=1)
    test_with_weather_df['week'] = test_with_weather_df.apply(lambda _: _['month'] * 4 + 
                                                              datetime.strptime(_['Date'], '%Y-%m-%d').date().day / 7, axis=1)
    train_target_df = train_with_weather_df[['WnvPresent']]
    return train_with_weather_df, train_target_df, test_with_weather_df