from dataclasses import dataclass

@dataclass
class Station:
    id: int
    name: str
    fullname: str
    aliases: list
    address: str
    stationsTypes: list
    iataCode: str
    stationUrl: str
    stationTimeZoneCode: str
    wheelChairPlatform: str
    significance: int
    longitude: float
    latitude: float
    imageUrl: str

@dataclass
class City:
    id: int
    name: str
    stations: list[Station]
    aliases: list[str]
    stationsTypes: list

    def __post_init__(self):
        self.stations = [Station(**station) for station in self.stations]


@dataclass
class Country:
    country: str
    code: str
    cities: list[City]

    def __post_init__(self):
        self.cities = [City(**city) for city in self.cities]


@dataclass
class Locations:
    list: list[Country]

    def from_json(json) -> list[Country]:
        return Locations([Country(**location) for location in json])

    def get_city_code(self, name: str) -> int:
        for country in self.list:
            for city in country.cities:
                if city.name == name:
                    return city.id
                for alias in city.aliases:
                    if alias == name:
                        return city.id

    def get_city_name(self, id: int) -> str:
        for country in self.list:
            for city in country.cities:
                if city.id == id:
                    return city.name

    def starts_with(self, substr: str) -> list[str]:
        result = []
        for country in self.list:
            for city in country.cities:
                if city.name.startswith(substr):
                    result.append(city.name)
                for alias in city.aliases:
                    if alias.startswith(substr):
                        result.append(alias)
        return result