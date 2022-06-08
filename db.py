import os
from typing import Iterable

import psycopg2

from models import CarInfo


def connect_to_db():
    try:
        # connection = psycopg2.connect(user=os.getenv("POSTGRES_USER"),
        #                               password=os.getenv("POSTGRES_PASSWORD"),
        #                               host=os.getenv("PG_HOST"),
        #                               port=os.getenv("POSTGRES_USER"),
        #                               database=os.getenv("POSTGRES_DB"))

        connection = psycopg2.connect(user="parser",
                                      password="parserpassword",
                                      host="localhost",
                                      port="5434",
                                      database="autoria")

        cursor = connection.cursor()

    except (Exception, psycopg2.Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
        return None, None

    if connection:
        return connection, cursor
    
    
class Database:
    connection, cursor = connect_to_db()
    table = os.getenv('TABLE_NAME', 'cars_info')
    
    @classmethod
    def insert_car_info_data(cls, data: Iterable[CarInfo]):
        query = f'INSERT INTO {cls.table} (' \
                f'url, title, price, mileage, owner_name, phone_number,' \
                f'img_url, img_count, car_number, vin_code) VALUES '

        for car in data:
            query += car.format_to_query() + ','

        query = query[:-1]

        cls.cursor.execute(query)
        cls.connection.commit()

    @classmethod
    def close_connection(cls):
        cls.cursor.close()
        cls.connection.close()
