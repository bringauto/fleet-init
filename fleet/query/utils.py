from fleet.query.query import Query
from fleet.query.car import CarDeleter
from fleet.query.user import UserDeleter
from fleet.query.station import StationDeleter
from fleet.query.route import RouteDeleter
from fleet.data.cookie import Cookie


class AllIdGetter(Query):
    def get_query(self) -> str:
        return """
                query QQ{
                  CarQuery{
                    cars{
                      nodes{
                        id
                      }
                    }
                  }
                  StationQuery{
                    stations{
                      nodes{
                        id
                      }
                    }
                  }
                  OrderQuery{
                    orders{
                    nodes{
                      id
                    }
                   }
                  }
                  RouteQuery{
                        routes{
                          nodes{
                            id
                          }
                       }
                    }
                  UserQuery{
                    all{
                        nodes{
                            email
                            userName
                            roles
                        }
                    }
                  }

                }
            """

    def handle_json_response(self, json_response: dict) -> None:
        pass


def delete_all(endpoint: str, login_cookie: Cookie) -> None:
    """Orders are deleted automatically after all other things deleted (I hope...)"""
    all_ids_json = AllIdGetter(endpoint, login_cookie).exec()
    for car_node in all_ids_json["data"]["CarQuery"]["cars"]["nodes"]:
        CarDeleter(car_node["id"], endpoint, login_cookie).exec()
    for route_node in all_ids_json["data"]["RouteQuery"]["routes"]["nodes"]:
        RouteDeleter(route_node["id"], endpoint, login_cookie).exec()
    for station_node in all_ids_json["data"]["StationQuery"]["stations"]["nodes"]:
        StationDeleter(station_node["id"], endpoint, login_cookie).exec()
    for user_node in all_ids_json["data"]["UserQuery"]["all"]["nodes"]:
        UserDeleter(user_node, endpoint, login_cookie).exec()
