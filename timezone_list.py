import pandas as pd
import requests
import lxml.html as lh

long_url = "https://www.timeanddate.com/time/zones/"
sortedbytime_url = "https://www.timeanddate.com/time/current-number-time-zones.html"

def pull_from_web(url):
    table = pd.read_html(url)
    zone_table = table[0]
    print(zone_table.columns)
    print(zone_table)
    zone_table.to_csv("zones.csv")

def get_zones():
    zones = pd.read_csv("zones.csv", index_col=0)
    zone_display = zones[['UTC Offset', 'Example Location']]
    print(zone_display.head())
    return zone_display


if __name__ == "__main__":
    #pull_from_web(sortedbytime_url)
    zonelist = get_zones()