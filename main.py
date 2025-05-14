#!/usr/bin/env python3

import glob
import json
import os

from fleet import argument_parser_init, config_parser_init, delete_all, file_exists
from fleet_management_http_client_python import (
    ApiClient,
    Configuration,
    StopApi,
    Stop,
    GNSSPosition,
    RouteApi,
    Route,
    RouteVisualization,
    PlatformHWApi,
    PlatformHW,
    CarApi,
    Car,
    MobilePhone,
    TenantApi,
    Tenant,
)
from fleet_management_http_client_python.exceptions import (
    BadRequestException as _BadRequestException,
)


CarName = str
RouteName = str


def run_queries(
    api_client: ApiClient, map_config_path: str, already_added_cars: list[CarName]
) -> None:
    with open(map_config_path, "r", encoding="utf-8") as map_file:
        map_config = json.load(map_file)
    stop_api = StopApi(api_client)
    new_stops = list()

    tenant_name = map_config["tenant"]
    tenant_created = create_tenant(api_client, tenant_name)
    if not tenant_created:
        print(
            f"Tenant '{tenant_name}' could not be created. Cannot create entities for map '{map_config_path}'"
        )
        return
    api_client.set_default_header("Cookie", "tenant=" + tenant_name)
    for stop in map_config["stops"]:
        print(f"New stop, name: {stop['name']}")
        new_stops.append(
            Stop(
                name=stop["name"],
                position=GNSSPosition(latitude=stop["latitude"], longitude=stop["longitude"]),
                notificationPhone=MobilePhone(phone=stop["contactPhone"]),
                isAutoStop=stop["isAutoStop"] if "isAutoStop" in stop else False,
            )
        )
    print("Sending create stops request")
    created_stops = stop_api.create_stops(new_stops)

    route_api = RouteApi(api_client)
    new_routes: list[Route] = list()
    new_visualizations: list[RouteVisualization] = list()
    visualization_stops: dict[RouteName, list[GNSSPosition]] = dict()
    for route in map_config["routes"]:
        stops = route["stops"]
        stop_ids: list[int] = list()
        visualization_stops[route["name"]] = list()
        for stop in stops:
            visualization_stops[route["name"]].append(
                GNSSPosition(latitude=stop["latitude"], longitude=stop["longitude"])
            )
            if stop["stationName"] == None:
                continue
            for created_stop in created_stops:
                if created_stop.name == stop["stationName"]:
                    stop_ids.append(created_stop.id)
        print(f"New route, name: {route['name']}")
        new_routes.append(Route(name=route["name"], stopIds=stop_ids))
    print("Sending create routes request")
    created_routes = route_api.create_routes(new_routes)

    for route in map_config["routes"]:
        for new_route in created_routes:
            if new_route.name == route["name"]:
                print(f"New route visualization for route {new_route.name}")
                new_visualizations.append(
                    RouteVisualization(
                        routeId=new_route.id,
                        hexcolor=route["color"],
                        points=visualization_stops[route["name"]],
                    )
                )
                break
    print("Sending redefine route visualizations request")
    route_api.redefine_route_visualizations(new_visualizations)

    platform_api = PlatformHWApi(api_client)
    car_api = CarApi(api_client)
    new_platforms = list()
    new_cars = list()
    for platform in platform_api.get_hws():
        if platform.name not in already_added_cars:
            already_added_cars.append(platform.name)
    for car in map_config["cars"]:
        if car["name"] in already_added_cars:
            print(f"Platform with name {car['name']} is already created; skipping")
            continue
        print(f"New platform hw, name: {car['name']}")
        new_platforms.append(PlatformHW(name=car["name"]))
    if len(new_platforms) > 0:
        print("Sending create platforms request")
        created_platforms = platform_api.create_hws(new_platforms)

    for car in map_config["cars"]:
        if car["name"] in already_added_cars:
            print(f"Car with name {car['name']} is already created; skipping")
            continue
        for new_platform in created_platforms:
            if new_platform.name == car["name"]:
                print(f"Creating car, name: {car['name']}")
                new_cars.append(
                    Car(
                        platformHwId=new_platform.id,
                        name=car["name"],
                        carAdminPhone=MobilePhone(phone=car["adminPhone"]),
                        underTest=car["underTest"],
                    )
                )
                already_added_cars.append(car["name"])
    if len(new_cars) > 0:
        print("Sending create cars request")
        car_api.create_cars(new_cars)


def create_tenant(api_client: ApiClient, tenant_name: str) -> bool:
    tenant_api = TenantApi(api_client)
    try:
        tenant_api.create_tenants([Tenant(name=tenant_name)])
        return True
    except _BadRequestException as e:
        response = tenant_api.get_tenants()
        tenant_already_exists = any(t.name == tenant_name for t in response)
        if not tenant_already_exists:
            print(f"Tenant '{tenant_name}' already exists.")
        else:
            print(f"Tenant '{tenant_name}' does not exists and could not be created. Error: {e}")
        return tenant_already_exists
    except Exception as exception:
        print(f"Could not create tenant '{tenant_name}' due to {exception}")
        return False


def main() -> None:
    args = argument_parser_init()
    if not file_exists(args.config):
        raise IOError(f"Input config file does not exist: {args.config}")
    config = config_parser_init(args.config)
    api_client = ApiClient(
        Configuration(
            host=config["DEFAULT"]["Url"], api_key={"APIKeyAuth": config["DEFAULT"]["ApiKey"]}
        )
    )
    args.maps = os.path.join(args.maps, "")
    if args.delete:
        delete_all(api_client)
        print("Fleet management deleted")
    already_added_cars: list[CarName] = list()
    for map_file_path in glob.iglob(f"{args.maps}*"):
        print(f"\nProcessing file: {map_file_path}")
        try:
            run_queries(api_client, map_file_path, already_added_cars)
        except Exception as exception:
            print(exception)
            return
    print("\nFleet management updated")


if __name__ == "__main__":
    main()
