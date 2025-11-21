import re

from fleet_management_http_client_python import (  # type: ignore
    Stop,
    GNSSPosition,
    Route,
    RouteVisualization,
    PlatformHW,
    Car,
    MobilePhone,
    Tenant,
)
from fleet_management_http_client_python.exceptions import BadRequestException  # type: ignore
from fleet.query.client import ManagementApiClient
from fleet.models import Map, CarName, RouteName


def get_tenant_cookie(api_client: ManagementApiClient, tenant_name: str) -> str | None:
    try:
        response = api_client.get_tenants()
        tenant = next((t for t in response if t.name == tenant_name), None)
        if tenant is None:
            print(f"Tenant '{tenant_name}' does not exist, creating it")
            tenant = api_client.create_tenants([Tenant(name=tenant_name)])[0]
        return api_client.set_tenant_cookie_with_http_info(tenant.id)
    except Exception as exception:
        print(f"Could not create/set tenant '{tenant_name}' due to {exception}")
        return None


def _make_red(message: str) -> str:
    return f"\033[031m{message}\033[0m"


def _construct_duplicate_error_msg(
    api_client: ManagementApiClient,
    map_config: Map,
    exception: BadRequestException,
    entity_type: str,
) -> str:
    match = re.search(r"Key \(tenant_id, name\)=\((\d+), ([^)]+)\) already exists", str(exception))
    if match:
        tenant_id, name = match.groups()
        try:
            tenant_name = next(
                (t.name for t in api_client.get_tenants() if t.id == int(tenant_id)), ""
            )
        except Exception:
            tenant_name = ""
        tenant = "Tenant " + f"'{tenant_name}'" if tenant_name else f"with ID={tenant_id}"
        if tenant_name:
            assert (
                tenant_name == map_config.tenant
            ), f"Mismatched tenant names between the map config and the request to the API: '{tenant_name}' != '{map_config.tenant}'."
        return _make_red(
            f"[ERROR] {tenant} already has {entity_type.lower()} with name '{name}' created."
        )
    return ""


def _create_stops(api_client: ManagementApiClient, map_config: Map) -> list[Stop]:
    new_stops: list[Stop] = []
    for stop in map_config.stops:
        print(f"New stop, name: {stop.name}")
        new_stops.append(
            Stop(
                name=stop.name,
                position=GNSSPosition(latitude=stop.latitude, longitude=stop.longitude),
                notificationPhone=MobilePhone(phone=stop.contactPhone),
                isAutoStop=stop.isAutoStop,
            )
        )
    print("Sending create stops request")
    return api_client.create_stops(new_stops)


def _create_routes(
    api_client: ManagementApiClient, map_config: Map, stops: list[Stop]
) -> tuple[list[Route], dict[RouteName, list[GNSSPosition]]]:
    new_routes: list[Route] = []
    visualization_stops: dict[RouteName, list[GNSSPosition]] = {}
    for route in map_config.routes:
        stations = route.stops
        stop_ids: list[int] = []
        visualization_stops[route.name] = []
        for station in stations:
            visualization_stops[route.name].append(
                GNSSPosition(latitude=station.latitude, longitude=station.longitude)
            )
            if station.stationName is None:
                continue
            for created_stop in stops:
                if created_stop.name == station.stationName:
                    stop_ids.append(created_stop.id)
        print(f"New route, name: {route.name}")
        new_routes.append(Route(name=route.name, stopIds=stop_ids))
    print("Sending create routes request")
    return api_client.create_routes(new_routes), visualization_stops


def _create_route_visualizations(
    api_client: ManagementApiClient,
    map_config: Map,
    created_routes: list[Route],
    visualization_stops: dict[RouteName, list[GNSSPosition]],
) -> None:
    new_visualizations: list[RouteVisualization] = []
    for route in map_config.routes:
        for new_route in created_routes:
            if new_route.name == route.name:
                print(f"New route visualization for route {new_route.name}")
                new_visualizations.append(
                    RouteVisualization(
                        routeId=new_route.id,
                        hexcolor=route.color,
                        points=visualization_stops[route.name],
                    )
                )
                break
    print("Sending redefine route visualizations request")
    api_client.redefine_route_visualizations(new_visualizations)


def _create_platform_hws(
    api_client: ManagementApiClient, map_config: Map, already_added_cars: list[CarName]
) -> list[PlatformHW]:
    # Create platforms and cars
    new_platforms: list[PlatformHW] = []
    for platform in api_client.get_hws():
        if platform.name not in already_added_cars:
            already_added_cars.append(platform.name)
    return new_platforms


def _create_cars(
    api_client: ManagementApiClient,
    map_config: Map,
    already_added_cars: list[CarName],
    platforms: list[PlatformHW],
) -> None:
    new_cars: list[Car] = []
    for car in map_config.cars:
        if car.name in already_added_cars:
            print(f"Platform with name {car.name} is already created; skipping")
            continue
        print(f"New platform hw, name: {car.name}")
        platforms.append(PlatformHW(name=car.name))
    if len(platforms) > 0:
        print("Sending create platforms request")
        platforms = api_client.create_hws(platforms)

    for car in map_config.cars:
        if car.name in already_added_cars:
            print(f"Car with name {car.name} is already created; skipping")
            continue
        for platform in platforms:
            if platform.name == car.name:
                print(f"Creating car, name: {car.name}")
                new_cars.append(
                    Car(
                        platformHwId=platform.id,
                        name=car.name,
                        carAdminPhone=MobilePhone(phone=car.adminPhone),
                        underTest=car.underTest,
                    )
                )
                already_added_cars.append(car.name)
    if len(new_cars) > 0:
        print("Sending create cars request")
        api_client.create_cars(new_cars)


def run_queries(
    api_client: ManagementApiClient, map_config: Map, already_added_cars: list[CarName]
) -> None:

    try:
        entity_type = "stop"
        stops = _create_stops(api_client, map_config)

        entity_type = "route"
        routes, visualization_stops = _create_routes(api_client, map_config, stops)

        entity_type = "route visualization"
        _create_route_visualizations(api_client, map_config, routes, visualization_stops)

        entity_type = "platform HW"
        platforms = _create_platform_hws(api_client, map_config, already_added_cars)

        entity_type = "car"
        _create_cars(api_client, map_config, already_added_cars, platforms)

    except BadRequestException as e:
        msg = _construct_duplicate_error_msg(api_client, map_config, e, entity_type)
        print(msg or e)
        return
