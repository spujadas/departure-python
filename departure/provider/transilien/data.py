import pathlib
import json


DATA_DIRNAME = "data"
IDF_DATA_FILENAME = "sncf-gares-et-arrets-transilien-ile-de-france.json"
FRANCE_DATA_FILENAME = "referentiel-gares-voyageurs.json"


def _stations(data_dirname, idf_data_filename):
    data_path = pathlib.Path(__file__).parents[0] / data_dirname / idf_data_filename

    # read from stations data file
    with open(data_path) as data_file:
        raw_stations = json.load(data_file)

    stations = {}

    for raw_station in raw_stations:
        station_id = raw_station["fields"]["code_uic"]
        station_data = {
            "nom": raw_station["fields"]["nom_gare"],
            "libelle": raw_station["fields"]["libelle"],
        }
        stations[station_id] = station_data

    return stations


def _stations_france(data_dirname, france_data_filename):
    data_path = pathlib.Path(__file__).parents[0] / data_dirname / france_data_filename

    # read from stations data file
    with open(data_path) as data_file:
        raw_stations_france = json.load(data_file)

    stations_france = {}

    for raw_station in raw_stations_france:
        station_id = str(raw_station["fields"]["pltf_uic_code"])
        station_data = {"nom": raw_station["fields"]["gare_alias_libelle_noncontraint"]}
        stations_france[station_id] = station_data

    return stations_france


STATIONS = _stations(DATA_DIRNAME, IDF_DATA_FILENAME)
STATIONS_FRANCE = _stations_france(DATA_DIRNAME, FRANCE_DATA_FILENAME)
