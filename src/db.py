import os
from typing import Iterable

import psycopg2
from psycopg2.errorcodes import UNIQUE_VIOLATION

from .exceptions import UniqueConstraintException
from .models import CarInfo
    
    
class Database:
    def __init__(self):
        self.connection, self.cursor = self.connect_to_db()
        self.table = os.getenv('TABLE_NAME', 'cars_info')

    def connect_to_db(self):
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
    
    def insert_car_info_data(self, data: Iterable[CarInfo]):
        query = f'INSERT INTO {self.table} (' \
                f'url, title, price, mileage, owner_name, phone_number,' \
                f'img_url, img_count, car_number, vin_code) VALUES '

        unique_error_count = 0

        for car in data:
            try:
                self.cursor.execute(query + car.format_to_query())
                self.connection.commit()
            except psycopg2.Error as e:
                if e.pgcode == UNIQUE_VIOLATION:
                    unique_error_count += 1
                    self.connection.rollback()
                    continue
                raise e

        query = query[:-1]

        if unique_error_count == len(data):
            raise UniqueConstraintException

    def close_connection(self):
        self.cursor.close()
        self.connection.close()
