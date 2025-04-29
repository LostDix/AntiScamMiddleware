# AntiScamMiddleware | Защита Telegram-чатов от мошенников
Этот middleware помогает защитить участников чата от финансовых мошенников, регулярно напоминая о мерах безопасности. Давайте разберём его работу подробно.
<br>
[Разработка Телеграм ботов](https://else.com.ru "Разработка Телеграм ботов") -> https://else.com.ru/

## Назначение класса
`AntiScamMiddleware` выполняет важную профилактическую функцию:

<ol> 
    <li>Отслеживает активность в чате</li> 
    <li>Автоматически отправляет предупреждения о мошенничестве</li> 
    <li>Контролирует частоту уведомлений</li> 
    <li>Не мешает обычному общению</li> 
</ol>
    
## Константа предупреждения
```
  WARNING_TEXT = """
  ⚠️ <b>Внимание! Участились случаи мошенничества!</b>

  Дорогие пользователи, будьте бдительны! В последнее время участились попытки обмана.
  🔹 Никогда не переводите средства незнакомым людям!
  🔹 Администрация НЕ запрашивает переводы.
  🔹 Проверяйте информацию и не доверяйте подозрительным предложениям.

  Берегите себя и свои финансы!
  """
```


+ HTML-форматированное сообщение</li>
+ Чёткие инструкции для пользователей</li>
+ Профилактическая информация</li>

## Инициализация
```
  def __init__(self, bot):
    self.bot = bot
    self.last_warning_time = {}  # {chat_id: last_warning_datetime}
    self.message_counters = defaultdict(int)  # {chat_id: message_count}
    super().__init__()
    logger.info("Initialized AntiScamMiddleware")
```
+ `bot` - экземпляр бота для отправки сообщений</li>
+ `last_warning_time` - время последнего предупреждения для каждого чата</li>
+ `message_counters` - счётчик сообщений в чатах</li>

## Основная логика работы
1. Обработка сообщений
```
  message = event.message or event.edited_message
  if not message:
    return await handler(event, data)

  if self._is_service_message(message):
    return await handler(event, data)

  chat_id = message.chat.id
```
+ Работает с обычными и отредактированными сообщениями</li>
+ Игнорирует служебные сообщения</li>
+ Получает идентификатор чата</li>

2. Учёт активности
```
  self.message_counters[chat_id] += 1

  if not message.reply_to_message and await self._check_general_warning(message):
    await self._send_warning(message)
    self.last_warning_time[chat_id] = datetime.now()
    self.message_counters[chat_id] = 0
```
+ Увеличивает счётчик сообщений</li>
+ Проверяет условия для отправки предупреждения</li>
+ Сбрасывает счётчик после отправки</li>

## Методы проверок
Условия отправки предупреждения
```
  async def _check_general_warning(self, message: Message) -> bool:
    chat_id = message.chat.id

    if chat_id not in self.last_warning_time:
        return True

    if (datetime.now() - self.last_warning_time[chat_id]) < timedelta(hours=3):
        return False

    return self.message_counters[chat_id] >= 50
```
+ Первое предупреждение - сразу</li>
+ Последующие - не чаще чем раз в 3 часа</li>
+ Только после 50+ сообщений в чате</li>

Отправка предупреждения
```
  async def _send_warning(self, message: Message):
    try:
        await self.bot.send_message(
            chat_id=message.chat.id,
            text=WARNING_TEXT,
            parse_mode="HTML"
        )
        logger.info(f"Sent scam warning to chat {message.chat.id}")
    except Exception as e:
        logger.error(f"Failed to send warning message: {e}")
```
+ Использует HTML-разметку</li>
+ Логирует успешную отправку</li>
+ Обрабатывает ошибки отправки</li>

## Практическое применение
Этот middleware особенно полезен для:

+ Финансовых чатов и каналов
+ Криптовалютных сообществ
+ Торговых площадок
+ Чатов с высокой активностью
+ Любых групп, где возможны случаи мошенничества


## Кастомизация
Вы можете адаптировать middleware под свои нужды:

<ol>
    <li>Изменить текст предупреждения</li>
    <li>Настроить временные интервалы</li>
    <li>Добавить проверку ключевых слов</li>
    <li>Ввести разные уровни предупреждений</li>
</ol>

```
  # Пример кастомизации интервалов
  def __init__(self, bot):
    self.warning_interval = timedelta(hours=1)  # вместо 3 часов
    self.message_threshold = 30  # вместо 50 сообщений
    ...
```

## Заключение
AntiScamMiddleware - это эффективное решение для профилактики мошенничества в Telegram-чатах, которое ненавязчиво напоминает участникам о безопасности.
<br>
<blockquote>
<b>Хотите комплексную защиту от мошенников в вашем чате?</b>

Команда ELSE (https://else.com.ru/) разрабатывает продвинутые системы безопасности:<br>

✅ Защиту от спама (как в этом примере)<br>
✅ Интеграцию с API, базами данных и внешними сервисами<br>
✅ Кастомизированные предупреждения<br>
✅ Быструю и стабильную работу<br>

Закажите защищённый чат на else.com.ru и общайтесь безопасно!<br>
[Создание Телеграм ботов](https://else.com.ru "Разработка Телеграм ботов") -> https://else.com.ru/
</blockquote>
    

    
