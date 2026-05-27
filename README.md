# Heisenberg Telegram Bot (aiogram 3.x + Google GenAI)

Бот для **супергрупп** в Telegram: он **игнорирует всё**, кроме сообщений, которые начинаются с обращения:

- `Хайзенберг, ...`
- `Хайзенберг ...`

Проверка **регистронезависимая** (работает и `хайзенберг`).

Дальше текст после слова «Хайзенберг» отправляется в Google GenAI (`google-genai`) в модель **`gemini-1.5-flash`** с заданной System Instruction (роль Хайзенберга).

## Структура проекта

- `main.py` — запуск бота и обработчики.
- `config.py` — загрузка переменных окружения.
- `.env` — шаблон ключей (заполни своими).
- `requirements.txt` — зависимости.
- `README.md` — эта инструкция.

## Переменные окружения

В `.env` должны быть:

- `BOT_TOKEN` — токен Telegram-бота (через `@BotFather`).
- `GOOGLE_API_KEY` — ключ Gemini Developer API (Google AI Studio).

## Локальный запуск (на ПК)

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# или .\.venv\Scripts\activate  # Windows PowerShell

pip install -r requirements.txt
python main.py
```

---

## Деплой на старый Android-телефон через Termux (подробный гайд)

Ниже — максимально практичная инструкция, как превратить старый Android (например, 4 ГБ ОЗУ) в сервер для Telegram-бота.

### 0) Что важно знать заранее

- Телефон должен иметь **стабильный интернет** (Wi‑Fi предпочтительнее).
- Для бота удобнее всего **Long Polling** (так и сделано) — не нужен публичный IP и HTTPS.
- Чтобы бот не “умирал”, нужно:
  - отключить оптимизацию батареи для Termux,
  - запускать процесс внутри `tmux`/`screen` или через `nohup`.

### 1) Установка Termux (правильный источник)

1. Установи **F-Droid** (магазин приложений с открытым ПО).
2. В F-Droid найди и установи **Termux**.

Почему так: версия Termux из Google Play часто устаревшая и может ломать установку пакетов.

### 2) Доступ к памяти и защита от “засыпания”

#### 2.1 Разрешить доступ к памяти

Открой Termux и выполни:

```bash
termux-setup-storage
```

Дай разрешение, которое попросит Android.

#### 2.2 Отключить оптимизацию батареи (обязательно)

На Android открой:

`Настройки` → `Приложения` → `Termux` → `Батарея`

И выбери что-то вроде:

- **Не ограничивать** / **Без ограничений** / **Don’t optimize**

Также полезно:

- отключить “Адаптивную батарею” для Termux,
- закрепить Termux в списке последних приложений (если прошивка это поддерживает).

### 3) Обновление пакетов и установка утилит

В Termux:

```bash
pkg update -y && pkg upgrade -y
pkg install -y python git nano
```

Проверка:

```bash
python --version
git --version
```

### 4) Клонирование репозитория и переход в папку

Выбери директорию, где будет проект (например, домашнюю):

```bash
cd ~
```

Шаблон команды клонирования:

```bash
git clone <ССЫЛКА_НА_ТВОЙ_РЕПОЗИТОРИЙ> heisenberg-bot
cd heisenberg-bot
```

Пример (замени на своё):

```bash
git clone https://github.com/username/heisenberg-bot.git heisenberg-bot
cd heisenberg-bot
```

### 5) Виртуальное окружение venv и установка зависимостей

Создай окружение:

```bash
python -m venv .venv
```

Активируй:

```bash
source .venv/bin/activate
```

Обнови pip и поставь зависимости:

```bash
pip install -U pip
pip install -r requirements.txt
```

### 6) Заполнение `.env` через nano

Открой `.env`:

```bash
nano .env
```

Впиши свои значения:

```env
BOT_TOKEN=123456:ABCDEF...
GOOGLE_API_KEY=AIzaSy...
```

Сохранить в nano:

- `Ctrl + O` → Enter
- `Ctrl + X`

### 7) Запуск бота в фоне, чтобы не отключался

Ниже — 3 варианта. Используй **один**.

#### Вариант A (рекомендуется): `tmux`

Установи:

```bash
pkg install -y tmux
```

Создай сессию:

```bash
tmux new -s heisenberg
```

Внутри tmux:

```bash
cd ~/heisenberg-bot
source .venv/bin/activate
python main.py
```

Как “отсоединиться” от tmux (бот продолжит работать):

- `Ctrl + B`, потом `D`

Как вернуться:

```bash
tmux attach -t heisenberg
```

#### Вариант B: `screen`

Установи:

```bash
pkg install -y screen
```

Запусти:

```bash
screen -S heisenberg
cd ~/heisenberg-bot
source .venv/bin/activate
python main.py
```

Отсоединиться:

- `Ctrl + A`, потом `D`

Вернуться:

```bash
screen -r heisenberg
```

#### Вариант C: `nohup` (самый простой)

```bash
cd ~/heisenberg-bot
source .venv/bin/activate
nohup python main.py > bot.log 2>&1 &
```

Посмотреть лог:

```bash
tail -n 200 bot.log
```

Остановить (найти PID и убить):

```bash
ps -ef | grep "python main.py"
kill <PID>
```

---

## Как использовать бота в группе

1. Добавь бота в **супергруппу**.
2. Дай ему право читать сообщения (обычно достаточно быть участником).
3. Пиши так:
   - `Хайзенберг, объясни разницу между ...`
   - `хайзенберг как сделать ...`

Если сообщение не начинается с обращения — бот молчит.

