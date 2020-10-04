import departure.helpers as helpers


def list_stations(stations):
    for station in sorted(stations.items(), key=lambda k: k[1]):
        print(f"{station[0]:6} {station[1]}")


def list_services(services):
    for i, service in enumerate(services):
        print(
            f"{helpers.ordinal_en(i + 1)} {service['std']} {service['platform']} "
            f"{service['destination_location_name']} "
            f"(from {service['origin_location_name']}) - {service['etd']}"
        )
        calling_points = [
            f"{cp['location_name']} ({cp['st']} / {cp['et']})"
            for cp in service['calling_points']
        ]
        if i == 0:
            print(f"  Calling at: {', '.join(calling_points)} ({service['operator']})")
