#!usr/bin/python3

"""
Module Docstring
Docstrings: http://www.python.org/dev/peps/pep-0257/
"""

###################################
#    ToDo
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
import os
from dotenv import load_dotenv
# from itertools import count
import itertools


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


def get_sj_vacancies(X_Api_App_Id, sj_auth, language, catalogues, page, count, town):
    host = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {
        'X-Api-App-Id': X_Api_App_Id,
        'Authorization': sj_auth,
    }
    payload = {
        'keyword': 'Программист {language}'.format(language=language),
        'catalogues': catalogues,
        'page': page,
        'town': town,

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

        if len(all_language_salaryes) > 0:
            average_salary = statistics.mean(all_language_salaryes)
        else:
            average_salary = 0
        average_salary = int(average_salary)
        language_data = {
            'vacancies_found': vacancies['found'],
            'vacancies_processed': len(all_language_salaryes),
            'average_salary': average_salary
        }

        language_stat[language] = language_data

    return language_stat


def get_sj_statiscics(languages, X_Api_App_Id, sj_auth, catalogues=33, town=14):
    language_stat = {}
    count = 100 #количество результатов на странице, 100 - максимальное

    for language in languages: 
        vacancies_items = []
        for page in itertools.count(0):
            vacancies = get_sj_vacancies(X_Api_App_Id, sj_auth, language, catalogues, page, count, town)
            pages = (vacancies['total'] // count) + 1
            if page >= pages:
                break
            for vacancy in vacancies['objects']:
                vacancies_items.append(vacancy)

        all_language_salaryes = [predict_rub_salary_sj(vacancy) for vacancy in vacancies_items if predict_rub_salary_sj(vacancy)]
        
        if len(all_language_salaryes) > 0:
            average_salary = statistics.mean(all_language_salaryes)
        else:
            average_salary = 0
        average_salary = int(average_salary)
        language_data = {
            'vacancies_found': vacancies['total'],
            'vacancies_processed': len(all_language_salaryes),
            'average_salary': average_salary
        }

        language_stat[language] = language_data


    return language_stat



def print_statistics(language_stat):
    for language, stat in language_stat.items():
        print(language)
        print(stat)



   

def main():

    # init

    logging.basicConfig(format = u'[LINE:%(lineno)d]#  %(message)s', level = logging.DEBUG)

    load_dotenv()
    X_Api_App_Id = os.getenv("X_Api_App_Id")
    sj_auth = os.getenv("Authorization")




    languages = [
        'python',
        'php',
        'java',
        'javascript',
        'go',
    ]

    catalogues = 33
    page = 3
    town = 14
    area = 2
    only_with_salary = True

    # do



    # try:
    #     hh_language_stat = get_hhru_statistics(languages, area, only_with_salary)
    #     print_statistics(hh_language_stat)
    #     print(hh_language_stat)
    # except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
    #     logging.error('HTTPError: Not Found', exc_info=True)


    try:
        sj_language_stat = get_sj_statiscics(languages, X_Api_App_Id, sj_auth)
        print_statistics(sj_language_stat)


    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
        logging.error('HTTPError: Not Found', exc_info=True)



if __name__ == '__main__':
    main()


# ['objects', 'total', 'subscription_active', 'subscription_id', 'more']

# ['agreement', 'canEdit', 'id_client', 'maritalstatus', 'date_published', 
# 'education', 'experience', 'gender', 'firm_name', 'languages', 'rejected', 
# 'is_archive', 'compensation', 'id', 'metro', 'moveable', 'age_from', 'response_info', 
# 'driving_licence', 'anonymous', 'is_closed', 'agency', 'fax', 'profession', 'place_of_work', 
# 'age_to', 'payment', 'date_archived', 'highlight', 'latitude', 'date_pub_to', 'children', 
# 'work', 'client_logo', 'is_storage', 'catalogues', 'vacancyRichText', 'payment_from', 
# 'client', 'longitude', 'candidat', 'link', 'payment_to', 'address', 'town', 'phones', 
# 'faxes', 'firm_activity', 'phone', 'type_of_work', 'currency', 'already_sent_on_vacancy']

