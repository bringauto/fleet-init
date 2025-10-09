from fleet_management_http_client_python import (  # type: ignore
    Configuration,
    ApiClient,
    StopApi,
    Stop,
    OrderApi,
    Order,
    RouteApi,
    Route,
    RouteVisualization,
    PlatformHWApi,
    PlatformHW,
    CarApi,
    Car,
    TenantApi,
    Tenant,
)


class ManagementApiClient:
    """Wrapper for HTTP Client for simpler usage and testability"""

    def __init__(self, host: str, api_key: dict[str, str]) -> None:
        configuration = Configuration(host=host, api_key=api_key)
        api_client = ApiClient(configuration)
        self.api_client = api_client
        self.stop_api = StopApi(api_client)
        self.route_api = RouteApi(api_client)
        self.platform_api = PlatformHWApi(api_client)
        self.car_api = CarApi(api_client)
        self.tenant_api = TenantApi(api_client)
        self.order_api = OrderApi(api_client)

    def create_stops(self, stops: list[Stop]) -> list[Stop]:
        return self.stop_api.create_stops(stops)

    def create_routes(self, routes: list[Route]) -> list[Route]:
        return self.route_api.create_routes(routes)

    def get_routes(self) -> list[Route]:
        return self.route_api.get_routes()

    def delete_route(self, route_id: int) -> None:
        self.route_api.delete_route(route_id=route_id)

    def get_stops(self) -> list[Stop]:
        return self.stop_api.get_stops()

    def delete_stop(self, stop_id: int) -> None:
        self.stop_api.delete_stop(stop_id=stop_id)

    def redefine_route_visualizations(self, visualizations: list[RouteVisualization]) -> None:
        self.route_api.redefine_route_visualizations(visualizations)

    def get_platforms(self) -> list[PlatformHW]:
        return self.platform_api.get_hws()

    def get_orders(self) -> list[Order]:
        return self.order_api.get_orders()

    def delete_order(self, car_id: int, order_id: int) -> None:
        self.order_api.delete_order(car_id=car_id, order_id=order_id)

    def create_hws(self, platforms: list[PlatformHW]) -> list[PlatformHW]:
        return self.platform_api.create_hws(platforms)

    def delete_hw(self, platform_hw_id: int) -> None:
        self.platform_api.delete_hw(platform_hw_id=platform_hw_id)

    def create_cars(self, cars: list[Car]) -> list[Car]:
        return self.car_api.create_cars(cars)

    def delete_car(self, car_id: int) -> None:
        self.car_api.delete_car(car_id=car_id)

    def get_tenants(self) -> list[Tenant]:
        return self.tenant_api.get_tenants()

    def create_tenants(self, tenants: list[Tenant]) -> list[Tenant]:
        return self.tenant_api.create_tenants(tenants)

    def delete_tenant(self, tenant_id: int) -> None:
        self.tenant_api.delete_tenant(tenant_id)

    def set_tenant_cookie_with_http_info(self, tenant_id: int) -> str | None:
        try:
            cookie_response = self.tenant_api.set_tenant_cookie_with_http_info(tenant_id)
            return cookie_response.headers.get("Set-Cookie")
        except Exception as exception:
            print(f"Could not set tenant cookie due to {exception}")
            return None

    def get_cars(self) -> list[Car]:
        return self.car_api.get_cars()

    def get_hws(self) -> list[PlatformHW]:
        return self.platform_api.get_hws()

    def set_default_header(self, header_name: str, header_value: str) -> None:
        self.api_client.set_default_header(header_name, header_value)
