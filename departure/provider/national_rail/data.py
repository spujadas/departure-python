import pathlib
import csv


STATION_CODES_FILENAME = "data/station_codes.csv"


def _stations(station_codes_filename):
    station_codes_path = pathlib.Path(__file__).parents[0] / station_codes_filename

    # read from stations data file if available
    with station_codes_path.open() as stations_codes_file:
        reader = csv.reader(stations_codes_file)
        next(reader, None)  # skip header row
        stations = {}
        for row in reader:
            stations[row[1]] = row[0]

    return stations


STATIONS = _stations(STATION_CODES_FILENAME)
