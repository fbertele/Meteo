from get_info import *
from DjangoHelper import DjangoHelper
import sys


def main():
    coords = mapquest(sys.argv[1]) if len(sys.argv) > 1 else (53.079, 8.801)
    icao_codes, names = airports_codes(coords)
    metar_data = [get_metar(code) for code in icao_codes]
    metars = zip(names, metar_data)
    surface_links = [chartmetuk(), chartsdwd()]
    sigwx_links = aviationweather()
    data = {'coords': coords,
            'surface_links': surface_links,
            'sigwx_links': sigwx_links,
            'metars': metars}
    DjangoHelper(data).show()


if __name__ == '__main__':
    main()
