import pandas as pd
from datetime import datetime

def read_basic_dataset():
    train_df = pd.read_csv('west_nile/input/train.csv')
    test_df = pd.read_csv('west_nile/input/test.csv')
    weather_df = pd.read_csv('west_nile/input/weather.csv')
    weather_df = weather_df[weather_df['Station'] == 2]
    train_with_weather_df = pd.merge(left=train_df, right=weather_df, how='inner', left_on=['Date'], right_on=['Date'])
    train_with_weather_df['month'] = train_with_weather_df.apply(lambda _: datetime.strptime(_['Date'], '%Y-%m-%d').date().month, axis=1)
    train_with_weather_df['week'] = train_with_weather_df.apply(lambda _: _['month'] * 4 + datetime.strptime(_['Date'], '%Y-%m-%d').date().day / 7, axis=1)
    test_with_weather_df = pd.merge(left=test_df, right=weather_df, how='inner', left_on=['Date'], right_on=['Date'])
    test_with_weather_df['month'] = test_with_weather_df.apply(lambda _: datetime.strptime(_['Date'], '%Y-%m-%d').date().month, axis=1)
    test_with_weather_df['week'] = test_with_weather_df.apply(lambda _: _['month'] * 4 + datetime.strptime(_['Date'], '%Y-%m-%d').date().day / 7, axis=1)
    train_target_df = train_with_weather_df[['WnvPresent']]
    return train_with_weather_df, train_target_df, test_with_weather_df