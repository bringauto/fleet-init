import pydantic


TenantName = str
CarName = str
RouteName = str


class Car(pydantic.BaseModel):
    name: CarName
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
    name: RouteName
    color: str
    stops: list[Station]


class Map(pydantic.BaseModel):
    tenant: TenantName
    cars: list[Car]
    stops: list[Stop]
    routes: list[Route]
