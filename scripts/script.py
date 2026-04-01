#to do:
#test calendar.txt and calendar_dates.txt filtering
#add error handling for missing files or columns

import pandas as pd
from datetime import datetime
import config

PATH = "/Users/felixbaum/projects/umdeeznuts/data/f-shuttleum~md~us-latest/"
stop_times = pd.read_csv(PATH + "stop_times.txt")
trips = pd.read_csv(PATH + "trips.txt")
routes = pd.read_csv(PATH + "routes.txt")
calendar = pd.read_csv(PATH + "calendar.txt")
calendar_dates = pd.read_csv(PATH + "calendar_dates.txt")
stops = pd.read_csv(PATH + "stops.txt")
#create list of fav_stops from config.py as ints
fav_stops = [int(stop) for stop in config.FAV_STOPS]
origin = config.ORIGIN

df = pd.merge(stop_times, trips, on='trip_id', how='inner')
#convert route_id to string to match routes.txt
df['route_id'] = df['route_id'].astype(str)
df = pd.merge(df, routes, on='route_id', how='inner')
df = df[df['stop_id'].isin(fav_stops)]
#filter to only active trips using calendar.txt and calendar_dates.txt
today = datetime.today().strftime('%Y%m%d')
print("Today's date:", today)
services_today = calendar[(calendar['start_date'] <= int(today)) & (calendar['end_date'] >= int(today)) & (calendar[datetime.today().strftime('%A').lower()] == 1)]['service_id'].tolist()
services_today += calendar_dates[calendar_dates['date'] == int(today)]['service_id'].tolist()
df = df[df['service_id'].isin(services_today)] #test this later


#convert arrival_time to datetime
df['arrival_time'] = pd.to_datetime(df['arrival_time'], format='%H:%M:%S', errors = 'coerce').dt.time
#filter to only next 3-5 active arrivals at each stop, sorted by arrival time
df = df[df['arrival_time'] >= datetime.now().time()]
df = df.sort_values(by='arrival_time')
df = df.groupby('stop_id').head(5) #top 5 arrivals per stop


df = pd.merge(df, stops[['stop_id', 'stop_name']], on='stop_id', how='left')
#reorder columns
df = df[['stop_id', 'stop_name', 'arrival_time', 'route_short_name', 'trip_headsign']]
print(df)