import pandas as pd
from datetime import datetime
from geopy.distance import great_circle

def get_multirow_df(feature_df):
    multirow_cnt = feature_df.groupby(['Date', 'Trap', 'Species']).count().sort_values(['Address'], ascending=False)[['Address']]
    multirow_cnt.columns = ['rowcount']
    return multirow_cnt

def get_month_virus_share(feature_df):
    try:
        feature_df.drop('virusshare_t', axis=1, inplace=True)
    except ValueError as ve:
        pass
    try:
        feature_df.drop('virusshare_ts', axis=1, inplace=True)
    except ValueError as ve:
        pass
    use_df = feature_df.copy()
    use_df['month'] = use_df.Date.apply(lambda _: datetime.strptime(_,'%Y-%m-%d').date().month)
    use_df['week'] = use_df.Date.apply(lambda _: datetime.strptime(_,'%Y-%m-%d').date().timetuple().tm_yday)
    trap_species = use_df.groupby(['month', 'Trap', 'Species']).sum()
    trap_species['virusshare_ts'] = trap_species.apply(lambda _: _['WnvPresent']/_['NumMosquitos'] 
                                                              if _['NumMosquitos'] else 0, axis=1)
    trap_species = trap_species[['virusshare_ts']]
    
    trap = use_df.groupby(['month', 'Trap']).sum()
    trap['virusshare_t'] = trap.apply(lambda _: _['WnvPresent']/_['NumMosquitos'] 
                                                              if _['NumMosquitos'] else 0, axis=1)
    trap = trap[['virusshare_t']]
    
    species = use_df.groupby(['Species']).sum()
    species['virusshare_s'] = species.apply(lambda _: _['WnvPresent']/_['NumMosquitos'] 
                                                              if _['NumMosquitos'] else 0, axis=1)
    species = species[['virusshare_s']]
    return trap_species, trap, species

def create_trap_distance_matrix(ungrouped_df):
    def gcd_for_row(row):
        loc1 = (row['Latitude_x'], row['Longitude_x'])
        loc2 = (row['Latitude_y'], row['Longitude_y'])
        return great_circle(loc1, loc2).meters
    trap_location_list = ungrouped_df.groupby(['Trap']).mean()[['Latitude', 'Longitude']]
    trap_location_list['trap'] = trap_location_list.index
    trap_location_list['Dummy'] = 0
    trap_location_matrix = pd.merge(left=trap_location_list, right=trap_location_list, 
                                    left_on=['Dummy'], right_on = ['Dummy'])
    trap_location_matrix.set_index(['trap_x', 'trap_y'], inplace=True)
    trap_location_matrix['distance'] = trap_location_matrix.apply(gcd_for_row, axis=1)
    return trap_location_matrix[['distance']]

def get_nearest_trap(trap_distance_df, trap_id):
    nearest_trap_id = trap_distance_df.loc[trap_id].sort_values(['distance']).index[1]
    distance = trap_distance_df.loc[trap_id, nearest_trap_id]['distance']
    return nearest_trap_id, distance

def get_nearest_trap_list(trap_distance_df, trap_id):
    return trap_distance_df.loc[trap_id].sort_values(['distance'])