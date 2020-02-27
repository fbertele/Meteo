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
    links = chartmetuk()
    path, template = initialize_template()
    data = {'path': path, 'links': links}
    page = template.render(data)
    show(page, path)


if __name__ == '__main__':
    main()
