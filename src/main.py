from __future__ import annotations

import logging
import time

from . import comparator, config, notifier, schedule_window, state
from .sources import glavred, ukrnet

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("news-bot")


def run_once() -> None:
    if not schedule_window.is_active_now():
        log.info(
            "Поза робочими годинами бота (будні 6:00–1:00, вихідні 7:00–23:00 "
            "за %s) — пропускаю перевірку",
            config.SCHEDULE_TIMEZONE,
        )
        return

    log.info("Отримую топ-3 новини з ukr.net...")
    top3 = ukrnet.fetch_top3()
    for item in top3:
        log.info("  ukr.net: %s", item.title)

    log.info("Отримую останні новини з glavred.info...")
    latest10 = glavred.fetch_latest()
    for item in latest10:
        log.info("  glavred: %s", item.title)

    log.info("Звіряю заголовки через OpenAI (%s)...", config.OPENAI_MODEL)
    uncovered = comparator.find_uncovered(top3, latest10)

    if not uncovered:
        log.info("Усі топ-новини ukr.net уже висвітлені на glavred — нічого не надсилаю")
        return

    fresh_urls = state.filter_already_notified([item.url for item in uncovered])
    fresh = [item for item in uncovered if item.url in fresh_urls]

    if not fresh:
        log.info("Усі не висвітлені новини вже були надіслані раніше — пропускаю")
        return

    log.info("Надсилаю %d новин(и) у Telegram", len(fresh))
    notifier.send_uncovered_news(fresh)
    state.mark_notified([item.url for item in fresh])


def main() -> None:
    interval_seconds = config.CHECK_INTERVAL_MINUTES * 60
    log.info(
        "Старт бота. Перевірка кожні %d хв.", config.CHECK_INTERVAL_MINUTES
    )
    while True:
        try:
            run_once()
        except Exception:
            log.exception("Помилка під час циклу перевірки")
        time.sleep(interval_seconds)


if __name__ == "__main__":
    main()
