from string import Template

from fleet.query.query import Query
from fleet.query.car import CarInfoGetter
from fleet.query.station import StationInfoGetter
from fleet.data.cookie import Cookie


class OrderAdder(Query):
    """We can't set id of cars and stations, so in config file, we have to connect order to car by name and
    then here in constructor find id associated to it"""

    def __init__(self, endpoint: str, login_cookie: Cookie, car_name: str, from_station_name, to_station_name, priority,
                 arrive, from_station_phone, to_station_phone) -> None:
        super().__init__(endpoint, login_cookie)
        self.car_name = car_name
        self.from_station_name = from_station_name
        self.to_station_name = to_station_name
        self.priority = priority
        self.arrive = arrive
        self.from_station_phone = from_station_phone
        self.to_station_phone = to_station_phone

        car_info_getter = CarInfoGetter(
            self.endpoint, self.login_cookie, car_name)
        self.car_id = car_info_getter.get_id_from_json(car_info_getter.exec())

        station_from_info_getter = StationInfoGetter(
            self.endpoint, self.login_cookie, from_station_name)
        self.from_station_id = station_from_info_getter.get_id_from_json(
            station_from_info_getter.exec())

        station_to_info_getter = StationInfoGetter(
            self.endpoint, self.login_cookie, to_station_name)
        self.to_station_id = station_to_info_getter.get_id_from_json(
            station_to_info_getter.exec())

    def get_query(self) -> str:
        return Template("""
            mutation M{
              OrderMutation{
                addOrder(order:{arrive : "$arrive",
                         carId: $carId,
                         priority: $priority,
                         fromStationId: $fromStationId,
                         toStationId: $toStationId,
                         toStationPhone: "$toStationPhone",
                         fromStationPhone: "$fromStationPhone"})
                {
                id
              }
              }
            }
        """).safe_substitute({'arrive': self.arrive, 'carId': self.car_id, 'priority': self.priority,
                              'fromStationId': self.from_station_id, 'toStationId': self.to_station_id,
                              'toStationPhone': self.to_station_phone,
                              'fromStationPhone': self.from_station_phone})

    def handle_json_response(self, json_response: dict) -> None:
        pass
