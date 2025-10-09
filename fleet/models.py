import pydantic


class Map(pydantic.BaseModel):
    tenant: str
    cars: list
    stops: list
    routes: list
