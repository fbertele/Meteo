from get_info import *
from DjangoHelper import DjangoHelper
import sys


def main():
    coords = mapquest(sys.argv[1]) if len(sys.argv) > 1 else (53.079, 8.801)
    metar = get_metar(coords)
    surface_links = [chartmetuk(), chartsdwd()]
    sigwx_links = aviationweather()
    data = {'coords': coords,
            'surface_links': surface_links,
            'sigwx_links': sigwx_links,
            'metar': metar}
    page = DjangoHelper(data)
    page.show()


if __name__ == '__main__':
    main()
