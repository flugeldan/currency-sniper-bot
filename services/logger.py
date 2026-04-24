import logging

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),  # в консоль
            logging.FileHandler("bot.log", encoding="utf-8")  # в файл
        ]
    )

def get_logger(name: str):
    return logging.getLogger(name)