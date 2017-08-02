import pandas as pd
from datetime import datetime

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
    return trap_species, trap

