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


def run_queries(
    api_client: ManagementApiClient, map_config: Map, already_added_cars: list[CarName]
) -> None:

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
    created_stops = api_client.create_stops(new_stops)

    new_routes: list[Route] = []
    new_visualizations: list[RouteVisualization] = []
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
            for created_stop in created_stops:
                if created_stop.name == station.stationName:
                    stop_ids.append(created_stop.id)
        print(f"New route, name: {route.name}")
        new_routes.append(Route(name=route.name, stopIds=stop_ids))
    print("Sending create routes request")
    created_routes = api_client.create_routes(new_routes)

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

    new_platforms: list[PlatformHW] = []
    new_cars: list[Car] = []
    for platform in api_client.get_hws():
        if platform.name not in already_added_cars:
            already_added_cars.append(platform.name)
    for car in map_config.cars:
        if car.name in already_added_cars:
            print(f"Platform with name {car.name} is already created; skipping")
            continue
        print(f"New platform hw, name: {car.name}")
        new_platforms.append(PlatformHW(name=car.name))
    if len(new_platforms) > 0:
        print("Sending create platforms request")
        created_platforms = api_client.create_hws(new_platforms)

    for car in map_config.cars:
        if car.name in already_added_cars:
            print(f"Car with name {car.name} is already created; skipping")
            continue
        for new_platform in created_platforms:
            if new_platform.name == car.name:
                print(f"Creating car, name: {car.name}")
                new_cars.append(
                    Car(
                        platformHwId=new_platform.id,
                        name=car.name,
                        carAdminPhone=MobilePhone(phone=car.adminPhone),
                        underTest=car.underTest,
                    )
                )
                already_added_cars.append(car.name)
    if len(new_cars) > 0:
        print("Sending create cars request")
        api_client.create_cars(new_cars)
