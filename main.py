from src import scrapers
from src import storage

from src import SearchInput, app
from src.route import Route

from fastapi import responses
import logging


def get_routes(input: SearchInput) -> list[Route]:

    logging.info("Searching through redis")
    routes = storage.redis_search_routes(input)
    if routes:
        logging.info("Routes found in redis")
        return routes

    logging.info("Checking database")
    routes = storage.database_search_routes(input)
    if routes:
        logging.info("Routes find in database")
        return routes

    logging.info("Scraping routes")
    return scrapers.scrape_search(input)


@app.get('/search')
def search(origin: str, destination: str, departure: str):

    input = SearchInput(origin, destination, departure)

    routes = get_routes(input)

    results = [route.get_dict() for route in routes]

    return responses.JSONResponse(results)


@app.get("/whisper")
def whisper(text: str):
    return scrapers.locations.starts_with(text.capitalize())


if __name__ == "__main__":
    ori = "Prague"
    des = "Olomouc"
    dep = "2022-05-10"

    resp = search(ori, des, dep)
    print(resp.body)
    print(resp.status_code)
