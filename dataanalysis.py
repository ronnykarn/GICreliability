import numpy as np
import pandas as pd
import seaborn as sns
import datetime as dt


# function to convert HHMM to datetime.time
def format_time(x):
    hhmm = dt.time(x)
    return hhmm


gmd = pd.read_csv('GMD_data.csv', parse_dates=[['YYYY', 'MM', 'DD']])
test = pd.melt(gmd, id_vars=['YYYY_MM_DD'], value_vars=['Kp1', 'Kp2', 'Kp3', 'Kp4', 'Kp5', 'Kp6', 'Kp7',
                                                        'Kp8'])
test = test.rename(columns={'variable': 'time',
                            'value': 'Kp',
                            'YYYY_MM_DD': 'DATETIME'})
test = test.replace(['Kp1', 'Kp2', 'Kp3', 'Kp4', 'Kp5', 'Kp6', 'Kp7', 'Kp8'], [0, 3, 6, 9, 12, 15, 18, 21])
test['DATETIME'] = pd.to_datetime(test['DATETIME']).dt.date
test['time'] = test['time'].apply(format_time)
test['DATETIME'] = test.apply(lambda r: dt.datetime.combine(r['DATETIME'], r['time']), axis=1)

test = test.sort_values(by=['DATETIME'], ignore_index=True)
test = test.drop(columns=['time'])

## Store only values greater than 5
test_storms = test[test['Kp'] > 5]

k = 1
