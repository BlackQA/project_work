# Фреймворк для автоматизированного тестирования OpenCart и Open Brewery DB

## Описание:

Этот репозиторий содержит автоматизированные тесты для:
- **OpenCart** (UI-тесты через Selenium):
- **Open Brewery DB** (API-тесты через Requests):

Фреймворк использует:
- PyTest в качестве тестового фреймворка
- Allure для отчетности
- интеграцию с Jenkins
- Page Object Model (POM) для UI-тестов
- Кастомную обертку API для тестов Open Brewery DB
- Поддержку браузеров: Chrome, Firefox, Yandex 
- Поддержку headless-режима 
- Автоматический скриншот при ошибке 
- Полное логирование 
- Параметризованные тесты 
- 
## Установка зависимостей:

```bash
  pip install -r requirements.txt
```

Тесты:
Запуск всех тестов:

```bash
pytest tests/
```

Запуск UI тестов в headless режиме:

```bash
pytest tests/ui/ --headless --browser=chrome
```

Запуск API тестов:

```bash
pytest tests/api/
```
