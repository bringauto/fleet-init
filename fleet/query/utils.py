import argparse
from os.path import isfile
from configparser import ConfigParser

from fleet_management_http_client_python import ( # type: ignore
    ApiClient,
    OrderApi,
    CarApi,
    PlatformHWApi,
    RouteApi,
    StopApi,
)


def delete_all(api_client: ApiClient) -> None:
    order_api = OrderApi(api_client)
    orders = order_api.get_orders()
    for order in orders:
        print(f"Deleting order {order.id}")
        try:
            order_api.delete_order(car_id=order.car_id, order_id=order.id)
        except Exception:
            print(f"Failed to delete order {order.id}, possibly belongs to a different tenant.")

    car_api = CarApi(api_client)
    cars = car_api.get_cars()
    for car in cars:
        print(f"Deleting car {car.id}, name: {car.name}")
        try:
            car_api.delete_car(car_id=car.id)
        except Exception:
            print(f"Failed to delete car {car.id}, possibly belongs to a different tenant.")

    platform_api = PlatformHWApi(api_client)
    platforms = platform_api.get_hws()
    for platform in platforms:
        print(f"Deleting platform {platform.id}, name: {platform.name}")
        try:
            platform_api.delete_hw(platform_hw_id=platform.id)
        except Exception:
            print(f"Failed to delete platform {platform.id}, possibly belongs to a different tenant.")

    route_api = RouteApi(api_client)
    routes = route_api.get_routes()
    for route in routes:
        print(f"Deleting route {route.id}, name: {route.name}")
        try:
            route_api.delete_route(route_id=route.id)
        except Exception:
            print(f"Failed to delete route {route.id}, possibly belongs to a different tenant.")

    stop_api = StopApi(api_client)
    stops = stop_api.get_stops()
    for stop in stops:
        print(f"Deleting stop {stop.id}, name: {stop.name}")
        try:
            stop_api.delete_stop(stop_id=stop.id)
        except Exception:
            print(f"Failed to delete stop {stop.id}, possibly belongs to a different tenant.")


def argument_parser_init() -> argparse.Namespace:
    """
    Initialize argument parser

    Return
    ------
    argparse.Namespace : object with atributes
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        help="Config file, default is config/config.ini",
        default="config/config.ini",
    )
    parser.add_argument(
        "-m",
        "--maps",
        type=str,
        help="Directory with input map config files, default is maps/",
        default="maps/",
    )
    parser.add_argument(
        "-d",
        "--delete",
        action="store_true",
        help="Delete all entities from database",
    )
    return parser.parse_args()


def config_parser_init(filename: str) -> ConfigParser:
    """
    Initialize config parser

    Parameters
    ----------
    filename : str
        Input config file

    Return
    ------
    ConfigParser : config parser
    """
    config = ConfigParser()
    config.read(filename)
    return config


def file_exists(filename: str) -> bool:
    """
    Check if file exists

    Parameters
    ----------
    filename : str
        File to check

    Return
    ------
    bool : True if exists otherwise False
    """
    return isfile(filename)
