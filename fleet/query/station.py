from string import Template

from fleet.query.query import Query
from fleet.data.cookie import Cookie


class StationAdder(Query):
    def __init__(self, endpoint: str, login_cookie: Cookie, name: str,
                 latitude: float, longitude: float, contact_phone: str) -> None:
        super().__init__(endpoint, login_cookie)
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.contact_phone = contact_phone

    def get_query(self):
        return Template("""
                mutation Q{
                  StationMutation{addStation(station: {name: "$name", latitude: $latitude, longitude: $longitude,
                                contactPhone: "$contactPhone"}){
                    id
                  }
                  }
                }
            """).safe_substitute({'name': self.name, 'latitude': self.latitude, 'longitude': self.longitude,
                                  'contactPhone': self.contact_phone})

    def handle_json_response(self, json_response):
        pass


class StationInfoGetter(Query):
    """Call parent exec() function and then pass result to function get_id_from_json() to get id"""

    def __init__(self, endpoint: str, login_cookie: Cookie, station_name: str) -> None:
        super().__init__(endpoint, login_cookie)
        self.station_name = station_name

    def get_query(self) -> str:
        return Template("""
            query Q{
              StationQuery{
                stations(where: {name:"$name"}){
                  nodes{id name}
                }
              }
            }
        """).safe_substitute({'name': self.station_name})

    def handle_json_response(self, json_response: dict) -> None:
        pass

    def get_id_from_json(self, json_response: dict) -> int:
        """Extracts id from json response"""
        stations = json_response["data"]["StationQuery"]["stations"]["nodes"]
        if len(stations) == 0:
            raise Exception(
                f"Station with name {self.station_name} doesn't exists!")
        if len(stations) > 1:
            raise Exception(
                f"There is more ({len(stations)}) stations with name {self.station_name}!")
        return stations[0]["id"]


class StationDeleter(Query):
    def __init__(self, station_id: int, endpoint: str, login_cookie: Cookie) -> None:
        super().__init__(endpoint, login_cookie)
        self.station_id = station_id

    def get_query(self) -> str:
        return Template("""
            mutation DeleteStation{
              StationMutation{
                deleteStation(stationId: $stationId){
                  id
                }
              }
            }
        """).safe_substitute({'stationId': self.station_id})

    def handle_json_response(self, json_response: dict) -> None:
        pass
