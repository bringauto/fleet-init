

class Stop:
    """Holds info about stop"""

    def __init__(self, latitude, longitude, order, station_name: str):
        self.latitude = latitude
        self.longitude = longitude
        self.order = order
        self.station_name = station_name
