import unittest
from unittest.mock import MagicMock, patch

from src.database_manager import DBManager


class TestDBManagerMethods(unittest.TestCase):
    """
    Кейсы для DBManager
    """

    @patch("src.database_manager.psycopg2.connect")
    def test_get_companies_and_vacancies_count(self, mock_connect):

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = None
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        returned_data = [("Company1", 5), ("Company2", 3)]
        mock_cursor.fetchall.return_value = returned_data

        db_name = "test_db"
        params = {"user": "test_user", "password": "test_pass", "host": "localhost"}
        db_manager = DBManager(db_name, params)

        result = db_manager.get_companies_and_vacancies_count()

        expected_query = """
                    SELECT company_name,
                    COUNT(vacancy_name)
                    FROM employers
                    LEFT JOIN vacancies
                    USING (employer_id)
                    GROUP BY company_name
                    """
        mock_cursor.execute.assert_called_once_with(expected_query)

        self.assertEqual(
            result,
            [
                {"employer": "Company1", "vacancy_counter": 5},
                {"employer": "Company2", "vacancy_counter": 3},
            ],
        )

        mock_conn.close.assert_called_once()

    @patch("src.database_manager.salary")
    @patch("src.database_manager.psycopg2.connect")
    def test_get_all_vacancies(self, mock_connect, mock_salary):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = None
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        returned_data = [
            ("Company1", "Vacancy1", 50000, 70000, "USD", "http://vacancy1.com"),
            ("Company2", "Vacancy2", 60000, 80000, "EUR", "http://vacancy2.com"),
        ]
        mock_cursor.fetchall.return_value = returned_data

        def salary_side_effect(sal_dict):
            avg = (sal_dict["from"] + sal_dict["to"]) / 2
            return str(avg)

        mock_salary.side_effect = salary_side_effect

        db_name = "test_db"
        params = {"user": "user", "password": "pass", "host": "localhost"}
        db_manager = DBManager(db_name, params)

        result = db_manager.get_all_vacancies()

        expected_query = """
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
        mock_cursor.execute.assert_called_once_with(expected_query)

        expected_result = [
            {
                "employer": "Company1",
                "vacancy": "Vacancy1",
                "salary": "60000.0",
                "currency": "USD",
                "url": "http://vacancy1.com",
            },
            {
                "employer": "Company2",
                "vacancy": "Vacancy2",
                "salary": "70000.0",
                "currency": "EUR",
                "url": "http://vacancy2.com",
            },
        ]
        self.assertEqual(result, expected_result)
        mock_conn.close.assert_called_once()

    @patch("src.database_manager.psycopg2.connect")
    def test_get_avg_salary(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = None

        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        mock_cursor.fetchall.return_value = [(70000,)]

        db_name = "test_db"
        params = {"user": "user", "password": "pass", "host": "localhost"}
        db_manager = DBManager(db_name, params)

        result = db_manager.get_avg_salary()

        expected_message = "Средняя зарплата по вакансиям хранящимся в базе данных: 70000.0"
        self.assertEqual(result, expected_message)
        mock_conn.close.assert_called_once()

    @patch("src.database_manager.salary")
    @patch("src.database_manager.psycopg2.connect")
    def test_get_vacancies_with_higher_salary(self, mock_connect, mock_salary):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = None

        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        returned_data = [
            (1, 101, "Vacancy1", "Area1", "No experience", 50000, 70000, "USD", "http://url1.com", 1001),
            (2, 202, "Vacancy2", "Area2", "Experience", 60000, 80000, "EUR", "http://url2.com", 1002),
        ]
        mock_cursor.fetchall.return_value = returned_data

        def salary_side_effect(sal_dict):
            avg = (sal_dict["from"] + sal_dict["to"]) / 2
            return str(avg)

        mock_salary.side_effect = salary_side_effect

        db_name = "test_db"
        params = {"user": "user", "password": "pass", "host": "localhost"}
        db_manager = DBManager(db_name, params)

        result = db_manager.get_vacancies_with_higher_salary()

        expected_result = [
            {
                "id": 1,
                "vacancy_id": 101,
                "vacancy": "Vacancy1",
                "area": "Area1",
                "experience": "No experience",
                "salary": "60000.0",
                "currency": "USD",
                "url": "http://url1.com",
                "employer_id": 1001,
            },
            {
                "id": 2,
                "vacancy_id": 202,
                "vacancy": "Vacancy2",
                "area": "Area2",
                "experience": "Experience",
                "salary": "70000.0",
                "currency": "EUR",
                "url": "http://url2.com",
                "employer_id": 1002,
            },
        ]
        self.assertEqual(result, expected_result)
        mock_conn.close.assert_called_once()

    @patch("src.database_manager.psycopg2.connect")
    def test_get_vacancies_with_keyword(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = None

        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        returned_data = [
            (1, 101, "DevOps Engineer", "Area1", "No experience", 50000, 70000, "USD", "http://url1.com", 1001),
            (2, 202, "Senior Developer", "Area2", "Experience", 60000, 80000, "EUR", "http://url2.com", 1002),
        ]
        mock_cursor.fetchall.return_value = returned_data

        db_name = "test_db"
        params = {"user": "user", "password": "pass", "host": "localhost"}
        db_manager = DBManager(db_name, params)

        keyword = "Developer"
        result = db_manager.get_vacancies_with_keyword(keyword)

        expected_query_part = f"LIKE '%{keyword}%'"
        args, _ = mock_cursor.execute.call_args
        query_executed = args[0]
        self.assertIn(expected_query_part, query_executed)

        expected_result = []
        for row in returned_data:
            expected_result.append(
                {
                    "id": row[0],
                    "vacancy_id": row[1],
                    "vacancy": row[2],
                    "area": row[3],
                    "experience": row[4],
                    "salary": f"от {row[5]} до {row[6]}",
                    "currency": row[7],
                    "url": row[8],
                    "employer_id": row[9],
                }
            )
        self.assertEqual(result, expected_result)
        mock_conn.close.assert_called_once()
