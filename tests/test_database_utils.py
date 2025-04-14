import unittest
from unittest.mock import MagicMock, call, patch

from src.database_utils import (
    create_database,
    create_table_to_database,
    save_data_to_database,
)


class TestDBFunctions(unittest.TestCase):
    """
    Кейсы для database_utils
    """

    @patch("src.database_utils.psycopg2.connect")
    def test_create_database(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        db_name = "test_db"
        params = {"user": "test_user", "password": "test_pass", "host": "localhost"}
        result = create_database(db_name, params)
        mock_connect.assert_called_once_with(database="postgres", **params)
        expected_calls = [call(f"DROP DATABASE IF EXISTS {db_name}"), call(f"CREATE DATABASE {db_name}")]
        mock_cursor.execute.assert_has_calls(expected_calls)
        self.assertEqual(mock_cursor.execute.call_count, 2)
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
        expected_message = f"База данных {db_name} успешно создана или уже существует!"
        self.assertEqual(result, expected_message)

    @patch("src.database_utils.psycopg2.connect")
    def test_create_table_to_database(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        db_name = "test_db"
        params = {"user": "test_user", "password": "test_pass", "host": "localhost"}
        result = create_table_to_database(db_name, params)
        mock_connect.assert_called_once_with(database=db_name, **params)
        expected_calls = [
            call("DROP TABLE IF EXISTS vacancies"),
            call("DROP TABLE IF EXISTS employers"),
            call(
                """CREATE TABLE employers (
            id SERIAL PRIMARY KEY,
            employer_id INT UNIQUE NOT NULL,
            company_name VARCHAR(255) NOT NULL,
            employer_url VARCHAR(255) NOT NULL,
            open_vacancies INT NOT NULL
            )"""
            ),
            call(
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
            ),
        ]
        mock_cursor.execute.assert_has_calls(expected_calls, any_order=False)
        self.assertEqual(mock_cursor.execute.call_count, 4)
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
        self.assertEqual(result, "Таблицы созданы!")

    @patch("src.database_utils.head_hunter_employers_information")
    @patch("src.database_utils.head_hunter_vacancies_information")
    @patch("src.database_utils.psycopg2.connect")
    def test_save_data_to_database(self, mock_connect, mock_vacancies_info, mock_employers_info):
        employers_data = [
            {"employer_id": 101, "name": "Компания 1", "url": "http://comp1.ru", "open_vacancies": 10},
            {"employer_id": 202, "name": "Компания 2", "url": "http://comp2.ru", "open_vacancies": 5},
        ]

        vacancies_data = [
            {
                "vacancy_id": 1001,
                "name": "Вакансия A",
                "area": "Москва",
                "experience": "Не требуется",
                "salary_from": 50000,
                "salary_to": 70000,
                "currency": "RUR",
                "alternate_url": "http://vacancyA.ru",
                "employer_id": 101,
            },
            {
                "vacancy_id": 2002,
                "name": "Вакансия B",
                "area": "Санкт-Петербург",
                "experience": "Опыт работы",
                "salary_from": 60000,
                "salary_to": 80000,
                "currency": "RUR",
                "alternate_url": "http://vacancyB.ru",
                "employer_id": 202,
            },
            {
                "vacancy_id": 3003,
                "name": "Вакансия C",
                "area": "Новосибирск",
                "experience": "Не требуется",
                "salary_from": 40000,
                "salary_to": 50000,
                "currency": "RUR",
                "alternate_url": "http://vacancyC.ru",
                "employer_id": 999,
            },
        ]
        mock_employers_info.return_value = employers_data
        mock_vacancies_info.return_value = vacancies_data
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = None
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        db_name = "test_db"
        params = {"user": "test_user", "password": "test_pass", "host": "localhost"}
        result = save_data_to_database(db_name, params, employers=employers_data, vacancies=vacancies_data)
        mock_connect.assert_called_once_with(database=db_name, **params)
        self.assertGreaterEqual(mock_conn.commit.call_count, 2)
        mock_conn.close.assert_called_once()
        self.assertEqual(result, "Таблицы заполнены!")
