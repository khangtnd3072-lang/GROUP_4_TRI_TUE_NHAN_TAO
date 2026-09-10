from contextlib import contextmanager
from datetime import date, datetime, time, timedelta
from decimal import Decimal

import mysql.connector

from app.core.config import settings


def get_connection():
    return mysql.connector.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
        autocommit=False,
    )


@contextmanager
def db_cursor(dictionary=True):
    connection = get_connection()
    cursor = connection.cursor(dictionary=dictionary)
    try:
        yield connection, cursor
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def fetch_all(query, params=None):
    with db_cursor() as (_, cursor):
        cursor.execute(query, params or ())
        return cursor.fetchall()


def fetch_one(query, params=None):
    with db_cursor() as (_, cursor):
        cursor.execute(query, params or ())
        return cursor.fetchone()


def execute(query, params=None):
    with db_cursor() as (_, cursor):
        cursor.execute(query, params or ())
        return cursor.lastrowid


def to_jsonable(value):
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()

    if isinstance(value, timedelta):
        total_seconds = int(value.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, dict):
        return {
            key: to_jsonable(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            to_jsonable(item)
            for item in value
        ]

    return value
