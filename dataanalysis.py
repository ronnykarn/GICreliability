import numpy as np
import pandas as pd
import seaborn as sns
import datetime as dt


def find_ranges(df, column, eps, value_column):
    """

    :param df:
    :param column:
    :param eps:
    :param value_column:
    :return:
    """
    # Initialize variables
    ranges = []
    start_range = None
    end_range = None

    # Iterate over each value in the column
    for i, value in enumerate(df[column]):
        if value > eps:
            if start_range is None:
                # Start a new range
                start_range = df[value_column].iloc[i]
                end_range = df[value_column].iloc[i]
            else:
                # Expand the current range
                end_range = df[value_column].iloc[i]
        elif start_range is not None:
            # End the current range
            ranges.append((start_range, end_range))
            start_range = None
            end_range = None

    # Check if there is an open range at the end
    if start_range is not None:
        ranges.append((start_range, end_range))

    # Create a new DataFrame to store the ranges
    result_df = pd.DataFrame(ranges, columns=['Start Range', 'End Range'])
    return result_df


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

# Store only values greater than 5

threshold = 5
stormTimeRanges = find_ranges(test, 'Kp', threshold, 'DATETIME')

# time delta between two time ranges
stormTimeRanges['MGMDT'] = stormTimeRanges['End Range'] - stormTimeRanges['Start Range']

# convert the time delta to integer hours and add 3 hours to include one of the end ranges
stormTimeRanges['MGMDT'] = stormTimeRanges['MGMDT'].astype('timedelta64[s]').astype('int64') / 3600 + 3


k = 1
