import json
import pandas as pd
from datetime import datetime
import requests
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def load_transactions(file_path: str) -> pd.DataFrame:
    """Загружает транзакции из Excel-файла.

    Args:
        file_path (str): Путь к файлу с транзакциями.

    Returns:
        pd.DataFrame: DataFrame с транзакциями.
    """
    try:
        df = pd.read_excel(file_path)
        logger.info(f"Загружено {len(df)} транзакций из {file_path}")
        return df
    except Exception as e:
        logger.error(f"Ошибка загрузки файла {file_path}: {e}")
        raise

def filter_by_date_range(
    df: pd.DataFrame, start_date: datetime, end_date: datetime
) -> pd.DataFrame:
    """Фильтрует транзакции по диапазону дат.

    Args:
        df (pd.DataFrame): Исходный DataFrame.
        start_date (datetime): Начальная дата.
        end_date (datetime): Конечная дата.

    Returns:
        pd.DataFrame: Отфильтрованный DataFrame.
    """
    mask = (df['Дата операции'] >= start_date) & (df['Дата операции'] <= end_date)
    filtered_df = df[mask].copy()
    logger.info(f"Отфильтровано {len(filtered_df)} транзакций за период")
    return filtered_df

def get_greeting_by_time(current_datetime: datetime) -> str:
    """Возвращает приветствие в зависимости от времени суток.

    Args:
        current_datetime (datetime): Текущая дата и время.

    Returns:
        str: Приветствие.
    """
    hour = current_datetime.hour
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 17:
        return "Добрый день"
    elif 17 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"

def get_currency_rates(currencies: List[str]) -> List[Dict[str, Any]]:
    """Получает курсы валют из API.

    Args:
        currencies (List[str]): Список валют для получения курсов.

    Returns:
        List[Dict[str, Any]]: Список словарей с курсами валют.
    """
    rates = []
    for currency in currencies:
        try:
            # Здесь должен быть реальный API-запрос
            rate = 73.21 if currency == "USD" else 87.08  # Заглушка
            rates.append({"currency": currency, "rate": rate})
        except Exception as e:
            logger.error(f"Ошибка получения курса для {currency}: {e}")
    return rates

def get_stock_prices(stocks: List[str]) -> List[Dict[str, Any]]:
    """Получает цены акций из API.

    Args:
        stocks (List[str]): Список акций для получения цен.

    Returns:
        List[Dict[str, Any]]: Список словарей с ценами акций.
    """
    prices = []
    for stock in stocks:
        try:
            # Здесь должен быть реальный API-запрос
            price = 150.12 if stock == "AAPL" else 3173.18  # Заглушка
            prices.append({"stock": stock, "price": price})
        except Exception as e:
            logger.error(f"Ошибка получения цены для {stock}: {e}")
    return prices


