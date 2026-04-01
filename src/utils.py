import logging
from datetime import datetime, timedelta

import pandas as pd

logger = logging.getLogger(__name__)


def load_transactions(file_path: str) -> pd.DataFrame:
    """Загружает транзакции из Excel-файла."""
    try:
        df = pd.read_excel(file_path)
        if df.empty:
            logger.warning(f"Загружен пустой файл {file_path}")
        if 'Дата операции' in df.columns:
            df['Дата операции'] = pd.to_datetime(df['Дата операции'], dayfirst=True)
        logger.info(f"Загружено {len(df)} транзакций из {file_path}")
        return df
    except Exception as e:
        logger.error(f"Ошибка загрузки файла {file_path}: {e}")
        raise


def get_greeting_by_time(current_datetime: datetime) -> str:
    """Возвращает приветствие в зависимости от времени суток."""
    hour = current_datetime.hour
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 17:
        return "Добрый день"
    elif 17 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def filter_by_date_range(df: pd.DataFrame, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """Фильтрует транзакции по диапазону дат."""
    mask = (df['Дата операции'] >= start_date) & (df['Дата операции'] <= end_date)
    filtered_df = df[mask].copy()
    logger.info(
        f"Отфильтровано {len(filtered_df)} транзакций за период "
        f"{start_date.strftime('%Y-%m-%d')} — {end_date.strftime('%Y-%m-%d')}"
    )
    return filtered_df


def get_date_range_by_period(date_str: str, period: str = 'M') -> tuple[datetime, datetime]:
    """Возвращает диапазон дат в зависимости от периода."""
    target_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    end_date = target_date

    if period == 'W':
        start_date = end_date - timedelta(days=end_date.weekday())
    elif period == 'M':
        start_date = datetime(target_date.year, target_date.month, 1)
    elif period == 'Y':
        start_date = datetime(target_date.year, 1, 1)
    else:
        raise ValueError(f"Неизвестный период: {period}")

    return start_date, end_date
