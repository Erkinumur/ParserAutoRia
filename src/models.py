from dataclasses import dataclass


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
        result = "("

        for field, value in self.__dict__.items():
            if isinstance(value, str):
                if "'" in value:
                    value = value.replace("'", "\"")
                result += f"'{value}', "
            elif value is None:
                result += 'null, '
            else:
                result += f"{value}, "

        result = result[:-2] + ')'

        return result
