import argparse

from src.parsers import ParserAutoRia


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-l', '--limit', default=0, type=int)
    arg_parser.add_argument('-p', '--page', default=1, type=int)
    args = arg_parser.parse_args()

    parser = ParserAutoRia()
    parser.start_parse(limit=args.limit, start_page=args.page)
    print('finish')

