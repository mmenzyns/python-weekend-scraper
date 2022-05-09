import json
from datetime import datetime

from .route import Route


def handler(x):
    """Handler function for print_json to help the function with unrecognized objects
    """
    if isinstance(x, datetime):
        return x.isoformat()
    # if isinstance(x, timedelta):
    #     return str(x)
    if isinstance(x, Route):
        return x.__dict__
    raise TypeError("Unknown type {}".format(type(x)))


def routes_dump(routes, separators=None) -> str:
    return json.dumps(routes, default=handler, separators=separators)
