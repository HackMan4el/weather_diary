"""
tests.py — Unit tests for Weather Diary logic.

Run:  python -m pytest tests.py -v
  or: python tests.py
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from logic import validate_date, validate_temperature, load_records, save_records, filter_records, DATA_FILE

TEST_FILE = "test_weather_data.json"


class TestValidateDate(unittest.TestCase):

    # Positive
    def test_valid_date_standard(self):
        self.assertTrue(validate_date("15.06.2024"))

    def test_valid_date_leading_zeros(self):
        self.assertTrue(validate_date("01.01.2000"))

    def test_valid_date_with_spaces(self):
        self.assertTrue(validate_date("  10.10.2023  "))

    def test_valid_date_today_format(self):
        self.assertTrue(validate_date("03.05.2025"))

    # Negative
    def test_invalid_date_wrong_separator(self):
        self.assertFalse(validate_date("15-06-2024"))

    def test_invalid_date_wrong_format_ymd(self):
        self.assertFalse(validate_date("2024.06.15"))

    def test_invalid_date_text(self):
        self.assertFalse(validate_date("не дата"))

    def test_invalid_date_empty(self):
        self.assertFalse(validate_date(""))

    def test_invalid_date_partial(self):
        self.assertFalse(validate_date("15.06"))

    # Boundary
    def test_boundary_last_day_of_year(self):
        self.assertTrue(validate_date("31.12.2023"))

    def test_boundary_first_day_of_year(self):
        self.assertTrue(validate_date("01.01.2023"))

    def test_boundary_invalid_day_32(self):
        self.assertFalse(validate_date("32.01.2023"))

    def test_boundary_invalid_month_13(self):
        self.assertFalse(validate_date("01.13.2023"))

    def test_boundary_feb_29_leap_year(self):
        self.assertTrue(validate_date("29.02.2024"))

    def test_boundary_feb_29_non_leap_year(self):
        self.assertFalse(validate_date("29.02.2023"))


class TestValidateTemperature(unittest.TestCase):

    # Positive
    def test_positive_integer(self):
        self.assertTrue(validate_temperature("25"))

    def test_negative_integer(self):
        self.assertTrue(validate_temperature("-10"))

    def test_float_positive(self):
        self.assertTrue(validate_temperature("23.5"))

    def test_float_negative(self):
        self.assertTrue(validate_temperature("-0.5"))

    def test_zero(self):
        self.assertTrue(validate_temperature("0"))

    def test_with_spaces(self):
        self.assertTrue(validate_temperature("  15  "))

    # Negative
    def test_empty_string(self):
        self.assertFalse(validate_temperature(""))

    def test_text_string(self):
        self.assertFalse(validate_temperature("тепло"))

    def test_mixed_string(self):
        self.assertFalse(validate_temperature("25C"))

    # Boundary
    def test_boundary_very_cold(self):
        self.assertTrue(validate_temperature("-273.15"))

    def test_boundary_plus_sign(self):
        self.assertTrue(validate_temperature("+5"))


class TestSaveLoadRecords(unittest.TestCase):

    def setUp(self):
        import logic
        self._orig = logic.DATA_FILE
        logic.DATA_FILE = TEST_FILE

    def tearDown(self):
        import logic
        logic.DATA_FILE = self._orig
        if os.path.exists(TEST_FILE):
            os.remove(TEST_FILE)

    # Positive
    def test_save_and_load_single_record(self):
        import logic
        record = {"date": "01.01.2024", "temperature": -5.0, "precipitation": "Нет", "description": "Ясно"}
        logic.save_records([record])
        self.assertEqual(logic.load_records(), [record])

    def test_save_and_load_multiple_records(self):
        import logic
        records = [
            {"date": "01.01.2024", "temperature": -5.0, "precipitation": "Нет", "description": "Ясно"},
            {"date": "02.01.2024", "temperature": 3.0, "precipitation": "Да", "description": "Снег"},
        ]
        logic.save_records(records)
        loaded = logic.load_records()
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[1]["description"], "Снег")

    # Boundary / edge
    def test_load_returns_empty_list_when_file_missing(self):
        import logic
        if os.path.exists(TEST_FILE):
            os.remove(TEST_FILE)
        self.assertEqual(logic.load_records(), [])

    def test_save_empty_list(self):
        import logic
        logic.save_records([])
        self.assertEqual(logic.load_records(), [])

    def test_json_file_is_valid_after_save(self):
        import logic
        records = [{"date": "10.05.2025", "temperature": 20.0, "precipitation": "Нет", "description": "Солнечно"}]
        logic.save_records(records)
        with open(TEST_FILE, "r", encoding="utf-8") as f:
            self.assertEqual(json.load(f), records)

    def test_unicode_description_preserved(self):
        import logic
        records = [{"date": "01.06.2024", "temperature": 18.0, "precipitation": "Нет", "description": "Тепло ☀️"}]
        logic.save_records(records)
        self.assertEqual(logic.load_records()[0]["description"], "Тепло ☀️")


class TestFilterRecords(unittest.TestCase):

    def setUp(self):
        self.records = [
            {"date": "01.01.2024", "temperature": -10.0, "precipitation": "Нет", "description": "Мороз"},
            {"date": "15.06.2024", "temperature": 25.0, "precipitation": "Нет", "description": "Жара"},
            {"date": "15.06.2024", "temperature": 18.0, "precipitation": "Да", "description": "Дождь"},
            {"date": "10.03.2024", "temperature": 5.0,  "precipitation": "Нет", "description": "Весна"},
        ]

    def test_filter_by_date_match(self):
        result = filter_records(self.records, date_filter="15.06.2024")
        self.assertEqual(len(result), 2)

    def test_filter_by_date_no_match(self):
        result = filter_records(self.records, date_filter="01.12.2099")
        self.assertEqual(result, [])

    def test_filter_by_temp_above_10(self):
        result = filter_records(self.records, temp_filter="10")
        self.assertEqual(len(result), 2)
        self.assertTrue(all(r["temperature"] > 10 for r in result))

    def test_filter_combined(self):
        result = filter_records(self.records, date_filter="15.06.2024", temp_filter="20")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["description"], "Жара")

    def test_no_filters_returns_all(self):
        result = filter_records(self.records)
        self.assertEqual(len(result), 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
