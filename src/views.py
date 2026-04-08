import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from src.utils import filter_by_date_range, get_greeting_by_time, load_transactions


def home_page(date_string: str, transactions_df: Optional[pd.DataFrame] = None) -> str:
    """Главная страница — возвращает JSON с данными для отображения."""
    current_datetime = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    greeting = get_greeting_by_time(current_datetime)

    # Загружаем данные: используем переданный DataFrame или загружаем из файла
    if transactions_df is None:
        df = load_transactions('data/operations.xlsx')
    else:
        df = transactions_df

    # Фильтруем по дате
    start_date = datetime(current_datetime.year, current_datetime.month, 1)
    filtered_df = filter_by_date_range(df, start_date, current_datetime)

    # Если нет транзакций, возвращаем пустые данные
    if filtered_df.empty:
        result: Dict[str, Any] = {
            'greeting': greeting,
            'cards': [],
            'top_transactions': []
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    # Расчёт данных по картам
    cards_data: List[Dict[str, Any]] = []
    for card_num in filtered_df['Номер карты'].unique():
        card_transactions = filtered_df[filtered_df['Номер карты'] == card_num]
        # Берём только расходные операции (отрицательные суммы)
        expenses = card_transactions[card_transactions['Сумма операции'] < 0]

        if not expenses.empty:
            total_spent = expenses['Сумма операции'].sum()
            cashback = abs(total_spent) * 0.01
        else:
            total_spent = 0
            cashback = 0

        cards_data.append({
            'last_digits': str(card_num)[-4:],
            'total_spent': round(abs(total_spent), 2),
            'cashback': round(cashback, 2)
        })

    # Топ‑5 транзакций (по абсолютной величине расходов)
    expenses_df = filtered_df[filtered_df['Сумма операции'] < 0]
    formatted_top_transactions: List[Dict[str, Any]]
    if not expenses_df.empty:
        top_transactions = (
            expenses_df.sort_values('Сумма операции', ascending=True)
            .head(5)
            [['Дата операции', 'Сумма операции', 'Категория', 'Описание']]
            .to_dict('records')
        )
        # Форматируем топ‑транзакции для JSON
        formatted_top_transactions = [
            {
                'date': t['Дата операции'].strftime('%d.%m.%Y'),
                'amount': round(t['Сумма операции'], 2),
                'category': t['Категория'],
                'description': t['Описание']
            }
            for t in top_transactions
        ]
    else:
        formatted_top_transactions = []

    result = {
        'greeting': greeting,
        'cards': cards_data,
        'top_transactions': formatted_top_transactions
    }

    return json.dumps(result, ensure_ascii=False, indent=2)
