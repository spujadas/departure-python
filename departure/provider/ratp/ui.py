from tabulate import tabulate


def list_lines(lines):
    table = []
    for line in sorted(lines, key=lambda k: k["code"]):
        table.append([line["id"], f"{line['reseau']} {line['code']}", line["name"]])

    print(tabulate(table, headers=["id", "code", "nom"]))


def list_directions(directions):
    print(
        tabulate(
            [[direction, directions[direction]] for direction in directions.keys()],
            headers=["code", "direction"],
        )
    )


def list_stations(stations, show_line: bool = False, show_station_id: bool = False):
    table = []

    # populate table
    for station in sorted(stations, key=lambda k: k["name"]):
        station_item = []

        if show_line:
            station_item.append(station["line"]["id"])
            station_item.append(
                f"{station['line']['reseau']} {station['line']['code']}"
            )

        if show_station_id:
            station_item.append(station["line_station_id"])

        station_item.append(station["name"])

        table.append(station_item)

    # set table headers
    headers = []
    if show_line:
        headers.extend(["line id", "line code"])
    if show_station_id:
        headers.append("line station id")
    headers.append("station name")

    # display table
    print(tabulate(table, headers))


def list_departures(departures):
    if departures["missions"]:
        print(tabulate(departures["missions"], tablefmt="plain"))
    if departures["perturbations"]:
        print(f"! {departures['perturbations']}")
