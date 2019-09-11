#!usr/bin/python3

"""
Module Docstring
Docstrings: http://www.python.org/dev/peps/pep-0257/
"""

###################################
#    ToDo
# Убрать токен в .env
# убрать файлы fetch_hhru_vacancies.py и fetch_superjob_vacancies.py из индекса git
# Посчитайте среднюю зарплату по языкам на SuperJob 
# Сделайте красивый вывод в консоль [terminaltables]
# Выведите таблицу статистику по двум сайтам 
# git
# readme.md
# сдать на проверку
####################################

__author__ = 'ArkJzzz (arkjzzz@gmail.com)'


import requests
import logging
import collections
import statistics
import argparse
from itertools import count
from dotenv import load_dotenv


def sort_dictionary_by_values(dictionary, reverse=False):
    sorted_dictionary = sorted(
        dictionary.items(), 
        key=lambda k: k[1], 
        reverse=reverse # Если нужно по возрастанию, то reverse=False
        )
    return collections.OrderedDict(sorted_dictionary)


def get_hhru_vacancies(language, page=0, area=2, only_with_salary=True):
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

def get_sj_vacancies():
    host = 'https://api.superjob.ru/2.0/vacancies/'

    ## FIXME: убрать нахер отсюда токен
    headers = {
        'X-Api-App-Id': X_Api_App_Id,
        'Authorization': sj_authorization,
    }
    payload = {
        'keyword': 'программист',
        'town': 14,
        'catalogues': 33,
    }

    response = requests.get(host, headers=headers, params=payload)
    response.raise_for_status()

    return response.json()


def predict_salary(salary_from, salary_to):
    if not salary_from and not salary_to:
        return None
    if not salary_to:
        return salary_from * 1.2
    elif  not salary_from:
        return salary_to * 0.8
    else:
        return statistics.mean([salary_from, salary_to])


def predict_rub_salary_hhru(vacancy):
    salary = vacancy['salary']
    if salary['currency'] == 'RUR':
        salary_from = vacancy['salary']['from']
        salary_to = vacancy['salary']['to']
        return predict_salary(salary_from, salary_to)
    else:
        return None


def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] == 'rub':
        salary_from = vacancy['payment_from']
        if salary_from == 0:
            salary_from = None
        salary_to = vacancy['payment_to']
        if salary_to == 0:
            salary_to = None
        return predict_salary(salary_from, salary_to)
    else:
        return None


def get_hhru_statistics(languages, area, only_with_salary):
    language_stat = {}

    for language in languages: 
        vacancies_items = []
        for page in count(0):
            vacancies = get_hhru_vacancies(language, page, area, only_with_salary)
            pages = vacancies['pages']
            if page >= pages:
                break
            for vacancy in vacancies['items']:
                vacancies_items.append(vacancy)

        all_language_salaryes = [predict_rub_salary_hhru(vacancy) for vacancy in vacancies_items if predict_rub_salary_hhru(vacancy)]

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


def print_sj_statistics(vacancy, payment):
    print('{profession}, {town}, {payment}, {currency}'.format(
        profession=vacancy['profession'], 
        town=vacancy['town']['title'],
        payment=payment,
        currency=vacancy['currency'],
        salary_from=vacancy['payment_from'],
        salary_to=vacancy['payment_to'],
        )
    )

   

def main():

    # init

    logging.basicConfig(format = u'[LINE:%(lineno)d]#  %(message)s', level = logging.DEBUG)

    load_dotenv()
    X_Api_App_Id = os.getenv("X_Api_App_Id")
    sj_authorization = os.getenv("Authorization")



    area = 2
    only_with_salary = True
    languages = [
        'python',
        'php',
        'java',
        'javascript',
        'go',
        'c',
    ]


    # do



    # try:
    #     language_stat = get_hhru_statistics(languages, area, only_with_salary)
    #     print_hhru_statistics(language_stat)
    #     print(language_stat)
    # except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
    #     logging.error('HTTPError: Not Found', exc_info=True)


    try:
        vacancies = get_sj_vacancies()
        for vacancy in vacancies['objects']:    
            payment = predict_rub_salary_sj(vacancy)
            print_sj_statistics(vacancy, payment)
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
        logging.error('HTTPError: Not Found', exc_info=True)



if __name__ == '__main__':
    main()



