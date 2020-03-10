from bs4 import BeautifulSoup as bSoup
import requests


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
    times = ['Latest', '6h', '12h', '18h']
    # Create dictionary of dictionaries {area:{'times':url, ...}} for every area in table
    sigwx_links = {area: {k: url + f'{i}{table[area]}.gif' for k,
                          i in zip(times, range(2, 6))} for area in table.keys()}
    return sigwx_links


if __name__ == '__main__':
    main()
