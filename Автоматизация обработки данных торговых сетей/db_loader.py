import csv
import logging
import os
import re
import psycopg2
from config import *

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='UTF-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Database:
    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self):
        if self._connection is None:
            self._connection = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            self._cursor = self._connection.cursor()
            logger.info('Подключение к БД %s установлено', DB_NAME)

    @property
    def cursor(self):
        return self._cursor
    
    def commit(self):
        self._connection.commit()
    
    def close(self):
        if self._connection:
            self._cursor.close()
            self._connection.close()
            self._connection = None
            logger.info('Подключение к БД закрыто')

class DataLoader:
    def __init__(self):
        self.db = Database()

    def _is_valid_file(self, filename):
        return bool(re.match(r'^\d+_\d+\.csv$', filename))
    
    def _load_file(self, filepath):
        rows_loaded = 0

        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    self.db.cursor.execute(
                        '''INSERT INTO checks (doc_id, item, category, amount, price, discount)
                           VALUES (%s, %s, %s, %s, %s, %s)''',
                        (
                            row['doc_id'],
                            row['item'],
                            row['category'],
                            int(row['amount']),
                            float(row['price']),
                            float(row['discount'])
                        )
                    )
                    rows_loaded += 1
                except Exception as e:
                    logger.error('Ошибка при загрузке строки из %s: %s', filepath, e)
        
        self.db.commit()
        return rows_loaded
    
    def load_all(self):
        if not os.path.exists(OUTPUT_DIR):
            logger.warning('Папка %s не найдена', OUTPUT_DIR)
            return 
        
        files = os.listdir(OUTPUT_DIR)
        valid_files = [f for f in files if self._is_valid_file(f)]

        if not valid_files:
            logger.warning('Нет файлов для загрузки')
            return
        
        total_files = 0
        total_rows = 0

        for filename in valid_files:
            filepath = os.path.join(OUTPUT_DIR, filename)

            try:
                rows = self._load_file(filepath)
                total_files += 1
                total_rows += rows
                logger.info('Загружен: %s | %d строк', filename, rows)
            except Exception as e:
                logger.error('Ошибка при загрузке файла %s: %s', filename, e)

        logger.info('Загрузка завершена: %d файлов, %d строк', total_files, total_rows)


if __name__ == '__main__':
    try:
        db = Database()
        db.connect()

        loader = DataLoader()
        loader.load_all()

        db.close()
    except Exception as e:
        logger.exception('Критическая ошибка: %s', e)