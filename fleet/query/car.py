from string import Template

from fleet.query.query import Query
from fleet.query.route import RoutesInfoGetter
from fleet.data.cookie import Cookie


class CarAdder(Query):
    def __init__(self, endpoint: str, login_cookie: Cookie, name: str, hw_id: str, comapanyName: str,
                 carAdminPhone: str, underTest: bool) -> None:
        super().__init__(endpoint, login_cookie)
        self.name = name
        self.hw_id = hw_id
        self.companyName = comapanyName
        self.adminPhone = carAdminPhone
        self.underTest = underTest

    def get_query(self) -> str:
        routes = RoutesInfoGetter(
            self.endpoint, self.login_cookie).exec()
        routeId = routes["data"]["RouteQuery"]["routes"]["nodes"][0]["id"]
        return Template("""
            mutation M{
              CarMutation{
              addCar(car : {name : "$name", hwId : "$hwId", companyName: "$companyName",
                underTest: true, carAdminPhone: "$adminPhone", routeId: $routeId
               }){
                id
                name
                token
                companyName
                carAdminPhone
                routeId
              }
              }
            }
        """).safe_substitute({'name': self.name, 'hwId': self.hw_id, 'companyName': self.companyName,
                              'underTest': self.underTest, 'adminPhone': self.adminPhone, 'routeId': routeId})

    def handle_json_response(self, json_response: dict) -> None:
        # Car adding does not return any errors, always success even if car already exists
        pass


class CarInfoGetter(Query):
    """Call parent exec() function and then pass result to function get_id_from_json() to get id"""

    def __init__(self, endpoint: str, login_cookie: Cookie, car_name: str) -> None:
        super().__init__(endpoint, login_cookie)
        self.car_name = car_name

    def get_query(self) -> str:
        return Template("""
            query Q{
              CarQuery{
                cars(where: {name: "$name"}){
                  nodes{
                    id
                    name
                  }
                }
              }
        }
        """).safe_substitute({'name': self.car_name})

    def handle_json_response(self, json_response: dict) -> None:
        pass

    def get_id_from_json(self, json_response: dict) -> int:
        """Extracts id from json response"""
        cars = json_response["data"]["CarQuery"]["cars"]["nodes"]
        if len(cars) == 0:
            raise Exception(f"Car with name {self.car_name} doesn't exists!")
        if len(cars) > 1:
            raise Exception(
                f"There is more ({len(cars)}) cars with name {self.car_name}!")
        return cars[0]["id"]


class CarDeleter(Query):
    def __init__(self, car_id: int, endpoint: str, login_cookie: Cookie) -> None:
        super().__init__(endpoint, login_cookie)
        self.car_id = car_id

    def get_query(self) -> str:
        return Template("""
            mutation DeleteCar{
              CarMutation{
                deleteCar(carId: $carId){
                  id
                }
              }
            }
        """).safe_substitute({'carId': self.car_id})

    def handle_json_response(self, json_response: dict) -> None:
        pass
