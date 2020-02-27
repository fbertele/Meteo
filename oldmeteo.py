from django.conf import settings
from django.template.loader import get_template
from bs4 import BeautifulSoup as bSoup
import django
import webbrowser
import requests
import shutil
import os


def chartsdwd():
    url = 'https://www.dwd.de/DWD/wetter/wv_spez/hobbymet/wetterkarten'
    uri_list = ['/bwk_bodendruck_na_ana.png', '/ico_tkboden_na_024.png',
                '/ico_tkboden_na_V36.png', '/ico_tkboden_na_036.png', '/ico_tkboden_na_048.png']
    name_list = ['now', '24h', '36h(12 UTC)', '36h(00 UTC)', '48h']
    iterable = list(zip(uri_list, name_list))
    for uri, name in iterable:
        image_url = f"https://www.dwd.de/DWD/wetter/wv_spez/hobbymet/wetterkarten/{uri}"
        resp = requests.get(image_url, stream=True)
        with open(f'Images/Surface Chart {name}.png', 'wb') as local_file:
            resp.raw.decode_content = True
            # Copy the response stream raw data to local image file.
            shutil.copyfileobj(resp.raw, local_file)


def chartmetuk():
    url = 'https://www.metoffice.gov.uk/weather/maps-and-charts/surface-pressure'
    source = bSoup(requests.get(url).text, 'lxml')
    # Scrape list of charts from page
    charts_list = source.find(id='colourCharts').find_all('li')
    # Extract (titles) and links from list
    #titles = [chart.get('data-value') for chart in charts_list]
    links = [chart.img['src'] for chart in charts_list]
    # zipper = tuple(zip([i for i in range(len(links))], links))
    # for i, link in zipper:
    #     resp = requests.get(link, stream=True)
    #     with open(f'Images/SurfaceChart{i}.png', 'wb') as local_file:
    #         # Copy the response stream raw data to local image file.
    #         shutil.copyfileobj(resp.raw, local_file)
    return links


def initialize_template():
    path = os.path.dirname(os.path.realpath(__file__))
    TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates',
                  'DIRS': [f'{path}/Images']}]
    settings.configure(TEMPLATES=TEMPLATES)
    django.setup()
    return path


def show(page, path):
    with open(f'{path}/Images/page.html', 'w') as f:
        f.write(page)
    webbrowser.get('safari').open(f"file://{path}/Images/page.html")


def main(links):
    path = initialize_template()
    template = get_template('template.html')
    data = {'path': path,
            'links': links
            }
    page = template.render(data)
    show(page, path)


if __name__ == '__main__':
    links = chartmetuk()
    main(links)
