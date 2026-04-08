import pytest
from typing import List, Dict, Any
from src.services import investment_bank, search_by_phone_numbers


def test_investment_bank_basic_case() -> None:
    """Базовый случай: одна транзакция, требующая округления."""
    transactions = [
        {'Дата операции': '2023-05-10', 'Сумма операции': 1712.00}
    ]
    saved = investment_bank('2023-05', transactions, 50)
    assert saved == 38.00  # 1750 - 1712 = 38


def test_investment_bank_invalid_date_format() -> None:
    """Тест на некорректный формат даты месяца."""
    transactions = [
        {'Дата операции': '2023-04-10', 'Сумма операции': 100.00}
    ]
    with pytest.raises(ValueError) as excinfo:
        investment_bank('invalid-month', transactions, 50)
    assert 'Некорректный формат месяца' in str(excinfo.value)


def test_investment_bank_transaction_with_invalid_date() -> None:
    """Транзакция с некорректной датой пропускается."""
    transactions = [
        {'Дата операции': 'invalid-date', 'Сумма операции': 100.00},
        {'Дата операции': '2023-05-15', 'Сумма операции': 200.00}
    ]
    saved = investment_bank('2023-05', transactions, 50)
    assert saved == 0.00  # Только корректная транзакция учитывается, 200 кратно 50


def test_search_by_phone_numbers_basic() -> None:
    """Базовый случай: один номер в описании."""
    transactions = [
        {'Описание': 'Я МТС +7 921 11-22-33', 'Сумма': 100},
        {'Описание': 'Без номера', 'Сумма': 200}
    ]
    result = search_by_phone_numbers(transactions)
    print(f"\nDEBUG: Найдено транзакций: {len(result)}")
    if result:
        print(f"DEBUG: Первая найденная транзакция: {result[0]}")
    assert len(result) == 1
    assert '+7 921 11-22-33' in result[0]['Описание']


def test_search_by_phone_numbers_missing_description() -> None:
    """Транзакция без поля 'Описание'."""
    transactions: List[Dict[str, Any]] = [
        {'Сумма': 100},  # Нет описания
        {'Описание': '+7 921 11-22-33', 'Сумма': 200}
    ]
    result = search_by_phone_numbers(transactions)
    print(f"\nDEBUG: Найдено транзакций: {len(result)}")
    if result:
        print(f"DEBUG: Найденные транзакции: {result}")
    assert len(result) == 1
    assert '+7 921 11-22-33' in result[0]['Описание']


def test_search_by_phone_numbers_different_formats() -> None:
    """Разные форматы номеров."""
    transactions = [
        {'Описание': '+7 (921) 111-22-33'},
        {'Описание': '+7 981 333-44-55'},
        {'Описание': '+7-921-111-22-33'},
        {'Описание': '+79211112233'},
        {'Описание': 'Обычный текст без номера'}
    ]
    result = search_by_phone_numbers(transactions)
    assert len(result) == 4
    descriptions_found = [t['Описание'] for t in result]
    assert '+7 (921) 111-22-33' in descriptions_found
    assert '+7 981 333-44-55' in descriptions_found
    assert '+7-921-111-22-33' in descriptions_found
    assert '+79211112233' in descriptions_found


def test_search_by_phone_numbers_no_phones() -> None:
    """Нет номеров в описаниях."""
    transactions = [
        {'Описание': 'Покупка в магазине', 'Сумма': 100},
        {'Описание': 'Оплата услуг', 'Сумма': 200}
    ]
    result = search_by_phone_numbers(transactions)
    assert len(result) == 0


def test_search_by_phone_numbers_empty_list() -> None:
    """Пустой список транзакций."""
    result = search_by_phone_numbers([])
    assert len(result) == 0
