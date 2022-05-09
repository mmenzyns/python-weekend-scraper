from slugify import slugify
from . import redis, engine
from . import SearchInput, Base

from . import serialize
from .route import Route

from datetime import date, datetime
import json

from sqlalchemy.orm.session import Session
from sqlalchemy import Column, Integer, String, FLOAT, cast, Date
from sqlalchemy.dialects.postgresql import TIMESTAMP


class DatabaseJourney(Base):
    __tablename__ = "menzynski_journeys"
    id = Column(Integer, primary_key=True)

    origin = Column(String(255))
    destination = Column(String(255))
    departure = Column(TIMESTAMP)
    arrival = Column(TIMESTAMP)
    carrier = Column(String(255))
    vehicle_type = Column(String(255))
    price = Column(FLOAT)
    currency = Column(String(3))

    def __init__(self, **kwargs):
        # Replace datetime types before initialization
        if type(kwargs['departure']) is str:
            kwargs['departure'] = datetime.fromisoformat(kwargs['departure'])
        if type(kwargs['arrival']) is str:
            kwargs['arrival'] = datetime.fromisoformat(kwargs['arrival'])

        super(DatabaseJourney, self).__init__(**kwargs)


# # Uncomment this to create a new table
# Base.metadata.create_all(engine)

def redis_search_routes(input: SearchInput) -> list[Route]:
    """Takes origin, destination and date from input. Searches for routes matching input in redis and returns them. Returns empty list otherwise.
    """
    routes_redis = redis.get(
        f"menzynski:journey:{input.origin}_{input.destination}_{input.date}")

    if routes_redis is None:
        return []

    try:
        routes_dict = json.loads(routes_redis)
    except json.decoder.JSONDecodeError:
        # Continue despite error, to keep the service functional
        return []
    else:
        return [Route(**route) for route in routes_dict]


def redis_load_location_id(location: str) -> int:
    """Searches for location_id based on location name in redis. Returns None if not found."""
    location_key = slugify(location)
    
    return redis.get(f"menzynski:location:{location_key}")


def redis_save_routes(input: SearchInput, routes: list[Route]):
    route_key = "menzynski:journey:{}_{}_{}".format(
        slugify(input.origin), slugify(input.destination), input.date)

    redis.set(route_key, serialize.routes_dump(routes, separators=(',', ': ')))


def redis_save_location_id(location: str, id: int):
    location_key = slugify(location)

    redis.set(f"menzynski:location:{location_key}", id)


def database_search_routes(input: SearchInput) -> list[Route]:
    """Takes origin, destination and date from input. Searches for routes matching input in database and returns them. Returns empty list otherwise.
    """
    routes = []
    with Session(engine) as session:
        journeys = session.query(DatabaseJourney).filter(
            DatabaseJourney.origin == input.origin,
            DatabaseJourney.destination == input.destination,
            cast(DatabaseJourney.departure,
                 Date) == date.fromisoformat(input.date)
        )

        for journey in journeys:
            route = Route(**journey.__dict__)
            routes.append(route)

            redis_save_routes(input, routes)

    return routes


def database_save_routes(routes: list[Route]):
    with Session(engine) as session:
        for route in routes:
            route_dict = route.__dict__
            journey = DatabaseJourney(**route_dict)
            # Add newly created object to the session
            session.add(journey)
        # Execute in the DB
        session.commit()
