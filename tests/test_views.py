from unittest.mock import patch
import pytest
import pandas as pd
from src.views import get_main_page_data

@patch('src.utils.load_transactions')
@patch('src.utils.get_currency_rates')
@patch('src.utils.get_stock_prices')
def test_get_main_page_data(mock_stock, mock_currency, mock_load):
    mock_load.return_value = pd.DataFrame({
        'Номер карты': ['1234567890125814', '1234567890127512'],
        'Дата операции': pd.to_datetime(['2023-05-10', '2023-05-15']),
        'Сумма операции': [100.00, 200.00],
        'Категория': ['Переводы', 'Супермаркеты'],
        'Описание': ['Перевод', 'Покупка']
    })
    mock_currency.return_value = [{"currency": "USD", "rate": 73.21}]
    mock_stock.return_value = [{"stock": "AAPL", "price": 150.12}]

    result = get_main_page_data('2023-05-20 14:30:00')

    assert result['greeting'] == "Добрый день"
    assert len(result['cards']) == 2
    assert len(result['top_transactions']) == 2