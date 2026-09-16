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
4. Якщо такі новини є (1, 2 або 3), надсилає в Telegram повідомлення:

   ```
   нам це цікаво?

   <заголовок 1 із лінком на ukr.net>
   <заголовок 2 із лінком на ukr.net>
   ```

5. Щоб не дублювати те саме сповіщення щопівгодини, доки glavred не
   напише новину, бот запам'ятовує вже надіслані посилання в
   `state.json` (зберігаються 3 дні).

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

## Запуск

```bash
python3 -m src.main
```

Бот працює у нескінченному циклі: раз на `CHECK_INTERVAL_MINUTES` хвилин
виконує перевірку, логує прогрес і за потреби пише в Telegram.

Для продакшн-запуску рекомендується systemd-юніт або Docker-контейнер із
`restart: always`, оскільки скрипт — це довготривалий процес, а не
одноразовий запуск.

### Приклад systemd-юніта

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
