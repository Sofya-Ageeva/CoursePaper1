import pytest
import pandas as pd
from src.utils import load_transactions, filter_by_date_range, get_greeting_by_time

def test_load_transactions():
    df = load_transactions('data/operations.xlsx')
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0

def test_filter_by_date_range():
    sample_df = pd.DataFrame({
        'Дата операции': pd.to_datetime(['2023-05-10', '2023-06-15']),
        'Сумма операции': [100.00, 200.00]
    })
    start = pd.to_datetime('2023-05-01')
    end = pd.to_datetime('2023-05-31')
    filtered = filter_by_date_range(sample_df, start, end)
    assert len(filtered) == 1

def test_get_greeting_by_time():
    morning = get_greeting_by_time(pd.to_datetime('2023-05-20 08:00:00'))
    assert morning == "Доброе утро"