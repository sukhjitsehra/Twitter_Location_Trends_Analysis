import sys
from datetime import datetime, timedelta
import pytz
from LocationTrendRepository import *

def handler():
    """Caller function according to arguments."""
    if len(sys.argv) < 2:
        print ("Not enough arguments")
        exit()
    SETTINGS = load_settings()
    if sys.argv[1] == "store":
        store(SETTINGS)
    elif sys.argv[1] == "search":
        if len(sys.argv) < 4:
            print ("Not enough arguments. Provide args hourly/daily and count.")
            exit(0)
        mode = ""
        if sys.argv[2] not in ["hourly", "daily", "date"]:
            print ("Incorrect argument.")
            exit(0)
        mode = sys.argv[2]
        
        if mode in ["hourly", "daily"]:
            period = 0
            try:
                period = abs(int(sys.argv[3]))
            except Exception as e:
                print ("Incorrect arguments.")
                exit(0)
            if period < 1:
                print ("Period has to be greater than 1")
                exit(0)
            search(SETTINGS, mode, period)
        elif mode in ["date"]:
            try:
                date = datetime.strptime(sys.argv[3], "%Y-%m-%d")
                search(SETTINGS, mode, date)
            except Exception as e:
                print ("Incorrect date format. Please enter date in YYYY-MM-DD form.")
        
def store(SETTINGS):
    """Caller function to store data in DB."""
    auth_token = get_auth_token(SETTINGS)
    digest = get_trends(SETTINGS, auth_token)
    store_trends(SETTINGS, digest)
    
def search(SETTINGS, mode, period):
    """Caller function to search for trends based on time intervals."""
    utc = pytz.UTC
    ce = pytz.timezone("Canada/Eastern")
    cur_time = datetime.now(tz = utc)
    
    if mode == "date":
        period = period.replace(tzinfo = ce)
        time_steps_ce = [period]
        for i in range(24):
            time_steps_ce.append(time_steps_ce[-1] + timedelta(hours = 1))
        time_steps = [i.astimezone(utc) for i in time_steps_ce]
    elif mode == "hourly":
        cur_hour = cur_time.replace(minute = 0, second = 0, microsecond = 0)
        time_steps = [cur_time, cur_hour]
        for i in range(period - 1):
            time_steps.append(time_steps[-1] - timedelta(hours = 1))
        time_steps = time_steps[::-1]
        time_steps_ce = [i.astimezone(ce) for i in time_steps]
    elif mode == "daily":
        cur_day = cur_time.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
        time_steps = [cur_time, cur_day]
        for i in range(period - 1):
            time_steps.append(time_steps[-1] - timedelta(days = 1))
        time_steps = time_steps[::-1]
        time_steps_ce = [i.astimezone(ce) for i in time_steps]
    
    time_format = "%Y-%m-%d %H:%M:%S"
    for i in range(len(time_steps) - 1):
        start_utc = time_steps[i].strftime(time_format)
        end_utc = time_steps[i + 1].strftime(time_format)
        start_ce = time_steps_ce[i].strftime(time_format)
        end_ce = time_steps_ce[i + 1].strftime(time_format)
        print ("{} Canada/Eastern - {} Canada/Eastern:".format(start_ce, end_ce))
        trends = trend_in_interval(SETTINGS, start_utc, end_utc)
        for name in trends:
            print ("{}\t{}".format(name, trends[name]))

if __name__ == "__main__":
    handler()