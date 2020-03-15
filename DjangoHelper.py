import django
from django.conf import settings
from django.template.loader import get_template
from django.shortcuts import render
import os


class DjangoHelper(object):

    def __init__(self, data, template_folder='Resources', template_name='template.html'):
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.data = data
        self.template_folder = template_folder
        self.template_name = template_name
        self.page = self.initialize_template()

    def initialize_template(self):
        TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates',
                      'DIRS': [f'{self.path}/{self.template_folder}']}]
        settings.configure(TEMPLATES=TEMPLATES)
        django.setup()
        template = get_template(f'{self.template_name}')
        page = template.render(self.data)
        return page

    def show(self):
        with open(f'{self.path}/{self.template_folder}/page.html', 'w') as f:
            f.write(self.page)
        platform = os.uname().sysname
        command = {'Darwin': 'open', 'Linux': 'xdg-open'}
        os.system(f'{command[platform]} file://{self.path}/{self.template_folder}/page.html')
