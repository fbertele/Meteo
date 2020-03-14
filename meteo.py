from get_info import *
import django
from django.conf import settings
from django.template.loader import get_template
from django.shortcuts import render
import webbrowser
import os
import sys


def initialize_template():
    path = os.path.dirname(os.path.realpath(__file__))
    TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates',
                  'DIRS': [f'{path}/Resources']}]
    settings.configure(TEMPLATES=TEMPLATES)
    django.setup()
    template = get_template('template.html')
    return path, template


def show(page, path):
    with open(f'{path}/Resources/page.html', 'w') as f:
        f.write(page)
    webbrowser.get('safari').open_new_tab(f"file://{path}/Resources/page.html")


def main():
    location = mapquest(sys.argv[1]) if len(sys.argv) > 1 else ('52.160', '8.130')
    surface_links = [chartmetuk(), chartsdwd()]
    sigwx_links = aviationweather()
    path, template = initialize_template()
    data = {'path': path,
            'location': location,
            'surface_links': surface_links,
            'sigwx_links': sigwx_links}
    page = template.render(data)
    show(page, path)


if __name__ == '__main__':
    main()
