import csv
import logging
import os
import random
from datetime import datetime
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


class ProductCatalog:
    def __init__(self):
        self._products = PRODUCTS
        self._price_ranges = PRICE_RANGES
        logger.info('Каталог товаров загружен: %d категорий', len(self._products))

    def get_random_category(self):
        category = random.choice(list(self._products.keys()))
        return category
    
    def get_random_product(self, category):
        product = random.choice(self._products[category])
        return product

    def generate_price(self, category):
        min_price, max_price = self._price_ranges[category]
        price = round(random.uniform(min_price, max_price), 2)
        return price
    

class CashRegister:
    def __init__(self, shop_num, cash_num, catalog):
        self.shop_num = shop_num
        self.cash_num = cash_num
        self.catalog = catalog

    def _generate_discount(self, price, amount):
        if random.random() < DISCOUNT_PROBABILITY:
            full_price = price * amount
            max_discount = full_price * (MAX_DISCOUNT_PERCENT / 100)
            discount = round(random.uniform(1, max(max_discount, 1)), 2)
            return discount
        return 0.0
    
    def generate_receipts(self, date_str):
        num_receipts = random.randint(*RECEIPTS_PER_CASH)
        all_rows = []

        logger.info('SHOP%d_CASH%d: старт генерации %d чеков',
                    self.shop_num, self.cash_num, num_receipts)
        
        for receipt_num in range(1, num_receipts + 1):
            doc_id = f'SHOP{self.shop_num:02d}-{date_str}-{receipt_num:04d}'
            num_items = random.randint(*ITEMS_PER_RECEIPT)

            for _ in range(num_items):
                try:
                    category = self.catalog.get_random_category()
                    item = self.catalog.get_random_product(category)
                    amount = random.randint(1, 5)
                    price = self.catalog.generate_price(category)
                    discount = self._generate_discount(price, amount)

                    all_rows.append({
                        'doc_id': doc_id,
                        'item': item,
                        'category': category,
                        'amount': amount,
                        'price': price,
                        'discount': discount
                    })
                except Exception as e:
                    logger.error('Ошибка при генерации позиции чека %s: %s', doc_id, e)

        logger.info("SHOP%d_CASH%d: готово — %d строк, %d чеков",
                    self.shop_num, self.cash_num, len(all_rows), num_receipts)
        return all_rows
    
    def get_filename(self):
        return f'{self.shop_num}_{self.cash_num}.csv'
    

class Shop:
    def __init__(self, shop_num, catalog):
        self.shop_num = shop_num
        num_cashes = random.randint(*CASHES_PER_SHOP)

        logger.info('SHOP%d: создаётся с %d кассами', shop_num, num_cashes)

        self.cash_registers = []
        for i in range(1, num_cashes + 1):
            self.cash_registers.append(CashRegister(shop_num, i, catalog))

    def generate_all_data(self, date_str):
        shop_data = {}
        for cash in self.cash_registers:
            filename = cash.get_filename()
            rows = cash.generate_receipts(date_str)
            shop_data[filename] = rows
        return shop_data
    


class DataGenerator:
    def __init__(self):
        logger.info('=' * 40)
        logger.info('Инициализация генератора данных')
        self.catalog = ProductCatalog()
        self.shops = []
        
        for i in range(1, NUM_SHOPS + 1):
            self.shops.append(Shop(i, self.catalog))
        logger.info('Создано магазинов: %d', len(self.shops))

    def clean_old_logs(self, days=3):
        log_path = LOG_FILE
        
        if not os.path.exists(log_path):
            return
        
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except IOError:
            return
        
        new_lines = []
        for line in lines:
            try:
                log_date_str = line[:10]
                log_date = datetime.strptime(log_date_str, "%Y-%m-%d")
                if log_date >= cutoff_date:
                    new_lines.append(line)
            except ValueError:
                new_lines.append(line)
        
        with open(log_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        removed = len(lines) - len(new_lines)
        logger.info('Очищено %d старых строк из лога', removed)

    def generate(self):
        self.clean_old_logs(days=3)
        
        try:
            os.makedirs(OUTPUT_DIR, exist_ok=True)
        except OSError as e:
            logger.error('Не могу создать папку %s: %s', OUTPUT_DIR, e)
            return
        
        date_str = datetime.now().strftime('%Y%m%d')
        total_files = 0

        logger.info('Начало генерации данных за %s', date_str)

        for shop in self.shops:
            try:
                shop_data = shop.generate_all_data(date_str)

                for filename, rows in shop_data.items():
                    filepath = os.path.join(OUTPUT_DIR, filename)
                    self._write_csv(filepath, rows)

                    total_files += 1
                    unique_receipts = len(set(row['doc_id'] for row in rows))
                    logger.info('Сохранён: %s | %d строк | %d чеков',
                                filename, len(rows), unique_receipts)
            except Exception as e:
                logger.error('Ошибка при обработке магазина %d: %s',
                             shop.shop_num, e)
        
        logger.info("Готово! %d файлов в %s/", total_files, OUTPUT_DIR)
        logger.info("=" * 40)

    def _write_csv(self, filepath, rows):
        try:
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['doc_id', 'item', 'category',
                                'amount', 'price', 'discount']
                )
                writer.writeheader()
                writer.writerows(rows)
        except IOError as e:
            logger.error('Ошибка записи файла %s: %s', filepath, e)
            raise         


if __name__ == '__main__':
    try:
        generator = DataGenerator()
        generator.generate()
    except Exception as e:
        logger.exception('Критическая ошибка: %s', e)