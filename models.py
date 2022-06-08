from dataclasses import dataclass
from datetime import datetime


@dataclass
class CarInfo:
    url: str
    title: str
    price: int
    mileage: int
    owner_name: str
    phone_number: str
    img_url: str
    img_count: int
    car_number: str
    vin_code: str

    def format_to_query(self):
        result = f"('{self.url}', '{self.title}', {self.price}," \
                 f"{self.mileage}, "
        result += f"'{self.owner_name}', " if self.owner_name else "null, "
        result += f"'{self.phone_number}', '{self.img_url}', {self.img_count}, "
        result += f"'{self.car_number}', " if self.car_number else "null, "
        result += f"'{self.vin_code}')" if self.vin_code else "null)"

        return result
