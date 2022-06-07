from dataclasses import dataclass
from datetime import datetime
from typing import List

import requests
from parsel import Selector
from requests import Response

from exceptions import BadRequestException
from models import CarInfo


class ParserAutoRia:
    BASE_URL = 'https://auto.ria.com/uk/car/used/'

    def _get_response(self, url: str) -> Response:
        resposne = requests.get(url)
        if resposne.status_code == 200:
            return resposne
        raise BadRequestException(
            f'url: {url}\nstatus_code: {resposne.status_code}'
        )

    def get_last_page_number(self) -> int:
        response = self._get_response(self.BASE_URL)
        selector = Selector(response.text)
        last_page = int(
            selector.xpath('//a[@class="page-link"]/text()')[-1]
                .get().replace(' ', '')
        )
        return last_page

    def get_next_url(self) -> str:
        last_page = self.get_last_page_number()
        page = 2
        yield self.BASE_URL
        while page <= last_page:
            yield self.BASE_URL + f'?page={page}'
            page += 1

    def parse_car_info(self, url: str) -> CarInfo:
        response = self._get_response(url)
        selector = Selector(response.text)

        price = selector.xpath('//div[@class="price_value"]/strong/text()').extract_first()
        price = int(price[:-1].replace(' ', ''))

        owner_name = selector.xpath('//h4[@class="seller_info_name bold"]/text()').get()

        img_count = selector.xpath('//a[@class="show-all link-dotted"]/text()').get('')
        if img_count:
            img_count = int([int(s) for s in img_count.split() if s.isdigit()][0])

        car_number = selector.xpath('//span[contains(@class, "state-num")]/text()').get()
        vin_code = selector.xpath('//span[@class="label-vin"]/text()').get()

        car = CarInfo(
            title=selector.xpath('//h1/text()').extract_first().strip(),
            price=price,
            mileage=int(
                selector.xpath('//div[@class="base-information bold"]/span/text()')
                    .get().strip()
            ),
            owner_name=owner_name.strip() if owner_name else '',
            phone_number='+380' + selector.xpath(
                '//span[@title="Перевірений  телефон"]/@data-phone-number').get(),
            img_url=selector.xpath('//div[@class="photo-620x465"]//img/@src').extract_first(),
            img_count=img_count,
            car_number=car_number.strip() if car_number else '',
            vin_code=vin_code.strip() if vin_code else '',
            datetime_found=datetime.utcnow()
        )

        print(f'{url} is parsed')

        return car

    def parse_links_from_catalog_page(self, url: str) -> List[str]:
        response = self._get_response(url)
        selector = Selector(response.text)
        links = selector.xpath('//a[@class="address"]')
        print(len(links))
        return [i.attrib.get('href', '') for i in links]

    def start_parse(self, limit: int = 0):
        if limit:
            count = 1
        cars_list = []
        for url in self.get_next_url():
            links = self.parse_links_from_catalog_page(url)
            cars = [
                self.parse_car_info(link)
                for link in links
            ]
            cars_list.extend(cars)

            if limit:
                if count >= limit:
                    break
                count += 1
        return cars_list


if __name__ == '__main__':
    parser = ParserAutoRia()
    cars_list = parser.start_parse()
    print(len(cars_list))
