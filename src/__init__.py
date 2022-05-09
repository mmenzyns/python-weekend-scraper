from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from redis import Redis
from collections import namedtuple

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


logging.basicConfig(level=logging.INFO)

load_dotenv('.env')

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB_ID = os.getenv("REDIS_DB_ID")
DATABASE_URL = os.getenv("DATABASE_URL")

SearchInput = namedtuple('RouteSearch', ['origin', 'destination', 'date'])

redis = Redis(host=f"{REDIS_HOST}", port=REDIS_PORT, db=REDIS_DB_ID,
              password=f"{REDIS_PASSWORD}", decode_responses=True)

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool
)

Base = declarative_base()