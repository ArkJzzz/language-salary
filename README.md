# Vacancy salaries

Утилита помогает проанализировать вакансии с сайтов [HeadHunter](https://hh.ru 'hh.ru') и [SuperJob](https://www.superjob.ru/ 'superjob.ru/'): скачивает все вакансии разработчиков и отображает в виде таблицы количество вакансий и среднюю зарплату по каждому из популярных яхыков программирования.


## Подготовка

Получите секретный ключ (Secret key) к [API SuperJob](https://api.superjob.ru/)


## Установка

1. Клонировать репозиторий:
```
git clone https://github.com/ArkJzzz/language-salary.git
```

2. Создать файл ```.env``` и поместить в него секретный ключ (Secret key) к [API SuperJob](https://api.superjob.ru/):
```
X_Api_App_Id='Ваш_секретный_ключ'
Authorization=Bearer r.000000010000001.example.access_token
```

3. Установить зависимости: 
```
pip3 install -r requirements.txt
```


## Запуск

Для запуска программы введите:
```
python3 main.py 
```


## Примерный результат выполнения

![](//example.png/600x200)





 