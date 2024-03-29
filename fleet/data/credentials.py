

class Credentials:

    __slots__ = ('username', 'password', 'endpoint')

    def __init__(self, username: str, password: str, url: str) -> None:
        self.username = username
        self.password = password
        self.endpoint = f'{url}/graphql'
