from datetime import datetime

import pandas as pd
import pytest

from src.reports import spending_by_category


@pytest.fixture
def sample_transactions() -> pd.DataFrame:
    """Фикстура с тестовыми данными транзакций."""
    return pd.DataFrame({
        'Дата операции': [
            datetime(2023, 10, 1),
            datetime(2023, 11, 15),
            datetime(2023, 12, 1),
            datetime(2024, 1, 10),
            datetime(2024, 1, 20),
            datetime(2024, 2, 5)
        ],
        'Сумма операции': [-1000, -2000, -1500, -3000, -500, -800],
        'Категория': [
            'Супермаркеты', 'Рестораны', 'Супермаркеты',
            'Супермаркеты', 'Транспорт', 'Супермаркеты'
        ],
        'Описание': [
            'Покупка продуктов', 'Ужин в ресторане', 'Продукты',
            'Еженедельная закупка', 'Автобус', 'Продукты'
        ]
    })


def test_default_date_returns_dataframe(sample_transactions: pd.DataFrame) -> None:
    """Тест: функция возвращает DataFrame при использовании текущей даты."""
    result = spending_by_category(sample_transactions, 'Супермаркеты')
    assert isinstance(result, pd.DataFrame)
    assert 'Дата операции' in result.columns
    assert 'Сумма операции' in result.columns


def test_correct_sum_for_category(sample_transactions: pd.DataFrame) -> None:
    """Тест: корректная сумма трат по категории за последние 90 дней."""
    # Фиксируем дату для воспроизводимости теста
    test_date = '2024-02-10'
    result = spending_by_category(sample_transactions, 'Супермаркеты', test_date)

    # Период: 90 дней до 2024‑02‑10 → с 2023‑11‑12 по 2024‑02‑10
    # Транзакции в периоде:
    # - 2023-12-01: -1500
    # - 2024-01-10: -3000
    # - 2024-02-05: -800
    expected_sum = -1500 + (-3000) + (-800)  # -5300
    actual_sum = result['Сумма операции'].sum()
    assert actual_sum == expected_sum, f"Ожидаемая сумма: {expected_sum}, фактическая: {actual_sum}"


def test_specific_date_filtering(sample_transactions: pd.DataFrame) -> None:
    """Тест: фильтрация по указанной дате (90 дней до указанной даты)."""
    test_date = '2024-02-10'
    result = spending_by_category(sample_transactions, 'Супермаркеты', test_date)

    expected_start = datetime(2023, 11, 12)  # 90 дней назад от 2024-02-10
    expected_end = datetime(2024, 2, 10)

    # В этот период попадают транзакции:
    # 2023-12-01 (-1500), 2024-01-10 (-3000), 2024-02-05 (-800)
    expected_sum = -1500 + (-3000) + (-800)  # -5300

    actual_sum = result['Сумма операции'].sum()

    if not result.empty:
        min_date = result['Дата операции'].min()
        max_date = result['Дата операции'].max()
        assert min_date >= expected_start, f"Минимальная дата {min_date} раньше ожидаемой {expected_start}"
        assert max_date <= expected_end, f"Максимальная дата {max_date} позже ожидаемой {expected_end}"

    assert actual_sum == expected_sum, f"Ожидаемая сумма: {expected_sum}, фактическая: {actual_sum}"


def test_category_not_found_returns_empty_df(sample_transactions: pd.DataFrame) -> None:
    """Тест: пустая таблица при отсутствии категории."""
    result = spending_by_category(sample_transactions, 'Неизвестная категория')
    assert result.empty
    assert len(result) == 0


def test_empty_dataframe_returns_empty_result() -> None:
    """Тест: пустая входная таблица → пустой результат."""
    empty_df = pd.DataFrame(columns=['Дата операции', 'Сумма операции', 'Категория', 'Описание'])
    result = spending_by_category(empty_df, 'Супермаркеты')
    assert result.empty
    assert len(result) == 0


def test_no_transactions_in_period_returns_empty(sample_transactions: pd.DataFrame) -> None:
    """Тест: нет транзакций в периоде → пустой результат."""
    old_data = pd.DataFrame({
        'Дата операции': [datetime(2022, 1, 1), datetime(2022, 2, 1)],
        'Сумма операции': [-500, -1000],
        'Категория': ['Супермаркеты', 'Супермаркеты'],
        'Описание': ['Старые покупки', 'Старые покупки']
    })
    result = spending_by_category(old_data, 'Супермаркеты', '2024-01-01')
    assert result.empty


def test_single_transaction_returns_correct_amount(sample_transactions: pd.DataFrame) -> None:
    """Тест: одна транзакция → корректная сумма."""
    single_data = pd.DataFrame({
        'Дата операции': [datetime(2024, 1, 10)],
        'Сумма операции': [-2500],
        'Категория': ['Супермаркеты'],
        'Описание': ['Единственная покупка']
    })
    result = spending_by_category(single_data, 'Супермаркеты', '2024-01-20')
    assert len(result) == 1
    assert result['Сумма операции'].iloc[0] == -2500


def test_multiple_transactions_same_date_grouped(sample_transactions: pd.DataFrame) -> None:
    """Тест: несколько транзакций в один день → сгруппированы."""
    same_day_data = pd.DataFrame({
        'Дата операции': [
            datetime(2024, 1, 10),
            datetime(2024, 1, 10),
            datetime(2024, 1, 10)
        ],
        'Сумма операции': [-500, -300, -700],
        'Категория': ['Супермаркеты', 'Супермаркеты', 'Супермаркеты'],
        'Описание': ['Покупка 1', 'Покупка 2', 'Покупка 3']
    })
    result = spending_by_category(same_day_data, 'Супермаркеты', '2024-01-20')
    assert len(result) == 1
    assert result['Сумма операции'].iloc[0] == -1500  # -500 + -300 + -700


def test_invalid_date_format_raises_valueerror(sample_transactions: pd.DataFrame) -> None:
    """Тест: некорректный формат даты → ValueError."""
    with pytest.raises(ValueError):
        spending_by_category(sample_transactions, 'Супермаркеты', 'некорректная_дата')


def test_grouping_by_date(sample_transactions: pd.DataFrame) -> None:
    """Тест: группировка транзакций по дате."""
    # Создаём данные с несколькими транзакциями в один день
    multi_day_data = pd.DataFrame({
        'Дата операции': [
            datetime(2024, 1, 10),
            datetime(2024, 1, 10),
            datetime(2024, 1, 15)
        ],
        'Сумма операции': [-100, -200, -300],
        'Категория': ['Супермаркеты', 'Супермаркеты', 'Супермаркеты']
    })
    result = spending_by_category(multi_day_data, 'Супермаркеты', '2024-01-20')
    # Должны быть две строки: одна для 2024‑01‑10 (сумма -300), одна для 2024‑01‑15 (-300)
    assert len(result) == 2
    # Проверяем сумму для первой даты
    first_row = result.iloc[0]
    assert first_row['Сумма операции'] == -300 or first_row['Сумма операции'] == -300
