# Головні новини — бот-звірка ukr.net vs glavred.info

Бот раз на N хвилин (за замовчуванням 30):

1. Бере три новини розділу «Головне» з ukr.net (напряму з
   `https://www.ukr.net/ajax/start.json` — сторінка ukr.net рендерить
   стрічку через JS, тому парсинг HTML не працює, а цей JSON-ендпоінт
   містить готові дані).
2. Бере останні 10 новин розділу «Головне за день» з
   `https://glavred.info/detail/main_news`.
3. Просить OpenAI (`chat.completions`, structured output) визначити, які
   з трьох новин ukr.net за змістом ще не висвітлені жодним із 10
   заголовків glavred (заголовки джерел часто сформульовані по-різному —
   порівняння рядків не підійшло б).
4. Якщо такі новини є (1, 2 або 3), надсилає в Telegram повідомлення (з
   випадковою вступною фразою зі списку в `src/notifier.py`):

   ```
   це нам цікаво?

   Заголовок першої новини (лінк)

   Заголовок другої новини (лінк)
   ```

   Заголовок — звичайний текст, клікабельне лише слово "лінк".

5. Щоб не дублювати те саме сповіщення щопівгодини, доки glavred не
   напише новину, бот запам'ятовує вже надіслані посилання в
   `state.json` (зберігаються 3 дні).

6. Працює лише в "робочі" години: будні 6:00–1:00, вихідні 7:00–23:00 за
   часом Europe/Kyiv (`src/schedule_window.py`, змінна `SCHEDULE_TIMEZONE`
   у `.env`, якщо потрібен інший часовий пояс). У GitHub Actions cron усе
   одно спрацьовує кожні 30 хв цілодобово, але поза цим вікном скрипт
   одразу завершується без звернень до ukr.net/glavred/OpenAI — тобто
   зайвих витрат на API вночі немає.

## Встановлення

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Заповніть `.env`:

- `TELEGRAM_BOT_TOKEN` — токен бота від [@BotFather](https://t.me/BotFather).
- `TELEGRAM_CHAT_ID` — id чату/каналу, куди писати (бот має бути доданий
  туди адміністратором; id можна дізнатись, наприклад, через
  [@userinfobot](https://t.me/userinfobot) або `getUpdates`).
- `OPENAI_API_KEY` — ключ [OpenAI API](https://platform.openai.com/account/api-keys).
- `OPENAI_MODEL` — модель для звірки (за замовчуванням `gpt-5-mini`).
  **Перевірте актуальну назву моделі на
  https://platform.openai.com/docs/models перед запуском** — на момент
  написання коду підтверджено існування `gpt-5-mini`, але лінійка
  моделей OpenAI оновлюється, і я не можу зі 100% впевненістю
  стверджувати, яка модель є найновішою на момент вашого запуску.

## Запуск через GitHub Actions (рекомендовано, не потребує сервера)

У репозиторії вже є `.github/workflows/news-bot.yml`: він запускається за
cron-розкладом раз на 30 хвилин (`*/30 * * * *`), одноразово виконує
`python -m src.run_once` і завершується — тобто фактично "крутиться" не
безперервним процесом, а короткими прогонами кожні півгодини, чого й
достатньо. Після кожного прогону, якщо `state.json` (список уже
надісланих новин) змінився, workflow сам комітить його назад у гілку —
завдяки цьому бот не дублює сповіщення про ту саму новину при наступних
запусках.

Для роботи потрібні **GitHub Actions secrets** у репозиторії
(Settings → Secrets and variables → Actions → New repository secret):

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `OPENAI_API_KEY`

Необов'язково — **Actions variable** (не secret, звичайна змінна) для
перевизначення моделі:

- `OPENAI_MODEL` (якщо не задати — використовується `gpt-5-mini` за
  замовчуванням)

Розклад cron у GitHub Actions спрацьовує не абсолютно точно щопівгодини
(може бути затримка на кілька хвилин під навантаженням інфраструктури
GitHub) — для цього завдання це не критично.

Перевірити вручну без очікування cron: вкладка **Actions** → workflow
**News comparison bot** → **Run workflow**.

## Локальний запуск (для розробки/тестування)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Заповніть `.env` тими самими значеннями, що й секрети вище, після чого:

```bash
python3 -m src.main
```

Бот працює у нескінченному циклі: раз на `CHECK_INTERVAL_MINUTES` хвилин
виконує перевірку, логує прогрес і за потреби пише в Telegram. Підходить
для запуску на власному сервері (не в GitHub Actions) — тоді для
production рекомендується systemd-юніт або Docker-контейнер із
`restart: always`.

### Приклад systemd-юніта (альтернатива GitHub Actions, для власного сервера)

```ini
[Unit]
Description=ukr.net vs glavred news bot
After=network.target

[Service]
WorkingDirectory=/opt/golovninovynystrichka
ExecStart=/opt/golovninovynystrichka/.venv/bin/python -m src.main
Restart=always
EnvironmentFile=/opt/golovninovynystrichka/.env

[Install]
WantedBy=multi-user.target
```

## Важливе застереження щодо джерел

- API `ukr.net/ajax/start.json` і верстка `glavred.info/detail/main_news`
  — неофіційні (публічно задокументованого API немає), тож обидва сайти
  можуть змінити структуру відповіді/сторінки без попередження. Якщо
  бот почне падати з помилкою «не вдалося знайти новини», перше, що
  варто перевірити — чи не змінилась розмітка/структура JSON.
- Я перевірив обидва джерела наживо під час розробки (16.09.2026) і
  підтвердив, що код витягує коректні заголовки й посилання.
