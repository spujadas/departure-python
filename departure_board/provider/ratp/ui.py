from tabulate import tabulate


def list_lines(lines):
    table = []
    for line in sorted(lines, key=lambda k: k["code"]):
        table.append([line["id"],
            f"{line['reseau']} {line['code']}",
            line["name"]
        ])

    print(tabulate(table, headers=['id', 'code', 'nom']))


def list_directions(directions):
    for direction in directions.keys():
        print(f"{direction} -> {directions[direction]}")


def list_stations(stations, show_line: bool = False, show_station_id: bool = False):
    table = []

    for station in sorted(stations, key=lambda k: k["name"]):
        station_item = {"name": station["name"]}

        if show_line:
            station_item["line_id"] = station["line"]["id"]
            station_item[
                "line_name"
            ] = f"{station['line']['reseau']} {station['line']['code']}"

        if show_station_id:
            station_item["line_station_id"] = station["line_station_id"]

        table.append(station_item)

    print(tabulate(table, tablefmt="plain"))


def list_departures(departures):
    if departures["missions"]:
        print(tabulate(departures["missions"], tablefmt="plain"))
    if departures["perturbations"]:
        print(f"! {departures['perturbations']}")
