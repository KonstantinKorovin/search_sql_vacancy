from abc import ABC, abstractmethod

import requests


class AbstractHH(ABC):
    """
    Класс представитель HH
    """

    @abstractmethod
    def employers_data(self) -> list:
        pass

    @abstractmethod
    def vacancies_data(self, data: list) -> list:
        pass


class HH(AbstractHH):
    """
    Класс получения информации с платформы headhunter
    """

    def __init__(self, keyword=None, page=0, per_page=10, max_employers=50):
        self.__url_employers = "https://api.hh.ru/employers?only_with_vacancies=True"
        self.__url_vacancies = "https://api.hh.ru/vacancies"
        self.__page = page
        self.__per_page = per_page
        self.__data_employers = []
        self.__data_vacancies = []
        self.__params = {"text": keyword, "page": page, "per_page": per_page}
        self.__max_employers = max_employers
        self.__ids = set()

    @staticmethod
    def __connect_api(url: str, params: dict | None = None) -> dict | list:
        """
        Подключение к API
        """
        try:
            response = requests.get(url=url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            print(f"Ошибка подключения к API {url}: {error}")
            return []

    def employers_data(self) -> list:
        """
        Получение стека работодателей
        """
        while True:
            data = self.__connect_api(url=self.__url_employers, params=self.__params)
            if (
                not data
                or "items" not in data
                or self.__page >= data.get("pages", 0)
                or len(self.__data_employers) >= self.__max_employers
            ):
                break
            for item in data["items"]:
                if item["id"] not in self.__ids:
                    self.__data_employers.append(item)
                    self.__ids.add(item["id"])
            self.__page += 1
            self.__params["page"] = self.__page

        return self.__data_employers

    def vacancies_data(self, data: list) -> list:
        """
        Получение стека вакансий
        """
        for employee in data:
            employer_id = employee["id"]
            page_vacancies = 0
            per_page = 100
            params_vacancies = {"employer_id": employer_id, "page": page_vacancies, "per_page": per_page}

            while True:
                data = self.__connect_api(url=self.__url_vacancies, params=params_vacancies)

                if not data or not data["items"] or page_vacancies >= data.get("pages", 0):
                    break
                else:
                    self.__data_vacancies.extend(data["items"])
                    page_vacancies += 1
                    params_vacancies["page"] = page_vacancies

        return self.__data_vacancies
