from typing import List, Iterable

import requests
from parsel import Selector
from requests import Response

from .db import Database
from .exceptions import BadRequestException, UniqueConstraintException
from .models import CarInfo


class ParserAutoRia:
    BASE_URL = 'https://auto.ria.com/uk/car/used'

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
        ) * 2
        print(f'lastpage - {last_page}')
        return last_page

    def get_next_url(self, start_page: int = 1) -> str:
        last_page = self.get_last_page_number()
        page = start_page
        while page <= last_page:
            yield self.BASE_URL + f'?page={page}'
            page += 1

    def parse_car_info(self, url: str) -> CarInfo | None:
        response = self._get_response(url)
        selector = Selector(response.text)

        if selector.xpath('//div[contains(@class, "sold-out")]'):
            return

        price = selector.xpath('//span[@data-currency="USD"]/text()').get()
        if not price:
            price = selector.xpath('//div[@class="price_value"]/strong/text()').get()
        if price:
            price = int(price.replace(' ', '').replace('$', ''))

        mileage = selector.xpath('//div[@class="base-information bold"]/span/text()').get()
        if mileage:
            mileage = int(mileage.strip())

        owner_name = selector.xpath('//h4[@class="seller_info_name bold"]/text()').get()
        if not owner_name:
            owner_name = selector.xpath('//h4[@class="seller_info_name"]/a/text()').get()
        if not owner_name:
            owner_name = selector.xpath('//h4[@class="seller_info_name"]/a/strong/text()')

        phone_number = selector.xpath(
            '//span[@class="phone bold"]/@data-phone-number').get()
        if phone_number:
            phone_number = '+380 ' + phone_number

        img_count = selector.xpath('//a[@class="show-all link-dotted"]/text()').get()
        if img_count:
            img_count = int([int(s) for s in img_count.split() if s.isdigit()][0])

        car_number = selector.xpath('//span[contains(@class, "state-num")]/text()').get()
        vin_code = selector.xpath('//span[@class="label-vin"]/text()').get()

        car = CarInfo(
            url=url,
            title=selector.xpath('//h1/text()').extract_first().strip(),
            price=price,
            mileage=mileage,
            owner_name=owner_name.strip() if owner_name else None,
            phone_number=phone_number,
            img_url=selector.xpath('//div[@class="photo-620x465"]//img/@src').extract_first(),
            img_count=img_count,
            car_number=car_number.strip() if car_number else None,
            vin_code=vin_code.strip() if vin_code else None
        )

        print(f'{url} is parsed')

        return car

    def parse_links_from_catalog_page(self, url: str) -> List[str]:
        response = self._get_response(url)
        selector = Selector(response.text)
        links = selector.xpath('//a[@class="address"]')
        print(len(links))
        print(url, end='\n\n')
        return [i.attrib.get('href', '') for i in links]

    def start_parse(self, limit: int = 0, start_page: int =1):
        if limit:
            count = 1

        for url in self.get_next_url(start_page):
            links = self.parse_links_from_catalog_page(url)
            cars = [
                self.parse_car_info(link)
                for link in links
            ]

            try:
                self.write_data_to_db([car for car in cars if car])
            except UniqueConstraintException:
                print('unique constraint')
                break

            if limit:
                if count >= limit:
                    break
                count += 1

    def write_data_to_db(self, data: Iterable[CarInfo]):
        Database.insert_car_info_data(data)
