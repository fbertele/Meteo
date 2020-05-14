from get_info import *
from DjangoHelper import DjangoHelper
import argparse


def parser():
    p = argparse.ArgumentParser(
        description='Display aeronautical metereological Information')
    p.add_argument('location', nargs='*')
    p.add_argument('-sat', '--satellite', action='store_true')
    args = p.parse_args()
    args.location = ' '.join(args.location)
    return args


def main():
    coords, location = get_coord(args.location) if args.location else (45.467, 9.19)
    names_metar_taf = get_metar(coords)
    surface_links = [swc_ukmetoffice(), swc_dwd()]
    sigwx_links = sigwx_aviationweather()
    sat_data = sat_24() if args.satellite else None
    data = {'location': location,
            'coords': coords,
            'surface_links': surface_links,
            'sigwx_links': sigwx_links,
            'names_metar_taf': names_metar_taf,
            'sat_data': sat_data}
    page = DjangoHelper(data)
    page.show()


if __name__ == '__main__':
    args = parser()
    main()
