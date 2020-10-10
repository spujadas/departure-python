import pathlib
import csv


DATA_DIRNAME = "data"
DATA_FILENAME = "stations-2020-01-nl.csv"


def _stations_by_ns_code(data_dirname, data_filename):
    data_path = pathlib.Path(__file__).parents[0] / data_dirname / data_filename

    # read from stations data file
    with open(data_path, encoding="utf8") as data_file:
        # fields: id, code, uic, name_short, name_medium, name_long, slug, country,
        # type, geo_lat, geo_lng
        data_reader = csv.DictReader(data_file, delimiter=",")

        stations = {}

        for station in data_reader:
            stations[station["code"]] = {
                "uic": station["uic"],
                "name_medium": station["name_medium"],
                "name_long": station["name_long"],
            }

    return stations


def _stations_by_uic(stations_by_ns_code_dict):
    stations = {}
    for ns_code in stations_by_ns_code_dict:
        stations[stations_by_ns_code_dict[ns_code]["uic"]] = {
            "ns_code": ns_code,
            "name_medium": stations_by_ns_code_dict[ns_code]["name_medium"],
            "name_long": stations_by_ns_code_dict[ns_code]["name_long"],
        }

    return stations


STATIONS_BY_NS_CODE = _stations_by_ns_code(DATA_DIRNAME, DATA_FILENAME)
STATIONS_BY_UIC = _stations_by_uic(STATIONS_BY_NS_CODE)
