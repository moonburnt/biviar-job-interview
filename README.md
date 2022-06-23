*Тестовое задание для собеседования в BIVIAR*.

# Описание

API для проведения онлайн-курсов, с использованием Django/DRF. Тестировалось с
python 3.10.
Документация API доступна в `/api/swagger`. Например:
`http://127.0.0.1:8000/api/swagger/`
(Swagger кидает exceptions при генерации схемы - это нормально, не нашел где отключить)

# Установка

```
git clone https://github.com/moonburnt/biviar-job-interview
cd biviar-job-interview
virtualenv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

# Запуск

```
cd courses
python manage.py runserver
```
