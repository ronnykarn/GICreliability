import numpy as np
import pandas as pd
import seaborn as sns
import datetime as dt
from datetime import timedelta


# <editor-fold desc="Functions for the script">
def find_event_ranges(df, column, eps, value_column):
    """

    :param df: input dataframe
    :param column: column over which the threshold operation is performed
    :param eps: threshold value to find continuous range
    :param value_column: column over which the ranges are needed usually time column
    :return: result_df: returns the start and end range of the required columns as a dataframe
    """
    # Initialize variables
    ranges = []
    start_range = None
    end_range = None

    # Iterate over each value in the column
    for i, value in enumerate(df[column]):
        if value >= eps:
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

    return ranges


def merge_ranges(df, cooldown):
    merged_ranges = []
    start_range = df.iloc[0]['Start Range']
    end_range = df.iloc[0]['End Range']
    max_value = df.iloc[0]['Max Value']

    for i in range(1, len(df)):
        if df.iloc[i]['Start Range'] - end_range <= timedelta(days=cooldown):
            end_range = max(end_range, df.iloc[i]['End Range'])
            max_value = max(max_value, df.iloc[i]['Max Value'])
        else:
            merged_ranges.append({'Start Range': start_range, 'End Range': end_range, 'Max Value': max_value})
            start_range = df.iloc[i]['Start Range']
            end_range = df.iloc[i]['End Range']
            max_value = df.iloc[i]['Max Value']

    merged_ranges.append({'Start Range': start_range, 'End Range': end_range, 'Max Value': max_value})
    return pd.DataFrame(merged_ranges)


# function to convert HHMM to datetime.time
def format_time(x):
    hhmm = dt.time(x)
    return hhmm


def assign_storm_category(value):
    if 5 <= value < 6:
        return 'G1'
    elif 6 <= value < 7:
        return 'G2'
    elif 7 <= value < 8:
        return 'G3'
    elif 8 <= value <= 9:
        return 'G4'


# </editor-fold>


# <editor-fold desc="Formatting GMD csv file to specific needs">
# data formatting to specific needs
gmdData = pd.read_csv('GMD_data.csv', parse_dates=[['YYYY', 'MM', 'DD']])
processedData = pd.melt(gmdData, id_vars=['YYYY_MM_DD'], value_vars=['Kp1', 'Kp2', 'Kp3', 'Kp4', 'Kp5', 'Kp6', 'Kp7',
                                                                     'Kp8'])

# rename column names after melt
processedData = processedData.rename(columns={'variable': 'time',
                                              'value': 'Kp',
                                              'YYYY_MM_DD': 'DATETIME'})

# replace Kp names to corresponding hour and format the column as time object
processedData = processedData.replace(['Kp1', 'Kp2', 'Kp3', 'Kp4', 'Kp5', 'Kp6', 'Kp7', 'Kp8'],
                                      [0, 3, 6, 9, 12, 15, 18, 21])
processedData['time'] = processedData['time'].apply(format_time)

# format the datetime column and strip the time
processedData['DATETIME'] = pd.to_datetime(processedData['DATETIME']).dt.date

# combine the date and time columns to form a single datetime column
processedData['DATETIME'] = processedData.apply(lambda r: dt.datetime.combine(r['DATETIME'], r['time']), axis=1)
processedData = processedData.sort_values(by=['DATETIME'], ignore_index=True)
processedData = processedData.drop(columns=['time'])
# </editor-fold>


# <editor-fold desc="Use the processed CSV file to calculate MGMDT, Storm intensity, and TTGMD">
#
threshold = 5
eventRanges = find_event_ranges(processedData, 'Kp', threshold, 'DATETIME')
result = []
for start, end in eventRanges:
    max_value = processedData.loc[(processedData['DATETIME'] >= start) & (processedData['DATETIME'] <= end), 'Kp'].max()
    result.append({'Start Range': start, 'End Range': end, 'Max Value': max_value})
result_df = pd.DataFrame(result)

# Merge events to recognize storms where there is activity within 1.5 days
stormRanges = merge_ranges(result_df, cooldown=1.5)

# Categorize the storms based of Max Kp value
stormRanges['category'] = stormRanges['Max Value'].apply(assign_storm_category)

# time delta between two time ranges
stormRanges['MGMDT'] = stormRanges['End Range'] - stormRanges['Start Range']

# convert the time delta to integer hours and add 3 hours to include one of the end ranges
stormRanges['MGMDT'] = stormRanges['MGMDT'].astype('timedelta64[s]').astype('int64') / 3600 + 3

# drop G1 events with Max value = 5
mask = (stormRanges['Max Value'] == 5) & (stormRanges['MGMDT'] == 3)
stormRanges = stormRanges.drop(stormRanges[mask].index).reset_index(drop=True)

# TTGMD calculation
TTGMD = []
for i in range(len(stormRanges) - 1):
    diff = stormRanges.loc[i + 1, 'Start Range'] - stormRanges.loc[i, 'End Range']
    TTGMD.append(diff)
TTGMD = pd.DataFrame({'TTGMD': TTGMD})
TTGMD = TTGMD.astype('timedelta64[s]').astype('int64') / 3600
# </editor-fold>

# export results to corresponding csv files
TTGMD.to_csv('TTGMD.csv', index=False)
stormRanges.to_csv('stormlengths.csv', index=False)

k=1