# Security Audit Report

## Чек-лист (OWASP Top 10)

- [ ] **Injection**: Проверка на SQL/Command Injection.
- [ ] **Broken Authentication**: Слабые пароли, отсутствие MFA.
- [ ] **Sensitive Data Exposure**: Хранение паролей в открытом виде.
- [ ] **XML External Entities (XXE)**: Обработка XML.
- [ ] **Broken Access Control**: Доступ к чужим данным по ID.
- [ ] **Security Misconfiguration**: Дефолтные настройки, лишние порты.
- [ ] **Cross-Site Scripting (XSS)**: Валидация ввода в веб-интерфейсе.
- [ ] **Insecure Deserialization**: Pickle/Yaml load.
- [ ] **Using Components with Known Vulnerabilities**: Старые библиотеки.
- [ ] **Insufficient Logging & Monitoring**: Отсутствие логов доступа.

## Найденные проблемы

### 1. Hardcoded Secrets
**Severity**: High
**Description**: API ключ найден в коде.
**Remediation**: Перенести в переменные окружения (.env).

### 2. ...
