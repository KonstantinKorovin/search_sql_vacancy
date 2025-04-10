from abc import ABC, abstractmethod

import psycopg2

from src.utils import salary


class BaseDBManager:
    """
    Класс представитель DBManager
    """

    @abstractmethod
    def get_companies_and_vacancies_count(self) -> list:
        pass

    @abstractmethod
    def get_all_vacancies(self) -> list:
        pass

    @abstractmethod
    def get_avg_salary(self) -> list | str:
        pass

    @abstractmethod
    def get_vacancies_with_higher_salary(self) -> list:
        pass

    @abstractmethod
    def get_vacancies_with_keyword(self, word: str) -> list:
        pass


class DBManager(ABC):
    """
    Класс для выгрузки информации из базы данных
    """

    def __init__(self, name, params):
        self.__name = name
        self.__params = params
        self.__conn = psycopg2.connect(dbname=self.__name, **self.__params)

    def get_companies_and_vacancies_count(self) -> list:
        """
        Получение всех компаний и количество их вакансий
        """
        try:
            with self.__conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT company_name,
                    COUNT(vacancy_name)
                    FROM employers
                    LEFT JOIN vacancies
                    USING (employer_id)
                    GROUP BY company_name
                    """
                )
                data = cur.fetchall()
                stacks = []

                for stack in data:
                    stack_dict = {"employer": stack[0], "vacancy_counter": stack[1]}
                    stacks.append(stack_dict)
                return stacks
        except psycopg2.Error as e:
            print(f"Ошибка: {e}")
        finally:
            self.__conn.close()

    def get_all_vacancies(self) -> list:
        """
        Получение всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию
        """
        try:
            with self.__conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT company_name,
                    vacancy_name,
                    salary_from,
                    salary_to,
                    currency,
                    url
                    FROM employers
                    LEFT JOIN vacancies
                    USING (employer_id)
                    """
                )
                data = cur.fetchall()
                stacks = []
                for stack in data:
                    stack_dict = {
                        "employer": stack[0],
                        "vacancy": stack[1],
                        "salary": salary({"from": stack[2], "to": stack[3]}),
                        "currency": stack[4],
                        "url": stack[5],
                    }
                    stacks.append(stack_dict)
                return stacks
        except psycopg2.Error as e:
            print(f"Ошибка: {e}")
            return []
        finally:
            self.__conn.close()

    def get_avg_salary(self) -> list | str:
        """
        Получение средней зарплаты по всем вакансиям
        """
        try:
            with self.__conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                    AVG(salary_from + salary_to) / 2
                    FROM vacancies
                    """
                )
                data = cur.fetchall()
                avg = float(data[0][0])
                return f"Средняя зарплата по вакансиям хранящимся в базе данных: {round(avg, 2)}"
        except psycopg2.Error as e:
            print(f"Ошибка: {e}")
            return []
        finally:
            self.__conn.close()

    def get_vacancies_with_higher_salary(self) -> list:
        """
        Получение вакансий с зарплатой выше среднего значения
        """
        try:
            with self.__conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM vacancies
                    WHERE (salary_from + salary_to) / 2 >
                    (SELECT AVG((salary_from + salary_to) / 2) FROM vacancies)
                    """
                )
                data = cur.fetchall()
                stacks = []
                for stack in data:
                    stack_dict = {
                        "id": stack[0],
                        "vacancy_id": stack[1],
                        "vacancy": stack[2],
                        "area": stack[3],
                        "experience": stack[4],
                        "salary": salary({"from": stack[5], "to": stack[6]}),
                        "currency": stack[7],
                        "url": stack[8],
                        "employer_id": stack[9],
                    }
                    stacks.append(stack_dict)
                return stacks

        except psycopg2.Error as e:
            print(f"Ошибка: {e}!")
            return []
        finally:
            self.__conn.close()

    def get_vacancies_with_keyword(self, word: str) -> list:
        """
        получение списка всех вакансий, в названии которых содержатся переданные в метод слова
        """
        try:
            with self.__conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT * FROM
                    vacancies
                    WHERE vacancy_name LIKE '%{word}%'
                    """
                )
                data = cur.fetchall()
                stacks = []
                for stack in data:
                    stack_dict = {
                        "id": stack[0],
                        "vacancy_id": stack[1],
                        "vacancy": stack[2],
                        "area": stack[3],
                        "experience": stack[4],
                        "salary": salary({"from": stack[5], "to": stack[6]}),
                        "currency": stack[7],
                        "url": stack[8],
                        "employer_id": stack[9],
                    }
                    stacks.append(stack_dict)
                return stacks
        except psycopg2.Error as e:
            print(f"Ошибка: {e}")
            return []
        finally:
            self.__conn.close()
