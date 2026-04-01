from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.utils import filter_by_date_range, get_date_range_by_period, get_greeting_by_time, load_transactions


@patch('pandas.read_excel')
def test_load_transactions_success(mock_read_excel: MagicMock) -> None:
    """Тест успешной загрузки транзакций с моком read_excel."""
    # Настраиваем мок: что возвращает read_excel
    mock_df = pd.DataFrame({
        'Дата операции': ['01.05.2023 10:00:00', '02.05.2023 11:00:00'],
        'Сумма операции': [100.00, 200.00]
    })
    mock_read_excel.return_value = mock_df

    # Вызываем функцию
    result = load_transactions('test_file.xlsx')

    # Проверки
    mock_read_excel.assert_called_once_with('test_file.xlsx')
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert 'Дата операции' in result.columns
    assert pd.api.types.is_datetime64_any_dtype(result['Дата операции'])


@patch('pandas.read_excel')
def test_load_transactions_file_not_found(mock_read_excel: MagicMock) -> None:
    """Тест обработки ошибки загрузки файла."""
    mock_read_excel.side_effect = FileNotFoundError("File not found")

    with pytest.raises(FileNotFoundError, match="File not found"):
        load_transactions('nonexistent.xlsx')


@patch('pandas.read_excel')
@patch('logging.Logger.error')
def test_load_transactions_logging_error(mock_logger: MagicMock, mock_read_excel: MagicMock) -> None:
    """Тест логирования ошибки при загрузке."""
    mock_read_excel.side_effect = Exception("Some error")

    with pytest.raises(Exception, match="Some error"):
        load_transactions('error_file.xlsx')

    mock_logger.assert_called_once()
    assert "Ошибка загрузки файла error_file.xlsx" in mock_logger.call_args[0][0]


@patch('pandas.read_excel')
@patch('src.utils.logger.warning')
def test_load_transactions_empty_file(mock_logger: MagicMock, mock_read_excel: MagicMock) -> None:
    """Тест загрузки пустого Excel-файла с проверкой текста предупреждения."""
    empty_df = pd.DataFrame()
    mock_read_excel.return_value = empty_df

    result = load_transactions('empty_file.xlsx')

    # Проверяем, что предупреждение было вызвано ровно один раз
    mock_logger.assert_called_once()

    # Проверяем текст сообщения
    log_message = mock_logger.call_args[0][0]
    assert "Загружен пустой файл empty_file.xlsx" in log_message
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


def test_filter_by_date_range_with_mock_logging() -> None:
    """Тест фильтрации с проверкой логирования."""
    sample_df = pd.DataFrame({
        'Дата операции': pd.to_datetime(['2023-05-10', '2023-06-15']),
        'Сумма операции': [100.00, 200.00]
    })

    start = pd.to_datetime('2023-05-01')
    end = pd.to_datetime('2023-05-31')

    with patch('src.utils.logger.info') as mock_logger:
        filtered = filter_by_date_range(sample_df, start, end)
        mock_logger.assert_called_once()
        log_message = mock_logger.call_args[0][0]
        assert "Отфильтровано 1 транзакций за период" in log_message
        assert "2023-05-01" in log_message
        assert "2023-05-31" in log_message

    assert len(filtered) == 1
    assert filtered.iloc[0]['Сумма операции'] == 100.00


def test_filter_by_date_range_empty_result() -> None:
    """Тест фильтрации, возвращающей пустой DataFrame."""
    sample_df = pd.DataFrame({
        'Дата операции': pd.to_datetime(['2023-05-10']),
        'Сумма операции': [100.00]
    })

    start = pd.to_datetime('2024-01-01')
    end = pd.to_datetime('2024-01-31')

    with patch('logging.Logger.info') as mock_logger:
        filtered = filter_by_date_range(sample_df, start, end)
        mock_logger.assert_called_once()
        log_message = mock_logger.call_args[0][0]
        assert "Отфильтровано 0 транзакций" in log_message

    assert len(filtered) == 0


@patch('src.utils.datetime')
def test_get_greeting_by_time_morning(mock_datetime: MagicMock) -> None:
    """Тест приветствия для утра."""
    test_time = datetime(2023, 5, 20, 8, 0, 0)
    mock_datetime.now.return_value = test_time
    mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

    greeting = get_greeting_by_time(test_time)
    assert greeting == "Доброе утро"


@pytest.mark.parametrize("date_str,period,expected_start,expected_end", [
    ('2023-05-10 08:00:00', 'W', datetime(2023, 5, 8), datetime(2023, 5, 10, 8, 0, 0)),  # среда → понедельник
    ('2023-05-16 14:00:00', 'W', datetime(2023, 5, 15), datetime(2023, 5, 16, 14, 0, 0)),  # вторник → понедельник
    ('2023-05-01 10:00:00', 'M', datetime(2023, 5, 1), datetime(2023, 5, 1, 10, 0, 0)),
    ('2023-12-25 16:00:00', 'Y', datetime(2023, 1, 1), datetime(2023, 12, 25, 16, 0, 0)),
    ('2024-02-15 12:00:00', 'M', datetime(2024, 2, 1), datetime(2024, 2, 15, 12, 0, 0)),  # високосный год
])
def test_get_date_range_by_period_parametrized(
        date_str: str,
        period: str,
        expected_start: datetime,
        expected_end: datetime) -> None:
    """Параметризованный тест для разных дат и периодов."""

    start, end = get_date_range_by_period(date_str, period)

    # Обнуляем время в start для сравнения (ожидаем начало дня)
    expected_start = expected_start.replace(hour=0, minute=0, second=0, microsecond=0)

    assert start == expected_start
    assert end == expected_end


@patch('src.utils.datetime')  # исправленный путь к datetime
def test_get_date_range_by_period_week_with_patch(mock_dt: MagicMock) -> None:
    """Тест для периода 'W' с использованием @patch."""
    # Настраиваем мок
    target_date = datetime(2023, 5, 15, 10, 0, 0)  # понедельник
    mock_dt.strptime.return_value = target_date

    start, end = get_date_range_by_period('2023-05-15 10:00:00', 'W')

    # Для понедельника начало недели — тот же день, но с 00:00:00
    expected_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    expected_end = target_date

    assert start == expected_start
    assert end == expected_end
    mock_dt.strptime.assert_called_once_with('2023-05-15 10:00:00', '%Y-%m-%d %H:%M:%S')


@patch('src.utils.datetime')  # исправленный путь к datetime
def test_get_date_range_by_period_month_with_patch(mock_dt: MagicMock) -> None:
    """Тест для периода 'M' с использованием @patch."""
    # Настраиваем мок
    target_date = datetime(2023, 6, 15, 14, 30, 0)
    mock_dt.strptime.return_value = target_date

    start, end = get_date_range_by_period('2023-06-15 14:30:00', 'M')

    expected_start = datetime(2023, 6, 1).replace(hour=0, minute=0, second=0, microsecond=0)
    expected_end = target_date

    assert start == expected_start
    assert end == expected_end
    mock_dt.strptime.assert_called_once_with('2023-06-15 14:30:00', '%Y-%m-%d %H:%M:%S')


@pytest.mark.parametrize("weekday,expected_offset", [
    (0, 0),  # понедельник — смещение 0 дней
    (1, 1),  # вторник — смещение 1 день назад
    (2, 2),  # среда — смещение 2 дня назад
    (3, 3),  # четверг — смещение 3 дня назад
    (4, 4),  # пятница — смещение 4 дня назад
    (5, 5),  # суббота — смещение 5 дней назад
    (6, 6),  # воскресенье — смещение 6 дней назад
])
@patch('src.utils.datetime')  # исправленный путь к datetime
def test_get_date_range_by_period_weekdays_with_patch(
        mock_dt: MagicMock,
        weekday: int,
        expected_offset: int) -> None:
    """Параметризованный тест для всех дней недели с @patch."""
    # Создаём дату с заданным днём недели (понедельник = 0)
    base_date = datetime(2023, 5, 8)  # 8 мая 2023 — понедельник
    test_date = base_date + timedelta(days=weekday)
    date_str = test_date.strftime('%Y-%m-%d 10:00:00')

    # Настраиваем мок для strptime
    mock_dt.strptime.return_value = test_date
    start, end = get_date_range_by_period(date_str, 'W')

    expected_start = (test_date - timedelta(days=weekday)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    expected_end = test_date

    assert start == expected_start
    assert end == expected_end
    mock_dt.strptime.assert_called_once()


@patch('src.utils.datetime')  # исправленный путь к datetime
def test_get_date_range_by_period_invalid_format_with_patch(mock_dt: MagicMock) -> None:
    """Тест обработки неверного формата даты с @patch."""
    # Имитируем ошибку парсинга даты
    mock_dt.strptime.side_effect = ValueError("Invalid date format")

    with pytest.raises(ValueError, match="Invalid date format"):
        get_date_range_by_period('invalid-date', 'M')
