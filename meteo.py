from get_info import *
from DjangoHelper import DjangoHelper
import sys


def main():
    location = mapquest(sys.argv[1]) if len(sys.argv) > 1 else ('53.079', '8.801')
    surface_links = [chartmetuk(), chartsdwd()]
    sigwx_links = aviationweather()
    data = {'location': location,
            'surface_links': surface_links,
            'sigwx_links': sigwx_links}
    DjangoHelper(data).show()


if __name__ == '__main__':
    main()
