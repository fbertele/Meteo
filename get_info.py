from math import radians, degrees, sin, cos, asin, acos, sqrt
from bs4 import BeautifulSoup as bSoup
import concurrent.futures
import requests
import json
import config
import os


def get_coord(location):
    key = config.api_key
    url = f'http://www.mapquestapi.com/geocoding/v1/address?key={key}&location={location}'
    source = requests.get(url).text
    response = json.loads(source)['results'][0]['locations'][0]
    # Extract coordinates and return them in a tuple
    coordinates = tuple(round(response['latLng'][tag], 3) for tag in ['lat', 'lng'])
    return coordinates


def swc_ukmetoffice():
    url = 'https://www.metoffice.gov.uk/weather/maps-and-charts/surface-pressure'
    source = bSoup(requests.get(url).text, 'lxml')
    # Scrape list of charts from page
    charts_list = source.find(id='colourCharts').find_all('li')
    # Extract links from list
    surface_links_uk = [chart.img['src'] for chart in charts_list]
    return surface_links_uk


def swc_dwd():
    url = 'https://www.dwd.de/DWD/wetter/wv_spez/hobbymet/wetterkarten'
    uri_list = ['/bwk_bodendruck_na_ana.png', '/ico_tkboden_na_024.png',
                '/ico_tkboden_na_V36.png', '/ico_tkboden_na_036.png', '/ico_tkboden_na_048.png']
    name_list = ['now', '24h', '36h(12 UTC)', '36h(00 UTC)', '48h']
    iterable = list(zip(uri_list, name_list))
    # Create list of dwd surface chart links
    surface_links_dwd = [url + uri for uri in uri_list]
    return surface_links_dwd


def sigwx_aviationweather():
    table = {'North Atlantic': '135', 'Europe/Asia': '105', 'North/South America': '129',
             'America/Africa': '130', 'Pacific': '131', 'Europe/Africa': '104',
             'Asia/Australia': '106', 'Pacific': '128', 'South Africa/Australia Polar': '109',
             'Europe/Asia Polar': '107', 'North America/Europe Polar': '108',
             'North Atlantic Polar': '132', 'North Pacific Polar': '133',
             'South Pacific Polar': '134'}
    url = 'https://aviationweather.gov/data/iffdp/'
    time = ['Latest', '6h', '12h', '18h']
    # Create dictionary of dictionaries {area:{'time':url, ...}} for each area in table
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


def get_metar(coords, radius=80, filename='airports.json'):
    icao_codes, names = airports_codes(coords, radius=radius, filename=filename)
    icao_codes = ' '.join([elem for elem in icao_codes])
    url = f'https://www.aviationweather.gov/metar/data?ids={icao_codes}&format=decoded&taf=on&layout=off'
    page = bSoup(requests.get(url).text, 'lxml')
    tables = page.find_all('table')
    tds, metar_taf_raw = [], []
    style = {'\nTAF for': 'table-success', '\nMETAR for': 'table-success', '\nText': 'table-primary'}
    for table in tables:
        # Find all raw metars and tafs
        metar = table.find_all(
            'td', attrs={'style': 'background-color: #CCCCCC; font-weight: bold'})
        # Place them in a list
        metar = metar_taf_raw.append('\n'.join([elem.text for elem in metar]))
        tag_value_style = []
        # Create [[tag, value, style], ...] for all the tds on the page
        for elem in table.find_all('tr'):
            # Get [tag, value] pairs
            tag_value = elem.text.split(':', 1)
            # Add bootstrap class style following style dict
            tag_value_style.append(
                tag_value + [(style[tag_value[0]]) if tag_value[0] in style.keys() else ''])
        # Collect all [[tag, value, style], ...] for different metar, taf and airports
        tds.append(tag_value_style)
    # Join 2 by 2 raw the metars and taf for same airport
    metar_taf_raw = list(zip(*[iter(metar_taf_raw), ] * 2))
    # Join names, metar_taf_raw, metar, taf all together in a list
    # names_metar_taf = [(airport_name, (metar_raw, taf_raw), [[metar_tag, metar_value],..],[taf_tag, taf_value], ...]), ...]
    names_metar_taf = list(zip(names, metar_taf_raw, *[iter(tds), ] * 2))
    return names_metar_taf


def sat_aviationweather():

    def sat_helper(type):
        url = f'https://aviationweather.gov/satellite/intl?region=b1&type={type}'
        page = bSoup(requests.get(url).text, 'lxml')
        links = page.find(id='content').find_all('script')
        # Get function that place image uris in image_url list
        url_fun = links[-1].text.strip('\n')
        # Initialise image_url longer than needed
        image_url = [None]*len(url_fun)
        # Execute function and fill image_url with image uris
        image = exec(compile(url_fun, '*', 'exec'))
        # Remove unnecessary padding and complete url with main domain
        sat_links = [f'https://aviationweather.gov{elem}' for elem in image_url if elem]
        return sat_links

    # Create dictionary {name:tag, ...} for sat images types
    types = {'Infrared': 'irbw', 'Infrared coloured': 'ircol',
             'Visible': 'vis', 'Water Vapour': 'wv'}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Create dictionary {name:[link1, ...], ...} for names in types keys
        results = {name: executor.submit(sat_helper, tag).result() for name, tag in types.items()}
    return results


if __name__ == '__main__':
    # pass
    print(get_coord('milano'))
