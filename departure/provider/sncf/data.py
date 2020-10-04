import pathlib
import json


DATA_DIRNAME = "data"
DATA_FILENAME = "referentiel-gares-voyageurs.json"


def _stations(data_dirname, data_filename):
    data_path = pathlib.Path(__file__).parents[0] / data_dirname / data_filename

    # read from stations data file
    with open(data_path) as data_file:
        raw_stations = json.load(data_file)

    stations = {}

    for raw_station in raw_stations:
        station_id = str(raw_station["fields"]["pltf_uic_code"])
        station_data = {"nom": raw_station["fields"]["gare_alias_libelle_noncontraint"]}
        stations[station_id] = station_data

    return stations


STATIONS = _stations(DATA_DIRNAME, DATA_FILENAME)
