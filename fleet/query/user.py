from string import Template

from fleet.query.query import Query
from fleet.data.cookie import Cookie


class UserAdder(Query):
    def __init__(self, endpoint: str, login_cookie: Cookie,
                 email: str, username: str, password: str, role: str) -> None:
        super().__init__(endpoint, login_cookie)
        self.email = email
        self.username = username
        self.password = password
        self.role = role

    def get_query(self) -> str:
        return Template("""
              mutation M{
              UserMutation{add(user : {
                    email : "$email",
                    password : "$password",
                    roles: "$role",
                    userName: "$username"
                }){
                succeeded
                errors {description, code}
              }
              }
            }
        """).safe_substitute(
            {'email': self.email, 'username': self.username, 'password': self.password, 'role': self.role})

    def handle_json_response(self, json_response: dict) -> None:
        if not json_response["data"]["UserMutation"]["add"]["succeeded"]:
            print("-----PROBLEM-----")
            print(json_response)
            print("-----------------")


class UserDeleter(Query):
    def __init__(self, user: dict, endpoint: str, login_cookie: Cookie) -> None:
        super().__init__(endpoint, login_cookie)
        self.user = user

    def get_query(self) -> str:
        return Template("""
            mutation DeleteUser{
              UserMutation{
                delete(user: {email: "$email", userName: "$userName", roles: "$roles"}){
                  succeeded
                  errors {description}
                }
              }
            }
        """).safe_substitute({'email': self.user["email"], 'userName': self.user["userName"],
                              'roles': self.user["roles"]})

    def handle_json_response(self, json_response: dict) -> None:
        pass
