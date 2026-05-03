# Security Audit Report

**Project:** products-s01
**Date:** 2024-04-27
**Auditor:** Student
**Version:** 1.0

---

## 📋 Executive Summary

Был проведен аудит безопасности приложения products-s01. В ходе аудита выявлены следующие критически важные уязвимости, требующие немедленного исправления. Общий уровень безопасности оценивается как **СРЕДНИЙ** с потенциалом повышения до ВЫСОКОГО после устранения найденных проблем.

---

## 🔴 Critical Vulnerabilities

### 1. Hardcoded Database Credentials

| Поле | Значение |
|------|----------|
| **Severity** | Critical |
| **CVSS Score** | 9.8 |
| **Location** | `app/config.py:15` |
| **CWE** | CWE-798 (Use of Hard-coded Credentials) |

**Description:**
Database password хардкожен в исходном коде приложения.

**Evidence:**
```python
# app/config.py
DATABASE_URL = "postgresql://user:hardcoded_password@localhost/db"