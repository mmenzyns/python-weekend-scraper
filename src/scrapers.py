from .location import Locations
from .route import RegioJetRoute, Route
from .storage import redis_load_location_id, redis_save_location_id
from . import SearchInput
from . import scrapers
from . import storage

import requests
import logging
from fastapi import HTTPException


def scrape_regio_locations() -> Locations:
    r = requests.get(
        'https://brn-ybus-pubapi.sa.cz/restapi/consts/locations', auth=('user', 'pass'))

    if r.status_code != 200:
        raise HTTPException(r.status_code, r.text)

    return Locations.from_json(r.json())


logging.info("Scraping locations")
locations = scrape_regio_locations()


def get_location_id(location: str) -> int:
    id = redis_load_location_id(location)

    if id is not None:
        return id

    id = locations.get_city_code(location)
    if id is None:
        raise ValueError("Location not found")

    redis_save_location_id(location, id)

    return id


def scrape_regio_search(source_id: int, destination_id: int, input: SearchInput) -> list[Route]:

    params = {
        'tariffs': "REGULAR",
        'toLocationType': "CITY",
        'toLocationId': destination_id,
        'fromLocationType': "CITY",
        'fromLocationId': source_id,
        'departureDate': input.date,
    }
    r = requests.get('https://brn-ybus-pubapi.sa.cz/restapi/routes/search/simple',
                     params=params, auth=('user', 'pass'), headers={'x-currency': 'EUR'})

    routes_dict = r.json()['routes']
    regio_routes = [RegioJetRoute(**route_dict)
                    for route_dict in routes_dict if route_dict['bookable']]
    return routes_from_regio(regio_routes, input)


def routes_from_regio(regio_routes: RegioJetRoute, input: SearchInput) -> list[Route]:
    routes = []
    for regio_route in regio_routes:
        source = input.origin
        destination = input.destination
        departure_datetime = regio_route.departureTime
        arrival_datetime = regio_route.arrivalTime
        # carrier = "REGIOJET"
        # vehicle_type = " ".join(regio_route.vehicleTypes)
        # price = regio_route.priceFrom
        # currency = "EUR"

        routes.append(Route(
            source, destination,
            departure_datetime, arrival_datetime
        ))

    return routes


def scrape_search(input: SearchInput):
    logging.info("Getting location ids")
    try:
        origin_id = get_location_id(input.origin)
        destination_id = get_location_id(input.destination)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    logging.info("Scraping routes")
    routes = scrapers.scrape_regio_search(
        origin_id, destination_id, input)

    logging.info("Saving locations to storage")

    storage.redis_save_routes(input, routes)

    storage.database_save_routes(routes)

    return routes
