from string import Template

from fleet.query.query import Query
from fleet.query.station import StationInfoGetter
from fleet.data.cookie import Cookie


class RouteAdder(Query):
    def __init__(self, endpoint: str, login_cookie: Cookie, name: str, color: str, stops: list) -> None:
        super().__init__(endpoint, login_cookie)
        self.name = name
        self.color = color
        self.stops = stops

    def get_query(self) -> str:
        stops_query_part = ""
        for i, stop in enumerate(self.stops):  # creates string of stops in GraphQL format. Example:
            # {latitude: 2.68, longitude: 5.3, $order: 1}, ...
            station_query_part = "station: null"
            if stop.station_name is not None:
                station_info = StationInfoGetter(
                    self.endpoint, self.login_cookie, stop.station_name)
                station_id = station_info.get_id_from_json(station_info.exec())
                station_query_part = Template("station: { id: $station_id }").safe_substitute({
                    'station_id': station_id})
            stops_query_part += Template("""{
                latitude: $latitude,
                longitude: $longitude,
                order: $order,
                $station_query_part
            }""").safe_substitute(
                {'latitude': stop.latitude, 'longitude': stop.longitude, 'order': stop.order,
                 'station_query_part': station_query_part}
            )
            if i < (len(self.stops) - 1):
                stops_query_part += ","  # comma between except last stop
        return Template("""
                    mutation M{
                      RouteMutation{addRoute(route : {name: "$name", color: "$color", stops: [
                        $stops
                      ]}){
                        id
                      }
                      }
                    }
            """).safe_substitute({'name': self.name, 'color': self.color, 'stops': stops_query_part})

    def handle_json_response(self, json_response: dict) -> None:
        pass


class RoutesInfoGetter(Query):
    def __init__(self, endpoint: str, login_cookie: Cookie) -> None:
        super().__init__(endpoint, login_cookie)

    def get_query(self) -> str:
        return """
                query QQ{
                  RouteQuery{
                        routes{
                          nodes{
                            id
                          }
                       }
                    }
                }
            """

    def handle_json_response(self, json_response: dict) -> None:
        pass


class RouteDeleter(Query):
    def __init__(self, route_id: int, endpoint: str, login_cookie: Cookie) -> None:
        super().__init__(endpoint, login_cookie)
        self.route_id = route_id

    def get_query(self) -> str:
        return Template("""
            mutation DeleteRoute{
              RouteMutation{
                deleteRoute(routeId: $routeId){
                  id
                }
              }
            }
        """).safe_substitute({'routeId': self.route_id})

    def handle_json_response(self, json_response: dict) -> None:
        pass
