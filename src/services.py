import logging
import re
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """Рассчитывает сумму для «Инвесткопилки» через округление трат."""
    try:
        target_month = datetime.strptime(month, '%Y-%m')
        total_saved = 0.0

        for transaction in transactions:
            # Безопасное получение данных транзакции
            transaction_date_str = transaction.get('Дата операции')
            amount_str = transaction.get('Сумма операции')

            if transaction_date_str is None or amount_str is None:
                logger.warning(f"Пропущена транзакция с неполными данными: {transaction}")
                continue

            try:
                transaction_date = datetime.strptime(transaction_date_str, '%Y-%m-%d')
                amount = float(amount_str)
            except (ValueError, TypeError) as e:
                logger.warning(f"Пропущена транзакция с некорректными данными: {transaction}. Ошибка: {e}")
                continue

            # Проверка, относится ли транзакция к целевому месяцу

            if (transaction_date.year == target_month.year
                    and transaction_date.month == target_month.month):
                # Округление вверх до ближайшего кратного limit
                if amount % limit == 0:
                    rounded_amount = amount
                else:
                    rounded_amount = ((amount // limit) + 1) * limit
                saved = rounded_amount - amount
                total_saved += saved

        logger.info(f"Инвесткопилка: отложено {total_saved:.2f} руб. за {month}")
        return round(total_saved, 2)

    except ValueError as e:
        error_msg = f"Некорректный формат месяца '{month}'. Ожидаемый формат: 'YYYY-MM'"
        logger.error(error_msg)
        raise ValueError(error_msg) from e


def search_by_phone_numbers(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ищет транзакции с телефонными номерами в описании.

    Args:
        transactions (List[Dict[str, Any]]): Список транзакций.

    Returns:
        List[Dict[str, Any]]: Транзакции с телефонными номерами.
    """
    # Улучшенное регулярное выражение — более гибкое
    phone_pattern = r'\+7[\s\-]?(?:\(\d{3}\)|\d{3})[\s\-]?\d{1,3}[\s\-]?\d{2}[\s\-]?\d{2}'
    result = []

    for transaction in transactions:
        # Безопасное получение описания
        description = transaction.get('Описание', '')
        if description is None:
            description = ''
        else:
            description = str(description)

        # Отладка: выводим, что ищем и где
        logger.debug(f"Проверяем описание: '{description}'")

        # Проверяем, есть ли номер в описании
        match = re.search(phone_pattern, description)
        if match:
            logger.debug(f"Найден номер: '{match.group()}' в описании: '{description}'")
            result.append(transaction)

    logger.info(f"Найдено {len(result)} транзакций с телефонными номерами")
    return result
