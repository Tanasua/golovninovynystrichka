"""Одноразовий запуск циклу перевірки — для планувальників (напр. GitHub
Actions cron), на відміну від src.main, який крутиться у нескінченному
циклі сам."""
from .main import run_once

if __name__ == "__main__":
    run_once()
