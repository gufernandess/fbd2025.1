import os
import psycopg2 as pg
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from psycopg2.extensions import connection as PgConnection
from typing import Tuple

def create_db_connections() -> Tuple[PgConnection, Engine]:
    load_dotenv()

    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASS')
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')

    connection = pg.connect(
        host=db_host,
        dbname=db_name,
        user=db_user,
        password=db_pass
    )

    connection_string = f'postgresql://{db_user}:{db_pass}@{db_host}/{db_name}'
    engine = create_engine(connection_string)

    return connection, engine
