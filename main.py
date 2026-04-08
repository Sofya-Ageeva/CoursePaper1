import logging
import sys
from datetime import datetime
from typing import Any, Dict, List

from src.services import investment_bank, search_by_phone_numbers
from src.utils import get_greeting_by_time, load_transactions
from src.views import home_page

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)


def main() -> None:
    """Главный модуль — демонстрирует работу всех функциональностей."""
    try:
        logger.info("Запуск главного модуля анализа финансовых транзакций")

        # Загружаем данные
        df = load_transactions('data/operations.xlsx')
        transactions: List[Dict[str, Any]] = [
            {str(k): v for k, v in row.items()}
            for row in df.to_dict('records')
        ]
        logger.info(f"Успешно загружено {len(transactions)} транзакций")

        print("\n" + "=" * 60)
        print("=== ГЛАВНЫЙ МОДУЛЬ: ДЕМОНСТРАЦИЯ РАБОТЫ СИСТЕМЫ АНАЛИЗА ФИНАНСОВ ===")
        print("=" * 60 + "\n")

        # 1. Главная страница
        print("1. === ГЛАВНАЯ СТРАНИЦА ===")
        home_result = home_page('2023-12-25 14:30:00')
        print(home_result)
        print()

        # 2. Инвесткопилка
        print("2. === ИНВЕСТКОПИЛКА (декабрь 2023, округление до 50 руб.) ===")
        investment_result = investment_bank('2023-12', transactions, 50)
        print(f"В копилку отложено: {investment_result} руб.")
        print()

        # 3. Поиск транзакций с телефонными номерами
        print("3. === ПОИСК ТРАНЗАКЦИЙ С ТЕЛЕФОННЫМИ НОМЕРАМИ ===")
        phone_transactions = search_by_phone_numbers(transactions)
        if phone_transactions:
            print(f"Найдено {len(phone_transactions)} транзакций с номерами:")
            for i, trans in enumerate(phone_transactions[:3], 1):  # показываем первые 3
                print(f"  {i}. Дата: {trans.get('Дата операции')}, "
                      f"Сумма: {trans.get('Сумма операции')}, "
                      f"Описание: {trans.get('Описание', 'N/A')}")
            if len(phone_transactions) > 3:
                print(f"  ... и ещё {len(phone_transactions) - 3} транзакций")
        else:
            print("Транзакций с телефонными номерами не найдено")
        print()

        # 4. Дополнительная статистика
        print("4. === ДОПОЛНИТЕЛЬНАЯ СТАТИСТИКА ===")
        total_transactions = len(transactions)
        expenses_df = df[df['Сумма операции'] < 0]
        income_df = df[df['Сумма операции'] > 0]

        total_expenses = abs(expenses_df['Сумма операции'].sum())
        total_income = income_df['Сумма операции'].sum()
        net_balance = total_income - total_expenses

        print(f"Всего транзакций: {total_transactions}")
        print(f"Общие расходы: {total_expenses:.2f} руб.")
        print(f"Общие доходы: {total_income:.2f} руб.")
        print(f"Чистый баланс: {net_balance:.2f} руб.")

        # Показываем приветствие в зависимости от времени
        current_datetime = datetime.now()
        greeting = get_greeting_by_time(current_datetime)
        print(f"\n{greeting}! Спасибо за использование системы анализа финансов!")

    except FileNotFoundError:
        logger.error("Файл с операциями не найден: data/operations.xlsx")
        print("Ошибка: Файл с операциями не найден. Убедитесь, что файл data/operations.xlsx существует.")
    except Exception as e:
        logger.error(f"Произошла ошибка при выполнении главного модуля: {e}")
        print(f"Произошла непредвиденная ошибка: {e}")


if __name__ == '__main__':
    main()
