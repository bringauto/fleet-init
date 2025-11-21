import pydantic


class Car(pydantic.BaseModel):
    name: str
    hwId: str
    adminPhone: str
    underTest: bool


class Stop(pydantic.BaseModel):
    name: str
    latitude: float
    longitude: float
    contactPhone: str
    isAutoStop: bool = False


class Station(pydantic.BaseModel):
    latitude: float
    longitude: float
    stationName: str | None


class Route(pydantic.BaseModel):
    name: str
    color: str
    stops: list[Station]


class Map(pydantic.BaseModel):
    tenant: str
    cars: list[Car]
    stops: list[Stop]
    routes: list[Route]
