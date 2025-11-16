# file: off_rest_example.py
import requests
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTextEdit, QTabWidget, QFrame, QMessageBox)
from PyQt6.QtCore import Qt
import sys

BASE = "https://world.openfoodfacts.org"

HEADERS = {
    "User-Agent": "Darcons-Trade-CalorieFetcher/1.0 (+https://darcons-trade.example)"
}

def get_product_by_barcode(barcode: str, fields=None, lang="ru", country="ru") -> dict:
    """
    Получение конкретного продукта по штрихкоду (API v2).
    """
    if fields is None:
        fields = "code,product_name,nutriments,brands,quantity,serving_size,language,lang,lc"
    url = f"{BASE}/api/v2/product/{barcode}"
    params = {"fields": fields, "lc": lang, "cc": country}
    r = requests.get(url, headers=HEADERS, params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def search_products(query: str, page_size=5, fields=None, lang="ru", country="ru") -> dict:
    """
    Поиск продуктов по тексту (Search API v2).
    Пример фильтра: можно добавлять tags и условия по нутриентам.
    """
    if fields is None:
        fields = "code,product_name,brands,nutriments,quantity,serving_size,ecoscore_grade"
    url = f"{BASE}/api/v2/search"
    params = {
        "search_terms": query,
        "fields": fields,
        "page_size": page_size,
        "lc": lang,
        "cc": country,
    }
    r = requests.get(url, headers=HEADERS, params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def extract_kcal(nutriments: dict) -> dict:
    """
    Извлекает калорийность и БЖУ.
    Возвращает значения на 100 г и на порцию (если доступно).
    """
    get = nutriments.get
    data = {
        "kcal_100g": get("energy-kcal_100g") or get("energy-kcal_value"),
        "protein_100g": get("proteins_100g"),
        "fat_100g": get("fat_100g"),
        "carbs_100g": get("carbohydrates_100g"),
        "kcal_serving": get("energy-kcal_serving"),
        "protein_serving": get("proteins_serving"),
        "fat_serving": get("fat_serving"),
        "carbs_serving": get("carbohydrates_serving"),
    }
    return {k: v for k, v in data.items() if v is not None}

class NutritionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Поиск калорийности продуктов")
        self.setFixedSize(600, 500)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        layout = QVBoxLayout(central_widget)
        
        # Создаем вкладки
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Вкладка поиска по штрихкоду
        barcode_tab = QWidget()
        barcode_layout = QVBoxLayout(barcode_tab)
        
        # Поле для штрихкода
        barcode_frame = QFrame()
        barcode_frame_layout = QHBoxLayout(barcode_frame)
        barcode_frame_layout.addWidget(QLabel("Штрихкод:"))
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Введите штрихкод продукта...")
        barcode_frame_layout.addWidget(self.barcode_input)
        
        barcode_layout.addWidget(barcode_frame)
        
        # Кнопка поиска по штрихкоду
        self.barcode_btn = QPushButton("Найти по штрихкоду")
        self.barcode_btn.clicked.connect(self.search_by_barcode)
        barcode_layout.addWidget(self.barcode_btn)
        
        # Результат поиска по штрихкоду
        self.barcode_result = QTextEdit()
        self.barcode_result.setReadOnly(True)
        barcode_layout.addWidget(self.barcode_result)
        
        # Вкладка поиска по названию
        search_tab = QWidget()
        search_layout = QVBoxLayout(search_tab)
        
        # Поле для поиска
        search_frame = QFrame()
        search_frame_layout = QHBoxLayout(search_frame)
        search_frame_layout.addWidget(QLabel("Название:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите название продукта...")
        search_frame_layout.addWidget(self.search_input)
        
        search_layout.addWidget(search_frame)
        
        # Кнопка поиска по названию
        self.search_btn = QPushButton("Найти по названию")
        self.search_btn.clicked.connect(self.search_by_name)
        search_layout.addWidget(self.search_btn)
        
        # Результат поиска по названию
        self.search_result = QTextEdit()
        self.search_result.setReadOnly(True)
        search_layout.addWidget(self.search_result)
        
        # Добавляем вкладки
        tabs.addTab(barcode_tab, "Поиск по штрихкоду")
        tabs.addTab(search_tab, "Поиск по названию")
    
    def search_by_barcode(self):
        """Поиск продукта по штрихкоду"""
        barcode = self.barcode_input.text().strip()
        if not barcode:
            QMessageBox.warning(self, "Ошибка", "Введите штрихкод")
            return
        
        self.barcode_result.clear()
        self.barcode_result.append("Поиск...")
        
        try:
            result = get_product_by_barcode(barcode)
            
            if result.get("product"):
                product = result["product"]
                self.display_product_info(product, self.barcode_result)
            else:
                self.barcode_result.append("Продукт не найден")
                
        except Exception as e:
            self.barcode_result.append(f"Ошибка: {str(e)}")
    
    def search_by_name(self):
        """Поиск продуктов по названию"""
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Ошибка", "Введите название продукта")
            return
        
        self.search_result.clear()
        self.search_result.append("Поиск...")
        
        try:
            result = search_products(query, page_size=5)
            products = result.get("products", [])
            
            if not products:
                self.search_result.append("Продукты не найдены")
                return
            
            for i, product in enumerate(products, 1):
                self.search_result.append(f"\n{'='*50}")
                self.search_result.append(f"Результат {i}:")
                self.display_product_info(product, self.search_result)
                
        except Exception as e:
            self.search_result.append(f"Ошибка: {str(e)}")
    
    def display_product_info(self, product, text_widget):
        """Отображение информации о продукте"""
        # Основная информация
        text_widget.append(f"Название: {product.get('product_name', 'Не указано')}")
        text_widget.append(f"Бренд: {product.get('brands', 'Не указан')}")
        text_widget.append(f"Упаковка: {product.get('quantity', 'Не указана')}")
        text_widget.append(f"Порция: {product.get('serving_size', 'Не указана')}")
        
        # Нутриенты
        nutriments = extract_kcal(product.get("nutriments", {}))
        if nutriments:
            text_widget.append("\nПищевая ценность:")
            for key, value in nutriments.items():
                # Преобразуем ключи в читаемый вид
                readable_key = key.replace('_', ' ').replace('100g', 'на 100г').replace('serving', 'на порцию')
                text_widget.append(f"  {readable_key}: {value}")
        else:
            text_widget.append("\nИнформация о пищевой ценности отсутствует")

if __name__ == "__main__":
    """
    # Пример 1: по штрихкоду
    barcode = "5449000000996"  # Coca-Cola 0.33 л (пример; замените своим)
    prod = get_product_by_barcode(barcode)
    if prod.get("product"):
        p = prod["product"]
        print("Название:", p.get("product_name"))
        print("Бренд:", p.get("brands"))
        print("Упаковка:", p.get("quantity"))
        print("Порция:", p.get("serving_size"))
        print("Нутриенты:", extract_kcal(p.get("nutriments", {})))
    else:
        print("Продукт не найден")

    # Пример 2: поиск по названию
    res = search_products("творог 5%", page_size=3)
    for i, p in enumerate(res.get("products", []), 1):
        print(f"\nРезультат {i}:")
        print("Штрихкод:", p.get("code"))
        print("Название:", p.get("product_name"))
        print("Бренд:", p.get("brands"))
        print("Нутриенты:", extract_kcal(p.get("nutriments", {})))
    """

    app = QApplication(sys.argv)
    window = NutritionApp()
    window.show()
    sys.exit(app.exec())
