from enum import Enum
from typing import Dict, Optional, Callable
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrderStatus(str, Enum):
    NEW = "NEW"
    PAID = "PAID"
    DONE = "DONE"
    CANCELLED = "CANCELLED"


class Event(str, Enum):
    CREATE_OK = "CREATE_OK"
    CREATE_FAIL = "CREATE_FAIL"
    RESERVE_OK = "RESERVE_OK"
    RESERVE_FAIL = "RESERVE_FAIL"
    PROCESS_OK = "PROCESS_OK"
    PROCESS_FAIL = "PROCESS_FAIL"


def next_state(state: str, event: str) -> str:
    """
    Определяет следующее состояние на основе текущего состояния и события.
    Args:
        state: Текущее состояние (NEW, PAID, DONE, CANCELLED)
        event: Событие (PAY_OK, PAY_FAIL, PROCESS_OK, PROCESS_FAIL)
    Returns:
        Следующее состояние
    """
    transitions = {
        ('NEW', 'PAY_OK'): 'PAID',
        ('NEW', 'PAY_FAIL'): 'CANCELLED',
        ('PAID', 'PROCESS_OK'): 'DONE',
        ('PAID', 'PROCESS_FAIL'): 'CANCELLED',
    }
    
    if (state, event) in transitions:
        new_state = transitions[(state, event)]
        logger.info(f"Transition: {state} + {event} -> {new_state}")
        return new_state
    
    logger.warning(f"Invalid transition: {state} + {event}")
    return state


class LogEntry:
    def __init__(self, log_id: str, data: Dict):
        self.log_id = log_id
        self.data = data
        self.status = OrderStatus.NEW
        self.history = [{"state": OrderStatus.NEW, "event": "INIT", "timestamp": time.time()}]
    
    def apply_event(self, event: str) -> str:
        old_status = self.status
        new_status = next_state(self.status, event)
        
        if new_status != old_status:
            self.status = new_status
            self.history.append({
                "state": new_status,
                "event": event,
                "timestamp": time.time()
            })
            logger.info(f"Log {self.log_id}: {old_status} -> {new_status} via {event}")
        
        return self.status
    
    def get_history(self):
        return self.history


class LogSagaOrchestrator:
    def __init__(self, max_retries: int = 3):
        self.logs: Dict[str, LogEntry] = {}
        self.max_retries = max_retries
        self.storage = {}  # Имитация хранилища логов
    
    def create_log(self, log_id: str, data: Dict) -> LogEntry:
        """Шаг 1: Создание записи лога"""
        log_entry = LogEntry(log_id, data)
        self.logs[log_id] = log_entry
        logger.info(f"Log {log_id} created with status {log_entry.status}")
        return log_entry
    
    def step_create_log(self, log_entry: LogEntry) -> bool:
        """
        Шаг 1: Создание записи лога
        """
        logger.info(f"Creating log entry {log_entry.log_id}")
        # Валидация данных лога
        if not log_entry.data.get("message"):
            raise ValueError("Log message is required")
        if not log_entry.data.get("level"):
            log_entry.data["level"] = "INFO"  # Уровень по умолчанию
        
        log_entry.data["created_at"] = time.time()
        log_entry.data["status"] = "pending"
        return True
    
    def compensate_create_log(self, log_entry: LogEntry):
        """
        Компенсация для шага 1: Удаление созданной записи
        """
        logger.info(f"Compensating: Removing log entry {log_entry.log_id}")
        if log_entry.log_id in self.logs:
            del self.logs[log_entry.log_id]
        log_entry.data["compensated"] = True
    
    def step_reserve_storage(self, log_entry: LogEntry) -> bool:
        """
        Шаг 2: Резервирование места в хранилище
        """
        logger.info(f"Reserving storage for log {log_entry.log_id}")
        
        log_size = len(str(log_entry.data)) * 2  
        storage_limit = 1024 * 1024 
        
        if log_size > storage_limit:
            raise Exception(f"Log size {log_size} exceeds storage limit")
        
        log_entry.data["storage_reserved"] = True
        log_entry.data["reserved_size"] = log_size
        log_entry.data["reserved_at"] = time.time()
        
        return True
    
    def compensate_reserve_storage(self, log_entry: LogEntry):
        """
        Освобождение зарезервированного места
        """
        logger.info(f"Compensating: Freeing storage for log {log_entry.log_id}")
        log_entry.data["storage_reserved"] = False
        log_entry.data.pop("reserved_size", None)
        log_entry.data.pop("reserved_at", None)
    
    def step_process_log(self, log_entry: LogEntry) -> bool:
        """
        Обработка и сохранение лога
        """
        logger.info(f"Processing log {log_entry.log_id}")
        
        if log_entry.data.get("simulate_failure"):
            raise Exception("Simulated processing failure")
        
        self.storage[log_entry.log_id] = {
            "data": log_entry.data,
            "processed_at": time.time(),
            "status": "processed"
        }
        
        log_entry.data["processed"] = True
        log_entry.data["processed_at"] = time.time()
        log_entry.data["status"] = "completed"
        
        return True
    
    def compensate_process_log(self, log_entry: LogEntry):
        """
        Компенсация для шага 3: Удаление из хранилища
        """
        logger.info(f"Compensating: Removing log {log_entry.log_id} from storage")
        if log_entry.log_id in self.storage:
            del self.storage[log_entry.log_id]
        log_entry.data["processed"] = False
        log_entry.data.pop("processed_at", None)
        log_entry.data["status"] = "cancelled"
    
    def execute_saga_step(self, log_id: str, step_name: str, step_func: Callable, 
                          compensation_func: Optional[Callable] = None,
                          success_event: Optional[str] = None,
                          fail_event: Optional[str] = None) -> bool:

        log_entry = self.logs.get(log_id)
        if not log_entry:
            logger.error(f"Log {log_id} not found")
            return False
        
        try:
            logger.info(f"Executing step {step_name} for log {log_id}")
            result = step_func(log_entry)
            
            if success_event:
                log_entry.apply_event(success_event)
            
            return True
            
        except Exception as e:
            logger.error(f"Step {step_name} failed for log {log_id}: {e}")
            
            if fail_event:
                log_entry.apply_event(fail_event)
            
            if compensation_func and log_entry.status == OrderStatus.CANCELLED:
                self._compensate_with_retry(log_id, compensation_func)
                self._compensate_previous_steps(log_id, step_name)
            
            return False
    
    def _compensate_previous_steps(self, log_id: str, failed_step: str):
        log_entry = self.logs.get(log_id)
        if not log_entry:
            return
        
        if failed_step == "process":
            self._compensate_with_retry(log_id, self.compensate_reserve_storage)
            self._compensate_with_retry(log_id, self.compensate_create_log)
        elif failed_step == "reserve":
            self._compensate_with_retry(log_id, self.compensate_create_log)
    
    def _compensate_with_retry(self, log_id: str, compensation_func: Callable):
        # Запускает компенсацию с макс 3 попытками при ошибке.
        log_entry = self.logs.get(log_id)
        if not log_entry:
            return
        
        delays = [1, 5, 30]
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Compensation attempt {attempt + 1} for log {log_id}")
                compensation_func(log_entry)
                logger.info(f"Compensation successful for log {log_id}")
                return
            except Exception as e:
                logger.error(f"Compensation attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(delays[attempt])
        
        logger.critical(f"All compensation attempts failed for log {log_id}. Moving to DLQ.")
        self._write_to_dlq(log_id, log_entry)
    
    def _write_to_dlq(self, log_id: str, log_entry: LogEntry):
        """
        Запись в Dead Letter Queue для ручной обработки
        """
        dlq_entry = {
            "log_id": log_id,
            "data": log_entry.data,
            "history": log_entry.get_history(),
            "timestamp": time.time(),
            "error": "Compensation failed after all retries"
        }
        logger.error(f"DLQ: {dlq_entry}")


def run_saga_example():
    orchestrator = LogSagaOrchestrator()

    log_entry = orchestrator.create_log(
        log_id="log-001",
        data={
            "message": "User login successful",
            "level": "INFO",
            "user_id": "user123",
            "ip": "192.168.1.100"
        }
    )
    
    print("\n=== Starting Saga for log-001 ===\n")
    
    # Шаг 1: Создание записи лога
    success = orchestrator.execute_saga_step(
        log_id="log-001",
        step_name="create",
        step_func=orchestrator.step_create_log,
        compensation_func=orchestrator.compensate_create_log,
        success_event=Event.CREATE_OK,
        fail_event=Event.CREATE_FAIL
    )
    print(f"Step 1 (CREATE) {'✓' if success else '✗'}")
    
    # Шаг 2: Резервирование места
    success = orchestrator.execute_saga_step(
        log_id="log-001",
        step_name="reserve",
        step_func=orchestrator.step_reserve_storage,
        compensation_func=orchestrator.compensate_reserve_storage,
        success_event=Event.RESERVE_OK,
        fail_event=Event.RESERVE_FAIL
    )
    print(f"Step 2 (RESERVE) {'✓' if success else '✗'}")
    
    # Шаг 3: Обработка лога
    success = orchestrator.execute_saga_step(
        log_id="log-001",
        step_name="process",
        step_func=orchestrator.step_process_log,
        compensation_func=orchestrator.compensate_process_log
    )
    print(f"Step 3 (PROCESS) {'✓' if success else '✗'}")
    
    print(f"\nFinal status: {log_entry.status}")
    print(f"Final data: {log_entry.data}")
    print(f"History: {log_entry.get_history()}")
    
    return orchestrator, log_entry


def run_failure_scenario():
    """
    Пример с ошибкой на шаге 3 (должна запуститься компенсация)
    """
    print("\n=== Running Failure Scenario ===\n")
    
    orchestrator = LogSagaOrchestrator()
    
    log_entry = orchestrator.create_log(
        log_id="log-002",
        data={
            "message": "Failed transaction",
            "level": "ERROR",
            "simulate_failure": True
        }
    )
    
    orchestrator.execute_saga_step(
        log_id="log-002",
        step_name="create",
        step_func=orchestrator.step_create_log,
        compensation_func=orchestrator.compensate_create_log,
        success_event=Event.CREATE_OK,
        fail_event=Event.CREATE_FAIL
    )
    
    orchestrator.execute_saga_step(
        log_id="log-002",
        step_name="reserve",
        step_func=orchestrator.step_reserve_storage,
        compensation_func=orchestrator.compensate_reserve_storage,
        success_event=Event.RESERVE_OK,
        fail_event=Event.RESERVE_FAIL
    )
    
    orchestrator.execute_saga_step(
        log_id="log-002",
        step_name="process",
        step_func=orchestrator.step_process_log,
        compensation_func=orchestrator.compensate_process_log
    )
    
    print(f"\nFailure scenario final status: {log_entry.status}")
    print(f"Failure scenario data: {log_entry.data}")


if __name__ == "__main__":
    orchestrator, log_entry = run_saga_example()
    
    run_failure_scenario()
