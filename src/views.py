import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List
from src.utils import (
    filter_by_date_range,
    get_greeting_by_time,
    get_currency_rates,
    get_stock_prices,
    load_transactions
)
import logging

logger = logging.getLogger(__name__)

def get_main_page_data(current_datetime_str: str) -> Dict[str, Any]:
    """Формирует данные для главной страницы.

    Args:
        current_datetime_str (str): Дата и время в формате 'YYYY-MM-DD HH:MM:SS'.

    Returns:
        Dict[str, Any]: JSON-ответ для главной страницы.
    """
    current_datetime = datetime.strptime(current_datetime_str, '%Y-%m-%d %H:%M:%S')
    start_date = current_datetime.replace(day=1)  # Начало месяца
    end_date = current_datetime

    # Загружаем данные
    df = load_transactions('data/operations.xlsx')

    # Фильтруем по дате
    filtered_df = filter_by_date_range(df, start_date, end_date)

    # Приветствие
    greeting = get_greeting_by_time(current_datetime)

    # Обработка карт
    cards = []
    if 'Номер карты' in filtered_df.columns:
        card_groups = filtered_df.groupby('Номер карты')
        for card_num, group in card_groups:
            total_spent = group['Сумма операции'].sum()
            cashback = total_spent * 0.01  # 1% кэшбэка
            cards.append({
                "last_digits": str(card_num)[-4:],
                "total_spent": round(float(total_spent), 2),
                "cashback": round(float(cashback), 2)
            })

    # Топ‑5 транзакций по сумме
    top_transactions = []
    if len(filtered_df) > 0:
        sorted_transactions = filtered_df.nlargest(5, 'Сумма операции')
        for _, row in sorted_transactions.iterrows():
            top_transactions.append({
                "date": row['Дата операции'].strftime('%d.%m.%Y'),
                "amount": round(float(row['Сумма операции']), 2),
                "category": str(row.get('Категория', 'Неизвестно')),
                "description": str(row.get('Описание', 'Без описания'))
            })

    # Курсы валют и акции из настроек
    with open('user_settings.json', 'r', encoding='utf-8') as f:
        settings = json.load(f)
    currency_rates = get_currency_rates(settings['user_currencies'])
    stock_prices = get_stock_prices(settings['user_stocks'])

    return {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
    "currency_rates": currency_rates,
    "stock_prices": stock_prices
    }


