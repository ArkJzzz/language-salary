#!usr/bin/python3

"""
Module Docstring
Docstrings: http://www.python.org/dev/peps/pep-0257/
"""


__author__ = 'ArkJzzz (arkjzzz@gmail.com)'


import requests
import logging
import collections
import statistics
import argparse
from itertools import count


def sort_dictionary_by_values(dictionary, reverse=False):
    sorted_dictionary = sorted(
        dictionary.items(), 
        key=lambda k: k[1], 
        reverse=reverse # Если нужно по возрастанию, то reverse=False
        )
    return collections.OrderedDict(sorted_dictionary)


def get_vacancies(language, page=0, area=2, only_with_salary=True):
    host = 'api.hh.ru'
    url = 'https://{host}/vacancies'.format(host=host)
    payload = {
        'text': 'Программист {language}'.format(language=language),
        'area': area,
        'only_with_salary': only_with_salary,
        'page': page
    }

    response = requests.get(url, params=payload)
    response.raise_for_status()

    return response.json()


def predict_rub_salary(vacancy):
    salary = vacancy['salary']
    if salary['currency'] == 'RUR':
        if not salary['to']:
            return salary['from'] * 1.2
        elif not salary['from']:
            return salary['to'] * 0.8
        else:
            return statistics.mean([salary['from'], salary['to']])
    else:
        return None


def get_hhru_statistics(languages, area, only_with_salary):
    language_stat = {}

    for language in languages: 
        vacancies_items = []
        for page in count(0):
            vacancies = get_vacancies(language, page, area, only_with_salary)
            pages = vacancies['pages']
            if page >= pages:
                break
            for vacancy in vacancies['items']:
                vacancies_items.append(vacancy)

        all_language_salaryes = [predict_rub_salary(vacancy) for vacancy in vacancies_items if predict_rub_salary(vacancy)]

        average_salary = statistics.mean(all_language_salaryes)
        average_salary = int(average_salary)
        language_data = {
            'vacancies_found': vacancies['found'],
            'vacancies_processed': len(all_language_salaryes),
            'average_salary': average_salary
        }

        language_stat[language] = language_data

    return language_stat


def print_hhru_statistics(language_stat):
    for language, stat in language_stat.items():
        print(language)
        print(stat)


   

def main():

    # init

    logging.basicConfig(format = u'[LINE:%(lineno)d]#  %(message)s', level = logging.DEBUG)


    # do

    parser = argparse.ArgumentParser(
        description='Сбор вакансий на сайте hh.ru'
        )

    parser.add_argument(
        '-l', 
        '--languages', 
        nargs='*', 
        help='введите названия интересующих языков программирования через пробел'
    )
    parser.add_argument(
        '-a', 
        '--area', 
        type=int, 
        default=2, 
        help='код региона (по умолчанию 2 - Санкт-Петербург)'
    )

    parser.add_argument(
        '-s', 
        '--only_with_salary', 
        type=bool,
        default=True, 
        help='Только вакансии, где указана зарплата (True, False)'
    )

    args = parser.parse_args()

    logging.debug(args.languages)
    logging.debug(args.area)
    logging.debug(args.only_with_salary)

    try:
        language_stat = get_hhru_statistics(args.languages, args.area, args.only_with_salary)
        print_hhru_statistics(language_stat)
        print(language_stat)
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
        logging.error('HTTPError: Not Found', exc_info=True)


if __name__ == '__main__':
    main()



