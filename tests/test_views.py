import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.views import home_page


@pytest.fixture
def sample_transactions_df() -> pd.DataFrame:
    """Фикстура с тестовыми данными транзакций."""
    return pd.DataFrame({
        'Дата операции': [
            datetime(2023, 5, 1, 10, 30, 0),
            datetime(2023, 5, 5, 14, 20, 0),
            datetime(2023, 5, 10, 18, 45, 0),
            datetime(2023, 5, 15, 9, 15, 0),
            datetime(2023, 5, 20, 12, 10, 0)
        ],
        'Сумма операции': [-1500.50, -2300.75, -800.00, -4500.25, -1200.30],
        'Категория': ['Продукты', 'Рестораны', 'Транспорт', 'Продукты', 'Развлечения'],
        'Описание': ['Покупка в супермаркете', 'Ужин в ресторане',
                     'Оплата проезда', 'Покупка продуктов', 'Билеты в кино'],
        'Номер карты': ['1234567890123456', '1234567890123456',
                        '9876543210987654', '1234567890123456', '9876543210987654']
    })


@patch('src.utils.load_transactions')
@patch('src.utils.get_greeting_by_time')
def test_home_page_full_flow(
        mock_greeting: MagicMock,
        mock_load: MagicMock, sample_transactions_df: pd.DataFrame) -> None:
    mock_greeting.return_value = "Добрый день"
    mock_load.return_value = sample_transactions_df

    result_json = home_page('2023-05-20 14:30:00', sample_transactions_df)
    result = json.loads(result_json)

    assert result['greeting'] == "Добрый день"
    assert len(result['cards']) == 2

    card_3456 = next((card for card in result['cards'] if card['last_digits'] == '3456'), None)
    assert card_3456 is not None
    assert card_3456['total_spent'] == pytest.approx(8301.50, abs=0.01)
    assert card_3456['cashback'] == pytest.approx(83.02, abs=0.01)

    card_7654 = next((card for card in result['cards'] if card['last_digits'] == '7654'), None)
    assert card_7654 is not None
    assert card_7654['total_spent'] == pytest.approx(2000.30, abs=0.01)
    assert card_7654['cashback'] == pytest.approx(20.00, abs=0.01)

    assert len(result['top_transactions']) == 5
    assert result['top_transactions'][0]['amount'] == -4500.25


@patch('src.utils.load_transactions')
@patch('src.utils.get_greeting_by_time')
def test_home_page_empty_transactions(mock_greeting: MagicMock, mock_load: MagicMock) -> None:
    mock_greeting.return_value = "Доброе утро"
    empty_df = pd.DataFrame(columns=[
        'Дата операции', 'Сумма операции', 'Категория', 'Описание', 'Номер карты'
    ])
    mock_load.return_value = empty_df

    result_json = home_page('2023-05-20 09:00:00', empty_df)
    result = json.loads(result_json)

    assert result['greeting'] == "Доброе утро"
    assert result['cards'] == []
    assert result['top_transactions'] == []


@patch('src.utils.load_transactions')
@patch('src.utils.get_greeting_by_time')
def test_home_page_single_card(mock_greeting: MagicMock, mock_load: MagicMock) -> None:
    mock_greeting.return_value = "Добрый вечер"
    single_card_df = pd.DataFrame({
        'Дата операции': [datetime(2023, 5, 1)],
        'Сумма операции': [-1000.00],
        'Категория': ['Продукты'],
        'Описание': ['Покупка в магазине'],
        'Номер карты': ['1111222233334444']
    })
    mock_load.return_value = single_card_df

    result_json = home_page('2023-05-01 19:00:00', single_card_df)
    result = json.loads(result_json)

    assert result['greeting'] == "Добрый вечер"
    assert len(result['cards']) == 1

    card = result['cards'][0]
    assert card['last_digits'] == '4444'
    assert card['total_spent'] == pytest.approx(1000.00, abs=0.01)
    assert card['cashback'] == pytest.approx(10.00, abs=0.01)

    assert len(result['top_transactions']) == 1
    assert result['top_transactions'][0]['amount'] == -1000.00
    assert result['top_transactions'][0]['category'] == 'Продукты'


def test_home_page_invalid_date_format() -> None:
    """Тест обработки некорректного формата даты."""
    with pytest.raises(ValueError, match="time data"):
        home_page('некорректная дата')


@patch('src.utils.get_greeting_by_time')
@patch('src.utils.load_transactions')
def test_home_page_no_expenses(mock_greeting: MagicMock, mock_load: MagicMock) -> None:
    mock_greeting.return_value = "Доброе утро"
    income_df = pd.DataFrame({
        'Дата операции': [datetime(2023, 5, 1)],
        'Сумма операции': [5000.00],  # Доход, не расход
        'Категория': ['Зарплата'],
        'Описание': ['Зачисление зарплаты'],
        'Номер карты': ['1234567890123456']
    })
    mock_load.return_value = income_df

    result_json = home_page('2023-05-01 08:00:00', income_df)
    result = json.loads(result_json)

    assert result['greeting'] == "Доброе утро"
    assert len(result['cards']) == 1  # Карта есть, но расходы = 0

    card = result['cards'][0]
    assert card['last_digits'] == '3456'
    assert card['total_spent'] == 0.00
    assert card['cashback'] == 0.00
    assert result['top_transactions'] == []


@patch('src.views.load_transactions')
@patch('src.views.get_greeting_by_time')
def test_home_page_filtering_correctness(mock_greeting: MagicMock, mock_load: MagicMock) -> None:
    """Тест корректности фильтрации по дате."""
    mock_greeting.return_value = "Добрый день"

    # Транзакции за разные месяцы
    mixed_dates_df = pd.DataFrame({
        'Дата операции': [
            datetime(2023, 4, 15),  # Апрель — не должен попасть
            datetime(2023, 5, 1),   # Май — должен попасть
            datetime(2023, 5, 20)   # Май — должен попасть
        ],
        'Сумма операции': [-500.00, -1000.00, -2000.00],
        'Категория': ['Разные', 'Продукты', 'Рестораны'],
        'Описание': ['Апрельская', 'Майская 1', 'Майская 2'],
        'Номер карты': ['1111', '1111', '2222']
    })
    mock_load.return_value = mixed_dates_df

    result_json = home_page('2023-05-25 10:00:00', mixed_dates_df)
    result = json.loads(result_json)

    assert result['greeting'] == "Добрый день"
    # Должны быть только майские транзакции
    assert len(result['cards']) == 2
    # Карта 1111: -1000.00 (майская), карта 2222: -2000.00 (майская)
    card_1111 = next((c for c in result['cards'] if c['last_digits'] == '1111'), None)
    assert card_1111 is not None
    assert card_1111['total_spent'] == pytest.approx(1000.00, abs=0.01)

    card_2222 = next((c for c in result['cards'] if c['last_digits'] == '2222'), None)
    assert card_2222 is not None
    assert card_2222['total_spent'] == pytest.approx(2000.00, abs=0.01)
