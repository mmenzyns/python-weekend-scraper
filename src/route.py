from dataclasses import dataclass
from datetime import datetime


@dataclass
class RegioJetRoute:
    id: int
    departureStationId: int
    departureTime: str
    arrivalStationId: int
    arrivalTime: str
    vehicleTypes: list
    transfersCount: int
    freeSeatsCount: int
    priceFrom: float
    priceTo: float
    creditPriceFrom: float
    creditPriceTo: float
    pricesCount: int
    actionPrice: bool
    surcharge: bool
    notices: bool
    support: bool
    nationalTrip: bool
    bookable: bool
    delay: str
    travelTime: str
    vehicleStandardKey: str


@dataclass
class Route:
    origin: str
    destination: str
    departure: datetime
    arrival: datetime
    # Others not supported by frontend
    # carrier: str
    # vehicle_type: str
    # price: float
    # currency: str

    def __post_init__(self):
        if type(self.departure) is str:
            self.departure = datetime.fromisoformat(self.departure)
        if type(self.arrival) is str:
            self.arrival = datetime.fromisoformat(self.arrival)

    def get_dict(self) -> dict:
        d = self.__dict__
        d['departure'] = d['departure'].strftime("%d. %m. %Y %H:%M:%S")
        d['arrival'] = d['arrival'].strftime("%d. %m. %Y %H:%M:%S")
        return d