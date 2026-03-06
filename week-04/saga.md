# Saga for logs-s01

## Project info
- **project_code**: `logs-s01`
- **group**: 432
- **student**: s01

## Business Process Steps
1. Create log entry → Status: NEW
2. Reserve storage → Status: PAID
3. Process log → Status: DONE


## Сага для обработки логов

## Бизнес-процесс
Сага управляет процессом создания и обработки записи лога через три последовательных шага:

1. **Создание записи лога** — валидация и сохранение метаданных
2. **Резервирование места в хранилище** — проверка размера и выделение ресурсов
3. **Обработка и сохранение лога** — финальное сохранение в хранилище

## Состояния заказа (OrderStatus)
- `NEW` — запись лога создана, ожидает обработки
- `PAID` — место в хранилище зарезервировано (в коде используется как "RESERVED")
- `DONE` — лог успешно обработан и сохранен
- `CANCELLED` — процесс отменен из-за ошибки

## События (Event)
- `CREATE_OK` / `CREATE_FAIL` — результат создания записи
- `RESERVE_OK` / `RESERVE_FAIL` — результат резервирования места
- `PROCESS_OK` / `PROCESS_FAIL` — результат обработки лога

### Таблица переходов

| Текущее состояние | Событие | Следующее состояние |
|-------------------|---------|---------------------|
| NEW | CREATE_OK | PAID |
| NEW | CREATE_FAIL | CANCELLED |
| NEW | RESERVE_FAIL | CANCELLED |
| PAID | RESERVE_OK | PAID (остается) |
| PAID | PROCESS_OK | DONE |
| PAID | PROCESS_FAIL | CANCELLED |

## Компенсирующие транзакции

При отмене саги (переход в CANCELLED) запускаются компенсирующие действия в обратном порядке:

### Шаг 3: Обработка лога (process)
- **Компенсация**: `compensate_process_log()`
- Действие: удаление лога из финального хранилища (`self.storage`)
- Статус: `data["processed"] = False`, `data["status"] = "cancelled"`

### Шаг 2: Резервирование места (reserve)
- **Компенсация**: `compensate_reserve_storage()`
- Действие: освобождение зарезервированного места
- Сброс флагов: `storage_reserved = False`, удаление `reserved_size` и `reserved_at`

### Шаг 1: Создание записи (create)
- **Компенсация**: `compensate_create_log()`
- Действие: удаление записи из `self.logs`
- Пометка: `data["compensated"] = True`

## Обработка ошибок при компенсации

Если компенсирующая транзакция завершается ошибкой, система:

1. **Retry** — повторяет попытку до 3 раз с увеличивающейся задержкой:
   - 1-я попытка: задержка 1 сек
   - 2-я попытка: задержка 5 сек
   - 3-я попытка: задержка 30 сек

2. **Dead Letter Queue (DLQ)** — если все попытки исчерпаны, запись помещается в DLQ для ручного разбора:
   ```python
   dlq_entry = {
       "log_id": log_id,
       "data": log_entry.data,
       "history": log_entry.get_history(),
       "timestamp": time.time(),
       "error": "Compensation failed after all retries"
   }