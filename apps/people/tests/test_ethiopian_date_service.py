from apps.people.services import EthiopianDateService
from datetime import date
import pytest

def test_validate_ethiopian_date_str():
    assert EthiopianDateService.validate_ethiopian_date_str("2016-01-01")
    assert not EthiopianDateService.validate_ethiopian_date_str("2016-13-01")

def test_ethiopian_to_gregorian():
    greg = EthiopianDateService.ethiopian_to_gregorian("2016-01-01")
    assert isinstance(greg, date)
    assert greg.year > 2020  # Should be a recent year

def test_gregorian_to_ethiopian():
    eth = EthiopianDateService.gregorian_to_ethiopian(date(2024, 9, 11))
    assert isinstance(eth, str)
    y, m, d = map(int, eth.split("-"))
    assert 1 <= m <= 13
