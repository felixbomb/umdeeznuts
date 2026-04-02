#to do:
#test calendar.txt and calendar_dates.txt filtering
#add error handling for missing files or columns
#assess for possible duplicates trips (same route, stop, and arrival time)
#jsonify output
#clean up code into functions and classes as needed
#117 missing headsign error? wtf?? add config harcode

import pandas as pd
from datetime import datetime
import config

PATH = config.SHUTTLE_PATH
def get_upcoming_departures():
    stop_times = pd.read_csv(PATH + "stop_times.txt")
    trips = pd.read_csv(PATH + "trips.txt")
    routes = pd.read_csv(PATH + "routes.txt")
    calendar = pd.read_csv(PATH + "calendar.txt")
    calendar_dates = pd.read_csv(PATH + "calendar_dates.txt")
    stops = pd.read_csv(PATH + "stops.txt")

    #convert relevant columns to string to prevent GTFS ID nonsense
    stop_times['trip_id'] = stop_times['trip_id'].astype(str)
    stop_times['stop_id'] = stop_times['stop_id'].astype(str)
    trips['trip_id'] = trips['trip_id'].astype(str)
    trips['route_id'] = trips['route_id'].astype(str)
    trips['service_id'] = trips['service_id'].astype(str)
    routes['route_id'] = routes['route_id'].astype(str)
    stops['stop_id'] = stops['stop_id'].astype(str)
    calendar['service_id'] = calendar['service_id'].astype(str)
    calendar_dates['service_id'] = calendar_dates['service_id'].astype(str)
    #create list of fav_stops from config.py as ints
    fav_stops = [str(stop) for stop in config.FAV_STOPS]
    origin = config.ORIGIN

    df = pd.merge(stop_times, trips, on='trip_id', how='inner')
    df = pd.merge(df, routes, on='route_id', how='inner')
    df = df[df['stop_id'].isin(fav_stops)]

    #filter to only active trips using calendar.txt and calendar_dates.txt
    today_int = int(datetime.today().strftime('%Y%m%d'))
    base_services = set(
        calendar[
            (calendar['start_date'] <= today_int) &
            (calendar['end_date'] >= today_int) &
            (calendar[datetime.today().strftime('%A').lower()] == 1)
        ]['service_id']
    )

    today_exceptions = calendar_dates[calendar_dates['date'] == today_int]
    added_services = set(today_exceptions[today_exceptions['exception_type'] == 1]['service_id'])
    removed_services = set(today_exceptions[today_exceptions['exception_type'] == 2]['service_id'])
    services_today = (base_services | added_services) - removed_services
    df = df[df['service_id'].isin(services_today)]

    #convert arrival_time to datetime
    df['arrival_seconds'] = df['arrival_time'].apply(gtfs_time_to_seconds)
    now = datetime.now()
    now_seconds = now.hour * 3600 + now.minute * 60 + now.second

    #filter to only upcoming arrivals and calculate minutes away
    #deal with possible nulls in arrival_seconds from bad GTFS data
    df = df[df['arrival_seconds'].notna()]
    df = df[df['arrival_seconds'] >= now_seconds]
    df['minutes_away'] = ((df['arrival_seconds'] - now_seconds) / 60).astype(int)
    df['arrival_display'] = df['arrival_seconds'].apply(seconds_to_time)
    df = df.sort_values(by=['stop_id', 'arrival_seconds'])
    df = df.groupby('stop_id').head(5)


    df = pd.merge(df, stops[['stop_id', 'stop_name']], on='stop_id', how='left')
    #reorder columns
    df['trip_headsign'] = df['trip_headsign'].fillna("Blue") #FIXME: 117 hardcode
    df = df[['stop_id', 'stop_name', 'arrival_display', 'minutes_away', 'route_short_name', 'trip_headsign','arrival_seconds']]
    df = df.where(pd.notnull(df), None) #replace NaNs with JSON None bc reasons (FIXME: better solution??)
    print(df[df.isna().any(axis=1)])
    return df.to_dict(orient='records')

def gtfs_time_to_seconds(t):
    parts = str(t).split(':')
    if len(parts) != 3:
        print(f"Invalid time format: {t}")
        return None
    h, m, s = map(int, parts)
    return h * 3600 + m * 60 + s

def seconds_to_time(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:02}"

if __name__ == "__main__":
    data = get_upcoming_departures()
    for row in data:
        print(row)
