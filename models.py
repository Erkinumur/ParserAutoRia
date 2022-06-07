from dataclasses import dataclass
from datetime import datetime


@dataclass
class CarInfo:
    title: str
    price: int
    mileage: int
    owner_name: str
    phone_number: str
    img_url: str
    img_count: int
    car_number: str
    vin_code: str
    datetime_found: datetime
