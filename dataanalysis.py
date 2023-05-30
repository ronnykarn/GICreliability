import numpy as np
import pandas as pd
import seaborn as sns
import datetime as dt


# <editor-fold desc="Functions for the script">
def find_ranges(df, column, eps, value_column):
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

    return ranges


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


# <editor-fold desc="Use the processed CSV file to calculate MGMDT and Storm intensity">
#
threshold = 5
stormRanges = find_ranges(processedData, 'Kp', threshold, 'DATETIME')
result = []
for start, end in stormRanges:
    max_value = processedData.loc[(processedData['DATETIME'] >= start) & (processedData['DATETIME'] <= end), 'Kp'].max()
    result.append({'Start Range': start, 'End Range': end, 'Max Value': max_value})
result_df = pd.DataFrame(result)

# Categorize the storms based of Max Kp value
result_df['category'] = result_df['Max Value'].apply(assign_storm_category)

# time delta between two time ranges
result_df['MGMDT'] = result_df['End Range'] - result_df['Start Range']

# convert the time delta to integer hours and add 3 hours to include one of the end ranges
result_df['MGMDT'] = result_df['MGMDT'].astype('timedelta64[s]').astype('int64') / 3600 + 3

result_df.to_csv('stormlengths.csv', index=False)
# </editor-fold>

k = 1
