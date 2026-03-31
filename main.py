from src.views import get_main_page_data
from src.services import investment_bank
import json

if __name__ == '__main__':
    # Пример вызова главной страницы
    main_data = get_main_page_data('2023-05-20 14:30:00')
    print("Главная страница:")
    print(json.dumps(main_data, ensure_ascii=False, indent=2))

    # Пример вызова сервиса «Инвесткопилка»
    sample_transactions = [
        {'Дата операции': '2023-05-10', 'Сумма операции': 1712.00},
        {'Дата операции': '2023-05-15', 'Сумма операции': 2450.00}
    ]
    saved = investment_bank('2023-05', sample_transactions, 50)
    print(f"\nИнвесткопилка: {saved} руб.")
