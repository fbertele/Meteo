from math import radians, degrees, sin, cos, asin, acos, sqrt
from bs4 import BeautifulSoup as bSoup
import concurrent.futures
import requests
import json
import config
import os


def mapquest(location):
    key = config.api_key
    url = f'http://www.mapquestapi.com/geocoding/v1/address?key={key}&location={location}'
    source = requests.get(url).text
    response = json.loads(source)['results'][0]['locations'][0]
    # Extract coordinates and return them in a tuple
    coordinates = tuple(round(response['latLng'][tag], 3) for tag in ['lat', 'lng'])
    return coordinates


def chartmetuk():
    url = 'https://www.metoffice.gov.uk/weather/maps-and-charts/surface-pressure'
    source = bSoup(requests.get(url).text, 'lxml')
    # Scrape list of charts from page
    charts_list = source.find(id='colourCharts').find_all('li')
    # Extract links from list
    surface_links_uk = [chart.img['src'] for chart in charts_list]
    return surface_links_uk


def chartsdwd():
    url = 'https://www.dwd.de/DWD/wetter/wv_spez/hobbymet/wetterkarten'
    uri_list = ['/bwk_bodendruck_na_ana.png', '/ico_tkboden_na_024.png',
                '/ico_tkboden_na_V36.png', '/ico_tkboden_na_036.png', '/ico_tkboden_na_048.png']
    name_list = ['now', '24h', '36h(12 UTC)', '36h(00 UTC)', '48h']
    iterable = list(zip(uri_list, name_list))
    # Create list of dwd surface chart links
    surface_links_dwd = [url + uri for uri in uri_list]
    return surface_links_dwd


def aviationweather():
    table = {'North Atlantic': '135', 'Europa/Asia': '105', 'Polar North America/Europe': '108',
             'America/Africa': '130', 'Pacific': '131', 'Polar South Africa/Australia': '109'}
    url = 'https://aviationweather.gov/data/iffdp/'
    time = ['Latest', '6h', '12h', '18h']
    # Create dictionary of dictionaries {area:{'time':url, ...}} for every area in table
    sigwx_links = {area: {k: url + f'{i}{table[area]}.gif' for k,
                          i in zip(time, range(2, 6))} for area in table.keys()}
    return sigwx_links


def airports_codes(coords, radius=50, filename='airports.json'):

    def great_circle_helper(lon1, lat1, lon2, lat2):
        # Return great circle distances in Km
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        return 2 * 6371 * asin(sqrt(a))

    path = os.path.dirname(os.path.realpath(__file__))
    with open(f'{path}/Resources/{filename}', 'r') as codes:
        airpts = json.load(codes)
    distances = {}
    target_lon, target_lat = coords[1], coords[0]
    for airpt in airpts:
        # Get lat and long from airports in airports_codes
        airpt_lon, airpt_lat = [float(coord) for coord in airpt['coordinates'].split(',')]
        # Calculate distances and store them in a dictionary {'icao_code': dist, ...}
        dist = great_circle_helper(airpt_lon, airpt_lat, target_lon, target_lat)
        distances[airpt['icao_code']] = dist
    # Sort distances dictionary
    sorted_dist = {k: v for k, v in sorted(distances.items(), key=lambda item: item[1])}
    # Get icao codes for airports in the 50 km radius from target position
    target_icao_codes = [key for key, value in sorted_dist.items() if value < radius]
    # Get names of airports in target_icao_codes
    target_names = [airpt['name'] for code in target_icao_codes
                    for airpt in airpts if airpt['icao_code'] == code]
    return target_icao_codes, target_names


def get_metar(coords):

    def metar_helper(icao_code):
        url = f'https://www.aviationweather.gov/metar/data?ids={icao_code}&format=raw&taf=on'
        source = bSoup(requests.get(url).text, 'lxml')
        metar = [elem.text.replace('\xa0\xa0', '\n') for elem in source.find_all('code')]
        return metar

    icao_codes, names = airports_codes(coords)
    # Call metar_helper() in parallel for each icao_code given
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(metar_helper, icao_codes)
        result = future.result()
    # Create list of tuples from result list [(METAR1, TAF1), ...]
    result = zip(*(iter(result),) * 2)
    # Create dict from result {airport_name : (METAR, TAF), ...}
    return {k: v for k, v in zip(names, result)}


if __name__ == '__main__':
    pass
    # main()
    # get_metar(mapquest('milano'))
    # mapquest('milano')
