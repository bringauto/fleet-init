from string import Template

from .query import Query
from ..data.cookie import Cookie


LOGIN_USERNAME = "Admin"
LOGIN_PASSWORD = "Admin1"
COOKIE_KEY = ".AspNetCore.Identity.Application"
ENDPOINT = "http://localhost:8011/graphql"


def login_query(username: str, password: str) -> str:
    """Gets query to login into portal - is used to get cookie and than use it later"""
    text_template = Template("""
        query UserLogin {
            UserQuery {
        login(login: {password: "$password", userName: "$username"}) {
          email
          roles
        }
        }
    }
    """)
    return text_template.safe_substitute({'password': password, 'username': username})


def get_login_cookie(endpoint: str) -> Cookie:
    """Logins to portal, which will response with cookie and function extracts it and returns it"""
    headers = {}
    query = login_query(LOGIN_USERNAME, LOGIN_PASSWORD)
    response = Query.call_query(query, headers, endpoint)
    all_cookies = response.cookies.get_dict()
    login_cookie = Cookie(COOKIE_KEY, all_cookies[COOKIE_KEY])
    return login_cookie
