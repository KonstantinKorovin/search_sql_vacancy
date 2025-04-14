import datetime


def head_hunter_employers_information(data: list) -> list:
    """
    Форматирование информации о работодателях
    """
    employers_list = []
    for stack in data:
        employers_dict = {
            "employer_id": stack.get("id"),
            "name": stack.get("name"),
            "url": stack.get("alternate_url"),
            "open_vacancies": stack.get("open_vacancies"),
        }
        employers_list.append(employers_dict)

    return employers_list


def salary(zn_salary: dict) -> str:
    """
    Форматирование зарплаты
    """
    if zn_salary["from"] and zn_salary["to"]:
        if zn_salary["from"] == zn_salary["to"]:
            return zn_salary["from"]
        else:
            return f"от {zn_salary["from"]} до {zn_salary["to"]}"
    elif zn_salary["from"] and not zn_salary["to"]:
        return f"от {zn_salary["from"]}"
    elif not zn_salary["from"] and zn_salary["to"]:
        return f"до {zn_salary["to"]}"
    else:
        return "Зарплата не указана"


def database_salary(zn_salary: dict) -> tuple:
    """
    Форматирование зарплаты для значения таблиц
    """
    if not zn_salary or zn_salary is None:
        return 0, 0
    elif zn_salary["from"] and zn_salary["to"]:
        return int(zn_salary["from"]), int(zn_salary["to"])
    elif not zn_salary["from"] and zn_salary["to"]:
        return 0, int(zn_salary["to"])
    elif zn_salary["from"] and not zn_salary["to"]:
        return int(zn_salary["from"]), 0
    else:
        return 0, 0


def head_hunter_vacancies_information(data: list) -> list:
    """
    Форматирование ответа о вакансиях
    """
    vacancies_list = []
    for stack in data:
        salary_ = database_salary(stack.get("salary", {}))
        area = stack.get("area", {}).get("name", "Не указано")
        experience = stack.get("experience", {}).get("name") if stack["experience"]["name"] else "Без опыта"
        alternate_url = stack.get("alternate_url") if stack.get("alternate_url") else "Ссылка отсутствует"
        currency = (
            stack.get("salary", {}).get("currency")
            if stack["salary"]["currency"] and salary_ != (0, 0)
            else "Не указано"
        )

        vacancies_dict = {
            "vacancy_id": stack.get("id"),
            "name": stack.get("name"),
            "area": area,
            "experience": experience,
            "salary_from": salary_[0],
            "salary_to": salary_[1],
            "currency": currency,
            "alternate_url": alternate_url,
            "employer_id": stack.get("employer", {}).get("id"),
        }
        vacancies_list.append(vacancies_dict)

    return vacancies_list


def greeting() -> str:
    """
    Приветствие юзера
    """
    date_time = datetime.datetime.now().time()
    if datetime.time(5, 0, 0) <= date_time < datetime.time(11, 0, 0):
        return "Доброе утро!"
    elif datetime.time(11, 0, 0) <= date_time < datetime.time(17, 0, 0):
        return "Добрый день!"
    elif datetime.time(17, 0, 0) <= date_time < datetime.time(23, 0, 0):
        return "Добрый вечер!"
    else:
        return "Доброй ночи!"


def get_companies_and_vacancies_count_parser(data: list) -> str:
    """
    Приведение коллекции к пользовательскому формату
    """
    employer_id = 1
    employer_str = ""
    for stack in data:
        employer_str += (
            f"{employer_id}. "
            f"Работодатель: "
            f"{stack["employer"]}, "
            f"Количество вакансий: "
            f"{stack["vacancy_counter"]}"
            f"\n--___--___\n"
        )
        employer_id += 1
    return employer_str


def get_all_vacancies_parser(data: list) -> str:
    """
    Приведение коллекции к пользовательскому формату
    """
    employer_id = 1
    employer_str = ""
    for stack in data:
        employer_str += (
            f"{employer_id}. "
            f"Работодатель: "
            f"{stack["employer"]}, "
            f"Название вакансии: "
            f"{stack["vacancy"]}, "
            f"Зарплата: "
            f"{stack["salary"]}, "
            f"Валюта: "
            f"{stack["currency"]}, "
            f"Ссылка на вакансию: "
            f"{stack["url"]}"
            f"\n--___--___\n"
        )
        employer_id += 1
    return employer_str


def get_vacancies_keyword_or_high_salary_parser(data: list) -> str:
    """
    Приведение коллекции к пользовательскому формату
    """
    employer_str = ""
    for stack in data:
        employer_str += (
            f"{stack["id"]}. "
            f"Номер вакансии: "
            f"{stack["vacancy_id"]}, "
            f"Название вакансии: "
            f"{stack["vacancy"]}, "
            f"Местоположение: "
            f"{stack["area"]}, "
            f"Опыт работы: "
            f"{stack["experience"]}, "
            f"Зарплата: "
            f"{stack["salary"]}, "
            f"Валюта: "
            f"{stack["currency"]}, "
            f"Ссылка на вакансию: "
            f"{stack["url"]}, "
            f"Номер работодателя: "
            f"{stack["employer_id"]}"
            f"\n--___--___\n"
        )
    return employer_str
