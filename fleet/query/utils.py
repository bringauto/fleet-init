import argparse
import os

from configparser import ConfigParser
import pydantic

from fleet.query.client import ManagementApiClient
from fleet.models import Map


class ScriptArgs(pydantic.BaseModel):
    config: str
    maps: str
    delete: bool
    test: bool


def load_map_config(map_config_path: str) -> Map:
    """Load map configuration from given file path. It is assumed that the file exists."""
    with open(map_config_path, "r", encoding="utf-8") as map_file:
        map_config = map_file.read()
    map_config_obj = Map.model_validate_json(map_config)
    return map_config_obj


def delete_all(api_client: ManagementApiClient) -> None:
    """Delete all existing entities (cars, routes, ...) from the database."""
    orders = api_client.get_orders()
    for order in orders:
        print(f"Deleting order {order.id}")
        try:
            api_client.delete_order(car_id=order.car_id, order_id=order.id)
        except Exception:
            print(f"Failed to delete order {order.id}, possibly belongs to a different tenant.")

    cars = api_client.get_cars()
    for car in cars:
        print(f"Deleting car {car.id}, name: {car.name}")
        try:
            api_client.delete_car(car_id=car.id)
        except Exception:
            print(f"Failed to delete car {car.id}, possibly belongs to a different tenant.")

    platforms = api_client.get_hws()
    for platform in platforms:
        print(f"Deleting platform {platform.id}, name: {platform.name}")
        try:
            api_client.delete_hw(platform_hw_id=platform.id)
        except Exception:
            print(
                f"Failed to delete platform {platform.id}, possibly belongs to a different tenant."
            )

    routes = api_client.get_routes()
    for route in routes:
        print(f"Deleting route {route.id}, name: {route.name}")
        try:
            api_client.delete_route(route_id=route.id)
        except Exception:
            print(f"Failed to delete route {route.id}, possibly belongs to a different tenant.")

    stops = api_client.get_stops()
    for stop in stops:
        print(f"Deleting stop {stop.id}, name: {stop.name}")
        try:
            api_client.delete_stop(stop_id=stop.id)
        except Exception:
            print(f"Failed to delete stop {stop.id}, possibly belongs to a different tenant.")


def load_script_args() -> ScriptArgs:
    """
    Load script arguments from command line and validate config file path and map directory path.

    If either path is invalid, raise FileNotFoundError.
    """

    args = ScriptArgs(**_argument_parser_init())
    if not os.path.isfile(args.config):
        raise FileNotFoundError(f"Config file '{args.config}' does not exist.")
    if not os.path.isdir(args.maps):
        raise FileNotFoundError(f"Nonexistent map directory: '{args.maps}'.")
    return args


def _argument_parser_init() -> dict:
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
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="Run in test mode (no requests to the server)",
    )
    return parser.parse_args().__dict__


def config_parser_init(filename: str) -> ConfigParser:
    """Initialize and return ConfigParser object from given filename to be used in the script."""
    config = ConfigParser()
    config.read(filename)
    return config
