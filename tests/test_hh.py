import unittest
from unittest.mock import Mock, patch

from src.hh import HH


class TestApiHeadHunter(unittest.TestCase):
    """
    Кейсы для класса HH
    """

    def test_employers_data_error(self):
        with patch("requests.get") as mock_get:
            mock_employers = Mock()
            mock_employers.json.return_value = '{"error": "404"}'
            mock_get.return_value = mock_employers

            result = HH().employers_data()
            self.assertEqual(result, [])

    def test_employers_data(self):
        with patch("requests.get") as mock_get:
            mock_employers = mock_get.return_value
            mock_employers.status_code = 200
            mock_employers.json.return_value = {
                "items": [
                    {"id": 1, "employer": "Самолет плюс", "vacancy": "Менеджер"},
                    {"id": 2, "employer": "Драйвер", "vacancy": "Перегонщик"},
                ],
                "pages": 2,
            }

            mock_get.return_value = mock_employers
            result = HH().employers_data()
            excepted = [
                {"id": 1, "employer": "Самолет плюс", "vacancy": "Менеджер"},
                {"id": 2, "employer": "Драйвер", "vacancy": "Перегонщик"},
            ]
            self.assertEqual(result, excepted)

    def test_vacancies_data_one(self):
        with patch("requests.get") as mock_get:

            data = [{"id": "1"}]

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "items": [
                    {
                        "id": "100",
                        "name": "Менеджер",
                        "employer": {"id": "1", "name": "Самолет плюс"},
                        "salary": {"from": 200000, "to": 200000, "currency": "RUR"},
                    },
                    {
                        "id": "200",
                        "name": "Перегонщик",
                        "employer": {"id": "1", "name": "Драйвер"},
                        "salary": {"from": 80000, "to": 100000, "currency": "RUR"},
                    },
                ],
                "pages": 1,
                "page": 0,
            }
            mock_get.return_value = mock_response

            hh = HH()
            result = hh.vacancies_data(data)

            expected = [
                {
                    "id": "100",
                    "name": "Менеджер",
                    "employer": {"id": "1", "name": "Самолет плюс"},
                    "salary": {"from": 200000, "to": 200000, "currency": "RUR"},
                },
                {
                    "id": "200",
                    "name": "Перегонщик",
                    "employer": {"id": "1", "name": "Драйвер"},
                    "salary": {"from": 80000, "to": 100000, "currency": "RUR"},
                },
            ]

            self.assertEqual(result, expected)

    def test_vacancies_data_two(self):
        with patch("requests.get") as mock_get:

            data = [{"id": "2"}]

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "items": [
                    {
                        "id": "100",
                        "name": "Менеджер",
                        "employer": {"id": "2", "name": "Самолет плюс"},
                        "salary": {"from": 200000, "to": 200000, "currency": "RUR"},
                    },
                    {
                        "id": "200",
                        "name": "Перегонщик",
                        "employer": {"id": "2", "name": "Драйвер"},
                        "salary": {"from": 80000, "to": 100000, "currency": "RUR"},
                    },
                ],
                "pages": 1,
                "page": 0,
            }
            mock_get.return_value = mock_response

            hh = HH()
            result = hh.vacancies_data(data)

            expected = [
                {
                    "id": "100",
                    "name": "Менеджер",
                    "employer": {"id": "2", "name": "Самолет плюс"},
                    "salary": {"from": 200000, "to": 200000, "currency": "RUR"},
                },
                {
                    "id": "200",
                    "name": "Перегонщик",
                    "employer": {"id": "2", "name": "Драйвер"},
                    "salary": {"from": 80000, "to": 100000, "currency": "RUR"},
                },
            ]

            self.assertEqual(result, expected)
