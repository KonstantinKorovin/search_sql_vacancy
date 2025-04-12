import pytest

from src.utils import (
    database_salary,
    get_all_vacancies_parser,
    get_companies_and_vacancies_count_parser,
    get_vacancies_keyword_or_high_salary_parser,
    head_hunter_employers_information,
    head_hunter_vacancies_information,
    salary,
)


@pytest.mark.parametrize(
    "result, expected",
    [
        (
            [{"id": 0, "employer_id": 1, "name": 2, "alternate_url": "str", "open_vacancies": 4, "work": True}],
            [{"employer_id": 0, "name": 2, "url": "str", "open_vacancies": 4}],
        ),
        (
            [{"id": 100, "employer_id": 13, "name": "1", "alternate_url": "int", "open_vacancies": 90, "work": False}],
            [{"employer_id": 100, "name": "1", "url": "int", "open_vacancies": 90}],
        ),
    ],
)
def test_head_hunter_employers_parametrize(result, expected):
    assert head_hunter_employers_information(result) == expected


@pytest.mark.parametrize(
    "result, expected",
    [
        ({"from": 10000, "to": 100000}, "от 10000 до 100000"),
        ({"from": None, "to": 100000}, "до 100000"),
        ({"from": 100000, "to": None}, "от 100000"),
        ({"from": None, "to": None}, "Зарплата не указана"),
        ({"from": 160000, "to": 160000}, 160000),
    ],
)
def test_salary(result, expected):
    assert salary(result) == expected


@pytest.mark.parametrize(
    "result, expected",
    [
        ({"from": 10000, "to": 100000}, (10000, 100000)),
        ({"from": None, "to": 100000}, (0, 100000)),
        ({"from": 100000, "to": None}, (100000, 0)),
        ({"from": None, "to": None}, (0, 0)),
        ({}, (0, 0)),
    ],
)
def test_database_salary(result, expected):
    assert database_salary(result) == expected


@pytest.mark.parametrize(
    "result, expected",
    [
        (
            [
                {
                    "id": "119206435",
                    "name": "Менеджер в отдел закупок / Оператор базы 1с",
                    "area": {"id": "160", "name": "Алматы", "url": "https://api.hh.ru/areas/160"},
                    "salary": {"from": 260000, "to": None, "currency": "KZT", "gross": False},
                    "alternate_url": "https://hh.ru/vacancy/119206435",
                    "employer": {"id": "3643187"},
                    "experience": {"id": "between1And3", "name": "От 1 года до 3 лет"},
                }
            ],
            [
                {
                    "vacancy_id": "119206435",
                    "name": "Менеджер в отдел закупок / Оператор базы 1с",
                    "area": "Алматы",
                    "experience": "От 1 года до 3 лет",
                    "salary_from": 260000,
                    "salary_to": 0,
                    "currency": "KZT",
                    "alternate_url": "https://hh.ru/vacancy/119206435",
                    "employer_id": "3643187",
                }
            ],
        ),
        (
            [
                {
                    "id": "111111",
                    "name": "Разработчик",
                    "area": {"id": "160", "name": "Москва", "url": "https://api.hh.ru/areas/160"},
                    "salary": {"from": None, "to": None, "currency": "KZT", "gross": False},
                    "alternate_url": None,
                    "employer": {"id": "36363636"},
                    "experience": {"id": "between1And3", "name": None},
                }
            ],
            [
                {
                    "vacancy_id": "111111",
                    "name": "Разработчик",
                    "area": "Москва",
                    "experience": "Без опыта",
                    "salary_from": 0,
                    "salary_to": 0,
                    "currency": "Не указано",
                    "alternate_url": "Ссылка отсутствует",
                    "employer_id": "36363636",
                }
            ],
        ),
    ],
)
def test_head_hunter_vacancies_information(result, expected):
    assert head_hunter_vacancies_information(result) == expected


def test_get_companies_and_vacancies_count_parser():

    res = [
        {"employer": "Самолет плюс", "vacancy_counter": 10},
        {"employer": "Фулфилмент", "vacancy_counter": 11},
        {"employer": "Завод", "vacancy_counter": 31},
        {"employer": "Драйвер", "vacancy_counter": 1},
    ]
    exc = (
        "1. Работодатель: Самолет плюс, Количество вакансий: 10\n--___--___\n"
        "2. Работодатель: Фулфилмент, Количество вакансий: 11\n--___--___\n"
        "3. Работодатель: Завод, Количество вакансий: 31\n--___--___\n"
        "4. Работодатель: Драйвер, Количество вакансий: 1\n--___--___\n"
    )

    assert get_companies_and_vacancies_count_parser(res) == exc


def test_all_vacancies_parser():
    res = [
        {"employer": "Самолет плюс", "vacancy": "Брокер", "salary": 200000, "currency": "RUR", "url": "2121312"},
        {"employer": "Драйвер", "vacancy": "Перегонщик", "salary": "от 10 до 29", "currency": "UZS", "url": "11111"},
        {"employer": "Завод", "vacancy": "Менеджер", "salary": "от 150", "currency": "Rzt", "url": "hh"},
        {"employer": "Студия21", "vacancy": "Оператор", "salary": "до 190", "currency": "НЕту", "url": "Ссылка"},
    ]
    exc = (
        "1. Работодатель: Самолет плюс, Название вакансии: Брокер, Зарплата: 200000, "
        "Валюта: RUR, Ссылка на вакансию: 2121312\n--___--___\n"
        "2. Работодатель: Драйвер, Название вакансии: Перегонщик, Зарплата: от 10 до 29, "
        "Валюта: UZS, Ссылка на вакансию: 11111\n--___--___\n"
        "3. Работодатель: Завод, Название вакансии: Менеджер, Зарплата: от 150, Валюта: "
        "Rzt, Ссылка на вакансию: hh\n--___--___\n"
        "4. Работодатель: Студия21, Название вакансии: Оператор, Зарплата: до 190, "
        "Валюта: НЕту, Ссылка на вакансию: Ссылка\n--___--___\n"
    )
    assert get_all_vacancies_parser(res) == exc


def test_get_vacancies_keyword_or_high_salary_parser():
    res = [
        {
            "id": "291",
            "vacancy_id": "1111",
            "vacancy": "developer",
            "area": "Mocow",
            "experience": "from 1 to 3 years",
            "salary": 200000,
            "currency": "RUR",
            "url": "https",
            "employer_id": 123214,
        },
        {
            "id": "19",
            "vacancy_id": "2212",
            "vacancy": "operator",
            "area": "Saint-Petersburg",
            "experience": "no experience",
            "salary": 100000,
            "currency": "RUR",
            "url": "//:",
            "employer_id": 43124314,
        },
        {
            "id": "13",
            "vacancy_id": "3432",
            "vacancy": "manager",
            "area": "Sochi",
            "experience": "no experience",
            "salary": 122232,
            "currency": "RUR",
            "url": "api.hh.ru/",
            "employer_id": 413431332,
        },
        {
            "id": "661",
            "vacancy_id": "4324",
            "vacancy": "stoner",
            "area": "Moscow",
            "experience": "from 3 to 6 years",
            "salary": 1000000,
            "currency": "USD",
            "url": "vacancies",
            "employer_id": 12312234,
        },
    ]
    exc = (
        "291. Номер вакансии: 1111, Название вакансии: developer, Местоположение: "
        "Mocow, Опыт работы: from 1 to 3 years, Зарплата: 200000, Валюта: RUR, Ссылка "
        "на вакансию: https, Номер работодателя: 123214\n--___--___\n"
        "19. Номер вакансии: 2212, Название вакансии: operator, Местоположение: "
        "Saint-Petersburg, Опыт работы: no experience, Зарплата: 100000, Валюта: RUR, "
        "Ссылка на вакансию: //:, Номер работодателя: 43124314\n--___--___\n"
        "13. Номер вакансии: 3432, Название вакансии: manager, Местоположение: Sochi, "
        "Опыт работы: no experience, Зарплата: 122232, Валюта: RUR, Ссылка на "
        "вакансию: api.hh.ru/, Номер работодателя: 413431332\n--___--___\n"
        "661. Номер вакансии: 4324, Название вакансии: stoner, Местоположение: "
        "Moscow, Опыт работы: from 3 to 6 years, Зарплата: 1000000, Валюта: USD, "
        "Ссылка на вакансию: vacancies, Номер работодателя: 12312234\n--___--___\n"
    )
    assert get_vacancies_keyword_or_high_salary_parser(res) == exc
