create table cars_info (
	id serial primary key,
	url varchar unique not null,
	title varchar not null,
	price int not null,
	mileage int,
	owner_name varchar,
	phone_number varchar,
	img_url varchar,
	img_count int,
	car_number varchar,
	vin_code varchar,
	datetime_found timestamp default (now() at time zone 'utc')
);