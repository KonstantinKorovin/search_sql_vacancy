import psycopg2

from src.utils import (
    head_hunter_employers_information,
    head_hunter_vacancies_information,
)


def create_database(name, params: dict) -> str | list:
    """
    Создатель БД
    """
    conn = psycopg2.connect(database="postgres", **params)
    cur = conn.cursor()

    try:
        conn.autocommit = True
        cur.execute(f"DROP DATABASE IF EXISTS {name}")
        cur.execute(f"CREATE DATABASE {name}")
        cur.close()
        conn.close()
        return f"База данных {name} успешно создана или уже существует!"
    except psycopg2.Error as e:
        cur.close()
        conn.close()
        raise e


def create_table_to_database(name, params: dict) -> str | list:
    """
    Создание таблиц в БД
    """
    conn = psycopg2.connect(database=name, **params)
    cur = conn.cursor()

    try:
        cur.execute("""DROP TABLE IF EXISTS vacancies""")
        cur.execute("""DROP TABLE IF EXISTS employers""")

        cur.execute(
            """CREATE TABLE employers (
            id SERIAL PRIMARY KEY,
            employer_id INT UNIQUE NOT NULL,
            company_name VARCHAR(255) NOT NULL,
            employer_url VARCHAR(255) NOT NULL,
            open_vacancies INT NOT NULL
            )"""
        )

        cur.execute(
            """CREATE TABLE vacancies (
            id SERIAL PRIMARY KEY,
            vacancy_id INT UNIQUE NOT NULL,
            vacancy_name VARCHAR(105) NOT NULL,
            area VARCHAR(55) NOT NULL,
            experience VARCHAR(55) NOT NULL,
            salary_from INT NOT NULL,
            salary_to INT NOT NULL,
            currency VARCHAR(25) NOT NULL,
            url VARCHAR(255) NOT NULL,
            employer_id INT NOT NULL,
            FOREIGN KEY (employer_id) REFERENCES employers (employer_id)
            )"""
        )
        conn.commit()
        cur.close()
        conn.close()
        return "Таблицы созданы!"
    except psycopg2.Error as e:
        cur.close()
        conn.close()
        raise e


def save_data_to_database(name, params: dict, employers, vacancies) -> str | list:
    """
    Заполнение таблиц
    """
    conn = psycopg2.connect(database=name, **params)
    employers_data = head_hunter_employers_information(employers)
    vacancies_data = head_hunter_vacancies_information(vacancies)

    with conn.cursor() as cursor:
        try:
            for stack in employers_data:
                cursor.execute(
                    """INSERT INTO employers (employer_id, company_name, employer_url, open_vacancies)
                    VALUES (%s, %s, %s, %s)""",
                    (stack["employer_id"], stack["name"], stack["url"], stack["open_vacancies"]),
                )
            print("Запись в таблицу employers...")
            conn.commit()

            cursor.execute("SELECT employer_id FROM employers")
            existing_employer_ids = set(str(row[0]) for row in cursor.fetchall())
            valid_vacancies = [v for v in vacancies_data if v["employer_id"] in existing_employer_ids]

            for stack in valid_vacancies:
                cursor.execute(
                    """INSERT INTO vacancies (
                    vacancy_id, vacancy_name, area, experience, salary_from, salary_to, currency, url, employer_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        stack["vacancy_id"],
                        stack["name"],
                        stack["area"],
                        stack["experience"],
                        stack["salary_from"],
                        stack["salary_to"],
                        stack["currency"],
                        stack["alternate_url"],
                        stack["employer_id"],
                    ),
                )
            print("Запись в таблицу vacancies...")
            conn.commit()
            conn.close()
            return "Таблицы заполнены!"
        except psycopg2.Error as e:
            conn.rollback()
            conn.close()
            raise e
