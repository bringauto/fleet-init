import json
import requests
from abc import ABC, abstractmethod

from fleet.data.cookie import Cookie


class Query(ABC):
    """Parent class for queries that add entities to portal."""

    def __init__(self, endpoint: str, login_cookie: Cookie) -> None:
        self.endpoint = endpoint
        self.login_cookie = login_cookie

    def exec(self) -> dict:
        headers = {
            "Cookie": f"{self.login_cookie.get_key()}={self.login_cookie.get_value()}"}
        response = self.call_query(self.get_query(), headers, self.endpoint)
        if "errors" in response.json():
            raise Exception("Query problem: " + json.dumps(response.json()))
        # Portal sometimes responds with error (if adding user with short password etc.)
        self.handle_json_response(response.json())
        return response.json()

    @staticmethod
    def call_query(query: str, headers: dict, endpoint: str) -> requests.models.Response:
        response = requests.post(
            endpoint, json={"query": query}, headers=headers)
        if response.status_code == 200:
            return response
        else:
            raise Exception(f"Query failed {response.status_code}")

    @abstractmethod
    def get_query(self) -> str:
        """This is implemented in each child class - creates query for each case (adding Car, User, ...)"""
        pass

    @abstractmethod
    def handle_json_response(self, json_response: dict):
        """If user sends bad data in query to server, he will get error response, but responses differ, so has to be
        implemented for different cases"""
        pass
