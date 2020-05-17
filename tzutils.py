from timezonefinder import TimezoneFinder
import datetime
from datetime import datetime as dt
from dateutil import tz
import logging
import pytz

def get_tz_from_coord(latitude, longitude):
    try:
        tf = TimezoneFinder()
        from_zone = tf.timezone_at(lng=longitude, lat=latitude)
        zone_source = tz.gettz(from_zone)
        utc = dt.utcnow()
        return from_zone, zone_source
    except Exception as e: 
        logging.error(e)


if __name__ == "__main__":
    

    format = '%Y-%m-%dT%H:%M:%S%z'
    datestring = '2016-09-20T16:43:45-07:00'
    #d = dt.strptime(datestring, format)

    format2 = '%Y-%m-%d %H:%M:%S.%f'
    utc = dt.utcnow()
    d = dt.strptime(str(utc), format2)

    print(datestring)
    print('Date:', d.date())
    print('Time:', d.time())


    print("\n\n")
    latitude, longitude = 52.5061, 13.358 # 'Europe/Berlin' coordinates
    from_zone, zone_source = get_tz_from_coord(latitude, longitude)
    print(from_zone)

    berlin_zone = tz.gettz('Europe/Berlin')
    print(berlin_zone)

    # current UTC
    utc = dt.utcnow()
    print(f'current UTC: {utc}')

    # Tell the datetime object that it's in UTC time zone since 
    # datetime objects are 'naive' by default
    #utc = utc.replace(tzinfo=zone_source)
    #print(f'Zone Source UTC: {utc}')

    #to_zone = tz.tzlocal()

    print("\n\n")
    to_zone = tz.gettz('America/New_York')
    print(f'To Zone: {to_zone}')
    nyc = utc.replace(tzinfo=to_zone)
    print(f'NYC: {nyc}')

    central = utc.astimezone(berlin_zone)
    print(central)

    print("\n\n")
    date_time_str = str(dt.now())
    print(date_time_str)
        
    date_time_obj = dt.strptime(date_time_str,  '%Y-%m-%d %H:%M:%S.%f')
    print(date_time_obj)

    #dto = dt.strptime(date_time_str, '%a, %d %B, %Y')
    #print(dto)
    """
    date_time = 'Mon, 21 March, 2015'
    dtj = dt.strptime(date_time,  '%a, %d %B, %Y')
    print(dtj)
    """