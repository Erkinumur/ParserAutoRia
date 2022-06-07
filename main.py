from parsers import ParserAutoRia


if __name__ == '__main__':
    parser = ParserAutoRia()
    cars_list = parser.start_parse()
    print(len(cars_list))
