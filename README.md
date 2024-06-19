
# Polygon Django Web3 App

## О проекте

Этот проект позволяет пользователям получать балансы токенов по указанным адресам, получать топ N адресов по балансу токенов, а также получать информацию о токене по его адресу. Он предоставляет следующие функции:
- Получение баланса определенного адреса
- Получение балансов для нескольких адресов
- Получение топ N адресов по балансу токенов
- Получение топ N адресов по балансу токенов с датами последних транзакций
- Получение информации о токене по его адресу

## Используемые технологии

- Python 3.10
- Django 4.2
- Django REST framework 3.14.0
- Web3 6.1.0
- multicall
- httpx
## Клонирование проекта

Выполните следующую команду:

```bash
git clone git@github.com:s1ntecs/polygon_web3_app.git
```

## Настройка переменных среды

- Создайте файл .env в /backend директории проекта.

- Скопируйте содержимое файла .env.example в файл .env.

- Заполните переменные среды в файле .env в соответствии с вашей конфигурацией.

## Установка зависимостей в виртуальное окружение

```
python -m venv venv
source venv/Scripts/activate
cd backend
pip install -r requerements.txt
```

## Применение миграций и запуск проекта

Выполните команды:

```
python manage.py migrate
```

```
python manage.py runserver
```

## Эндпойнты

### Получение баланса выбранного адреса

GET `GET http://localhost:8000/get_balance?address=`
Пример запроса: `http://localhost:8000/get_balance?address=0x5f84192D83A49C2D7Aac6C859a7BDABf18e970b8`

Пример ответа:
```json
{
    "balance": "233.6580794289185"
}
```

### Получение балансов нескольких адресов одновременно

POST `http://localhost:8000/get_balance_batch/`

Тело запроса:

```json
{
    "addresses": ["0x5f84192D83A49C2D7Aac6C859a7BDABf18e970b8", "0x00091B44f98a9DfBaF12CfF719bbA49EC41e0000"]
}
```

Пример ответа:
```json
{
    "balances": [
        233.6580794289185,
        16.350157563222268
    ]
}
```

### Получение списка топ адресов по балансам токена

GET `http://localhost:8000/get_top?N=`

Пример запроса: `http://localhost:8000/get_top?N=3`

Пример ответа:
```json
{
    "top_balances": [
        [
            "0x5f84192D83A49C2D7Aac6C859a7BDABf18e970b8",
            233.6580794289185
        ],
        [
            "0x1b77BD3cb4b21463045Da1DDe5F23E68062b6eB8",
            223.3332499235561
        ],
        [
            "0x8765be05EeC11af44D2b9Ebd23bE8c519A75B5Ff",
            136.01824098932278
        ]
    ]
}
```

### Получение списка топ адресов по балансам токена с информацией о датах последних транзакций (Дата возвращается в формате timestamp)

GET `http://localhost:8000/get_top_with_transactions?N=`

Пример запроса: `http://localhost:8000/get_top_with_transactions?N=3`

Пример ответа:
```json
{
    "top_with_transactions": [
        [
            "0x5f84192d83a49c2d7aac6c859a7bdabf18e970b8",
            233.6580794289185,
            "1692362334"
        ],
        [
            "0x1b77bd3cb4b21463045da1dde5f23e68062b6eb8",
            223.3332499235561,
            "1692348847"
        ],
        [
            "0x8765be05eec11af44d2b9ebd23be8c519a75b5ff",
            136.01824098932278,
            "1692579896"
        ]
    ]
}
```

### Развертывание сервера для обработки HTTP-запросов по вышеуказанным функциям

GET `http://localhost:8000/get_token_info?address=`

Пример запроса: `http://localhost:8000/get_token_info?address=0x1a9b54a3075119f1546c52ca0940551a6ce5d2d0`

Пример ответа:

``` json
{
    "symbol": "TBY",
    "name": "Storage Gastoken V3",
    "totalSupply": 7763601406430754392973
}
```

