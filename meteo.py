from bs4 import BeautifulSoup as bSoup
import django
import django.conf
import django.template.loader
import webbrowser
import requests
import os


def chartmetuk():
    url = 'https://www.metoffice.gov.uk/weather/maps-and-charts/surface-pressure'
    source = bSoup(requests.get(url).text, 'lxml')
    # Scrape list of charts from page
    charts_list = source.find(id='colourCharts').find_all('li')
    # Extract links from list
    links = [chart.img['src'] for chart in charts_list]
    return links


def aviationweather():
    table = {'North Atlantic': '135', 'Europa/Asia': '105', 'Polar North America/Europe': '108',
             'America/Africa': '130', 'Pacific': '131', 'Polar South Africa/Australia': '109'}
    url = 'https://aviationweather.gov/data/iffdp/'
    keys = ['Latest', '6h', '12h', '18h']
    #table = {'North Atlantic': '135', 'Europa/Asia': '105'}
    # Create dictionary of dictionaries {area:{'key':url, ...}} for every area in table
    sigwx_links = {area: {k: url + f'{i}{table[area]}.gif' for k,
                          i in zip(keys, range(2, 6))} for area in table.keys()}
    return sigwx_links


def initialize_template():
    path = os.path.dirname(os.path.realpath(__file__))
    TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates',
                  'DIRS': [f'{path}/Images']}]
    django.conf.settings.configure(TEMPLATES=TEMPLATES)
    django.setup()
    template = django.template.loader.get_template('template.html')
    return path, template


def show(page, path):
    with open(f'{path}/Images/page.html', 'w') as f:
        f.write(page)
    webbrowser.get('safari').open_new_tab(f"file://{path}/Images/page.html")


def main():
    surface_links = chartmetuk()
    sigwx_links = aviationweather()
    path, template = initialize_template()
    data = {'path': path,
            'surface_links': surface_links,
            'sigwx_links': sigwx_links}
    page = template.render(data)
    show(page, path)


if __name__ == '__main__':
    main()
    # aviationweather()
