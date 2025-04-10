import re

import psycopg2

from src.config import config
from src.database_manager import DBManager
from src.database_utils import create_database, create_table_to_database, save_data_to_database
from src.hh import HH
from src.utils import greeting, get_companies_and_vacancies_count_parser, get_all_vacancies_parser, \
    get_vacancies_keyword_or_high_salary_parser


def start_function(word: str) -> str:
    if re.fullmatch("нет", word, flags=re.I):
        return "Возвращайтесь когда вам удобно."
    elif re.fullmatch("да", word, flags=re.I):
        return "Приступим!"
    else:
        return "Не понимаю вас попробуйте снова."


def head_hunter_function(word: str) -> list:
    try:
        if re.fullmatch("1", word):
            print("Ищу работодателей...")
            return HH().employers_data()
        elif re.fullmatch("2", word):
            print("""Вы можете передать поочередно через пробел слово,
по которому будет производится поиск интересующих вас работодателей,
номер страницы с которой будет начинаться пагинация,
количество элементов на странице, и максимальное количество работодателей,
или оставить поле пустым чтобы выполнить стандартный запрос.
(При формировании запроса помните, что кол-во элементов в ответе должно соответствовать,
или быть меньше кол-ва элементов на странице!!!)""")
            hh_input = input().split()
            if len(hh_input) == 4:
                keyword = hh_input[0]
                page = hh_input[1]
                per_page = hh_input[2]
                max_employers = hh_input[3]
                if int(per_page) > int(max_employers):
                    print(f"Кол-во элементов: {per_page} не может быть больше кол-ва работодателей: {max_employers}")
                    return []
                else:
                    print("Ищу работодателей...")
                    return HH(
                        keyword=keyword,
                        page=int(page),
                        per_page=int(per_page),
                        max_employers=int(max_employers)
                    ).employers_data()
            elif len(hh_input) == 0:
                print("Ищу работодателей без указанного вами описания...")
                return HH().employers_data()
            else:
                print("Неккоректные данные, пожалуйста ознакомьтесь с информацией о допустимых данных.")
                return []
        else:
            print("""Ошибка получения вакансий!
Возможно вы передаете не правильный номер, или по вашему запросу ничего не нашлось.""")
            return []
    except TypeError as e:
        print(f"Ошибка: {e}")
        return []
    except ValueError as e:
        print(f"Ошибка: {e}")
        return []


def main(params: dict) -> str | list:
    """
    Функция взаимодействия с пользователем
    """
    print(greeting())
    print("""Это приложение предоставляет возможность заполнить таблицы работодателей,
и таблицу вакансий соответствующими данными о вакансиях этих работодателей.
Вы готовы?""")
    user_input = input()
    user_stack = start_function(user_input)

    if not re.fullmatch("приступим!", user_stack, flags=re.I):
        print(start_function(user_input))
        return "До новых встреч!"
    else:
        print("""Для того чтобы получить информацию о работодателях с 'hh.ru' введите 1,
чтобы получить информацию о работодателях по определенному слову в описании введите 2:""")
    hh_input = input()
    hh_stack = head_hunter_function(hh_input)
    if not hh_stack:
        return "Попробуйте снова!"
    else:
        print("Данные получены!")
        print("""Следующий этап это создание таблицы с данными о работодателях, и таблицы с данными о вакансиях.
Вы можете передать название для внешнего сервера, или оставить поле пустым для применения дефолтного значения.
ЕсЛи ВаШа Бд УжЕ сОзДаНа И вЫ хОтИтЕ пРоСмАтРиВаТь Ее То ВвЕдИтЕ ! eXiT ! :) """)
    db_input = input("Название бд: ")
    if not re.fullmatch("eXiT", db_input, flags=re.I):
        if len(db_input) == 0:
            name = "headhunterapiworker"
        else:
            name = db_input
        database = create_database(name=name, params=params)
        tables = create_table_to_database(name=name, params=params)
        saving = save_data_to_database(
            name=name, params=params, employers=hh_stack, vacancies=HH().vacancies_data(hh_stack)
        )
        print(database)
        print(tables)
        print(saving)
    elif re.fullmatch("eXiT", db_input, flags=re.I):
        print("Введите название базы данных:")
        name_input = input()
        name = name_input
        print("Перехожу к бд без ее создания...")
    else:
        print("Неккоректный ввод!")
        return []

    print("""
Введите 1 для получения всех компаний и их работодателей,
2 для всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию,
3 для рассчета средней зарплаты по всем вакансиям,
4 для получения всех вакансий у которых значение зарплаты выше среднего значения зарплаты по всем вакансиям,
5 для получения вакансий по определнному слову в описании
""")
    finally_input = input()
    dbase = DBManager(name=name, params=params)
    try:
        if re.fullmatch("1", finally_input):
            return get_companies_and_vacancies_count_parser(
                dbase.get_companies_and_vacancies_count()
            )
        elif re.fullmatch("2", finally_input):
            return get_all_vacancies_parser(dbase.get_all_vacancies())
        elif re.fullmatch("3", finally_input):
            return dbase.get_avg_salary()
        elif re.fullmatch("4", finally_input):
            return get_vacancies_keyword_or_high_salary_parser(dbase.get_vacancies_with_higher_salary())
        elif re.fullmatch("5", finally_input):
            print("Введите слово для поиска:")
            word_input = input()
            db = get_vacancies_keyword_or_high_salary_parser(
                dbase.get_vacancies_with_keyword(word_input)
            )
            if not db:
                print("Таких вакансий нету в базе данных, попробуйте снова!")
                return []
            else:
                return db
    except psycopg2.Error as e:
        return f"Ошибка: {e}"


#if __name__ == "__main__":
    #print(main(params=config()))
