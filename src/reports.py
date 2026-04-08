from datetime import datetime, timedelta
from typing import Optional
import pandas as pd


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Возвращает траты по заданной категории за последние три месяца."""
    if date is None:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(date, '%Y-%m-%d')

    start_date = end_date - timedelta(days=90)

    mask = (
        (transactions['Дата операции'] >= start_date)
        & (transactions['Дата операции'] <= end_date)
        & (transactions['Категория'] == category)
    )
    filtered = transactions[mask]

    result = filtered.groupby('Дата операции').agg({
        'Сумма операции': 'sum'
    }).reset_index()
    print(f"Рассчитаны траты по категории '{category}' за период {start_date.date()} — {end_date.date()}")
    return result
