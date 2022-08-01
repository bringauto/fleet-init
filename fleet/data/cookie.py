

class Cookie:
    """Class to hold data for cookie (now just key-value, but later can be added more)"""

    def __init__(self, key: str, value: str) -> None:
        self.key = key
        self.value = value

    def get_key(self) -> str:
        return self.key

    def get_value(self) -> str:
        return self.value
