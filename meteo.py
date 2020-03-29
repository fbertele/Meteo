from get_info import *
from DjangoHelper import DjangoHelper
import sys


def main():
    coords = get_coord(sys.argv[1]) if len(sys.argv) > 1 else (53.079, 8.801)
    names_metar_taf = get_metar(coords)
    surface_links = [swc_ukmetoffice(), swc_dwd()]
    sigwx_links = sigwx_aviationweather()
    sat_links = sat_aviationweather()
    data = {'coords': coords,
            'surface_links': surface_links,
            'sigwx_links': sigwx_links,
            'names_metar_taf': names_metar_taf,
            'sat_links': sat_links}
    page = DjangoHelper(data)
    page.show()


if __name__ == '__main__':
    main()
