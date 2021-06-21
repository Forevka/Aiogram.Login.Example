## Пример Login button

[Login button](https://core.telegram.org/bots/api#loginurl)

Приложение разбито на две составляющие [bot](https://github.com/Forevka/Aiogram.Login.Example/blob/main/bot.py) и [web](https://github.com/Forevka/Aiogram.Login.Example/blob/main/web.py)


Читая эту статью вы должны ознакомиться с основами питона, здесь не будут разобраны тривиальные вопросы, например импорты в файлах и DI. Также я полагаю что вы уже ознакомились с фреймворками aiogram и fastapi которые были использованы в этом туториале.

# Подготовка перед запуском

После получения токена от бота вам нужно пойти в настройки этого бота, кнопка "Bot Settings" и перейти в раздел "Domain". В этом разделе нужно задать адрес на котором будет размещен веб сервис - тоесть то, куда будет переходить пользователь по нажатию на кнопку с login url

# Разбор кода

## Bot

```python
@dp.message(commands={"login"})
async def cmd_login(message: Message) -> None:
    login_markup = InlineKeyboardMarkup(**{
        "inline_keyboard": [
            [
                InlineKeyboardButton(**{
                    "login_url": LoginUrl(**{
                        "url": f"{HOST_URL}/auth",
                    }),
                    "text": "login",
                })
            ]
        ]
    })

    await message.answer("Here login button", reply_markup=login_markup)
```

Хендлер который реагирует на команду `/login`, он отправляет простое сообщение с кнопкой которая переадресовывает пользователя на ваш сайт.
Собственно со стороны бота это весь нужный нам код.

## Web

```python
def check_user_data(data: TelegramAuthModel, token):
    secret = hashlib.sha256()
    secret.update(token.encode('utf-8'))
    sorted_params = collections.OrderedDict(sorted(data.dict().items()))
    msg = "\n".join(["{}={}".format(k, v)
                    for k, v in sorted_params.items() if k != 'hash'])

    return data.hash == hmac.new(secret.digest(), msg.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()

```
Функция которая проводит валидацию данных переданных от пользователя. Это нужно для того что-бы убедиться что данные пришли действительно от телеграма и юзер их не придумал сам. Алгоритм можно найти [тут](https://core.telegram.org/widgets/login#checking-authorization), а начальный код был взят отсюда [JRootJunior](https://gist.github.com/JrooTJunior/887791de7273c9df5277d2b1ecadc839) правда там есть баг, оставляю найти его и другие различия для читателя.

```python
async def login_route(request: Request, user: TelegramAuthModel = Depends()) -> Response:
    if (ENVIRONMENT.lower().strip() == "production"):
        if (not check_user_data(user, BOT_TOKEN)):
            raise HTTPException(status_code=401, detail="Nice try hacker :D")

    user_from_database = FakeRepo().get_user(user.id)

    if (user_from_database["role_id"] == 2):
        raise HTTPException(
            status_code=401, detail="Sorry you don't have permission")

    return templates.TemplateResponse("login.html", {
        "request": request,
        **user.dict()
    })
```

Самый интересный кусок кода, этo функция которая выступает обработчиком роута для логина пользователя. Именно она будет вызвана после "нажатия" пользователем кнопки login.
Здесь я валидирую данные, проверяю его роль и на основе этого возвращаю ответ.
Предполагается что `FakeRepo` будет заменена на конкретную(другую) имплементацию общения с базой, здесь это выступает как пример алгоритма.

## Config .env
```env
ENVIRONMENT = getenv("env", "debug")

BOT_TOKEN = getenv("bot_token", "Aa:123")
HOST_URL = getenv("host_url", "")
```

Тривиально, задаём токен от бота и хост на котором будут запускаться сервисы.
HOST_URL должен быть белым, тоесть доступным всем в интернете, адресом.

# Как это запустить?

Бот работает в режиме [long polling](https://core.telegram.org/bots/api#getupdates) и ему не нужен белый айпи в отличие от веб сервиса.

## Ручной запуск

Установка зависимостей

`pip install -r requirements.txt`

Bot, **перед запуском проверьте переменные среды**

`python bot.py`

Web построен на fastapi и для него нужен uvicorn, **перед запуском проверьте переменные среды**

`uvicorn web:app --reload`

## Docker

Конфигурация написана в [компоуз файле](https://github.com/Forevka/Aiogram.Login.Example/blob/main/docker-compose.yml).

`docker-compose up`
Всё остальное произойдёт само.

# Использование

После запуска веб сервисе перейдите на `host_url`/docs - вы должны увидеть swagger документацию, пример ниже на скрине 

![swagger](https://github.com/Forevka/Aiogram.Login.Example/blob/main/imgs/swagger-ex.PNG)

Если вы видите такое же на своём экране то скорее всего всё отлично!

После этого вы должны зайти в бота и отправить ему команду `/login` в ответ вы получите сообщение с кнопкой логина

![login-button](https://github.com/Forevka/Aiogram.Login.Example/blob/main/imgs/login-ex.PNG)

После нажатия на эту кнопку вы будете перенаправлены на `host_url`/auth и увидите данный экран

![user](https://github.com/Forevka/Aiogram.Login.Example/blob/main/imgs/user-ex.PNG)

Здесь будет та информация о пользователе которую предоставил вам телеграм. Весь набор полей [можно найти в специальной моделе](https://github.com/Forevka/Aiogram.Login.Example/blob/main/models.py)

## Итог
Здесь был реализован минимальный пример для работы с login button используя современные фреймворки [aiogram v3](https://github.com/aiogram/aiogram/tree/dev-3.x) и [fast-api](https://fastapi.tiangolo.com/)
Безусловно это решение не является единственно верным и правильним, жду ваших PR если у вас есть замечания и предложения.