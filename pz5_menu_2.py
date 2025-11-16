import sys
import requests
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTextEdit, QTabWidget, QFrame, QMessageBox, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Стилизация приложения
style_sheet = """
QMainWindow {
    background-color: #F5F5F5;
}

QWidget#Tabs {
    background-color: #FFFFFF;
    border-radius: 8px;
    margin: 10px;
}

QWidget#Side {
    background-color: #E8F4FD;
    border-radius: 8px;
    margin: 10px;
}

QLabel {
    color: #333333;
    font-family: "Arial";
}

QLabel#Header {
    background-color: #4CAF50;
    color: white;
    border-radius: 5px;
    padding: 8px;
    font-weight: bold;
    font-size: 14px;
}

QLineEdit {
    background-color: #FFFFFF;
    border: 2px solid #CCCCCC;
    border-radius: 5px;
    padding: 8px;
    font-size: 13px;
}

QLineEdit:focus {
    border-color: #4CAF50;
}

QPushButton {
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 10px 15px;
    font-weight: bold;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #45a049;
}

QPushButton:pressed {
    background-color: #3d8b40;
}

QTextEdit {
    background-color: #FFFFFF;
    border: 2px solid #CCCCCC;
    border-radius: 5px;
    padding: 10px;
    font-size: 13px;
    line-height: 1.4;
}

QGroupBox {
    font-weight: bold;
    font-size: 13px;
    color: #333333;
    border: 2px solid #CCCCCC;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 5px;
}
"""

class NutritionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Поиск калорийности продуктов")
        self.setFixedSize(800, 600)
        
        # Центральный виджет
        central_widget = QWidget()
        central_widget.setObjectName("Tabs")
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QHBoxLayout(central_widget)
        
        # Левая панель - вкладки поиска
        left_widget = QWidget()
        left_widget.setObjectName("Tabs")
        left_layout = QVBoxLayout(left_widget)
        
        # Заголовок приложения
        title_label = QLabel("ПОИСК КАЛОРИЙНОСТИ ПРОДУКТОВ")
        title_label.setObjectName("Header")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        left_layout.addWidget(title_label)
        
        # Создаем вкладки
        tabs = QTabWidget()
        tabs.setFont(QFont("Arial", 11))
        left_layout.addWidget(tabs)
        
        # Вкладка поиска по штрихкоду
        barcode_tab = self.createBarcodeTab()
        
        # Вкладка поиска по названию
        search_tab = self.createSearchTab()
        
        # Добавляем вкладки
        tabs.addTab(barcode_tab, "Поиск по штрихкоду")
        tabs.addTab(search_tab, "Поиск по названию")
        
        # Правая панель - результаты
        right_widget = QWidget()
        right_widget.setObjectName("Side")
        right_layout = QVBoxLayout(right_widget)
        
        # Заголовок для правой панели
        results_label = QLabel("РЕЗУЛЬТАТЫ ПОИСКА")
        results_label.setObjectName("Header")
        results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        right_layout.addWidget(results_label)
        
        # Область для отображения результатов
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setPlaceholderText("Здесь будут отображаться результаты вашего поиска...")
        
        right_layout.addWidget(self.results_display)
        
        # Добавляем обе панели в основной layout
        main_layout.addWidget(left_widget, 2)
        main_layout.addWidget(right_widget, 1)
    
    def createBarcodeTab(self):
        """Создает вкладку для поиска по штрихкоду"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Группа для поиска по штрихкоду
        barcode_group = QGroupBox("Поиск продукта по штрихкоду")
        barcode_layout = QVBoxLayout(barcode_group)
        
        # Поле для ввода штрихкода
        barcode_frame = QFrame()
        barcode_frame_layout = QHBoxLayout(barcode_frame)
        
        barcode_label = QLabel("Штрихкод:")
        barcode_label.setFont(QFont("Arial", 11))
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Например: 3017620422003 (Nutella)")
        self.barcode_input.setFont(QFont("Arial", 11))
        
        barcode_frame_layout.addWidget(barcode_label)
        barcode_frame_layout.addWidget(self.barcode_input)
        
        barcode_layout.addWidget(barcode_frame)
        
        # Кнопка поиска
        self.barcode_btn = QPushButton("Найти по штрихкоду")
        self.barcode_btn.clicked.connect(self.search_by_barcode)
        barcode_layout.addWidget(self.barcode_btn)
        
        # Примеры штрихкодов
        examples_label = QLabel("Примеры для теста:\n3017620422003 - Nutella\n5449000000996 - Coca-Cola\n7613032629994 - Nesquik")
        examples_label.setFont(QFont("Arial", 10))
        examples_label.setStyleSheet("color: #666; background-color: #f9f9f9; padding: 8px; border-radius: 5px;")
        
        layout.addWidget(barcode_group)
        layout.addWidget(examples_label)
        layout.addStretch()
        
        return tab
    
    def createSearchTab(self):
        """Создает вкладку для поиска по названию"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Группа для поиска по названию
        search_group = QGroupBox("Поиск продуктов по названию")
        search_layout = QVBoxLayout(search_group)
        
        # Поле для поиска
        search_frame = QFrame()
        search_frame_layout = QHBoxLayout(search_frame)
        
        search_label = QLabel("Название:")
        search_label.setFont(QFont("Arial", 11))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Например: apple, milk, bread...")
        self.search_input.setFont(QFont("Arial", 11))
        
        search_frame_layout.addWidget(search_label)
        search_frame_layout.addWidget(self.search_input)
        
        search_layout.addWidget(search_frame)
        
        # Кнопка поиска
        self.search_btn = QPushButton("Найти по названию")
        self.search_btn.clicked.connect(self.search_by_name)
        search_layout.addWidget(self.search_btn)
        
        # Примеры названий
        examples_label = QLabel("Примеры для теста:\napple, milk, bread, chocolate, yogurt")
        examples_label.setFont(QFont("Arial", 10))
        examples_label.setStyleSheet("color: #666; background-color: #f9f9f9; padding: 8px; border-radius: 5px;")
        
        layout.addWidget(search_group)
        layout.addWidget(examples_label)
        layout.addStretch()
        
        return tab
    
    def search_by_barcode(self):
        """Поиск продукта по штрихкоду"""
        barcode = self.barcode_input.text().strip()
        if not barcode:
            QMessageBox.warning(self, "Ошибка", "Введите штрихкод")
            return
        
        self.display_search_status("🔍 Поиск по штрихкоду...")
        
        try:
            # Показываем детальную информацию о запросе
            self.results_display.append(f"📡 Запрос штрихкода: {barcode}")
            
            result = self.get_product_by_barcode(barcode)
            
            if result and result.get("status") == 1 and result.get("product"):
                product = result["product"]
                self.display_single_product(product, "НАЙДЕННЫЙ ПРОДУКТ")
            else:
                error_msg = result.get("status_verbose", "Продукт не найден") if result else "Ошибка подключения"
                self.results_display.append(f"❌ {error_msg}")
                self.results_display.append("💡 Попробуйте другой штрихкод")
                
        except Exception as e:
            self.results_display.append(f"❌ Ошибка: {str(e)}")
            self.results_display.append("🔧 Проверьте подключение к интернету")
    
    def search_by_name(self):
        """Поиск продуктов по названию"""
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Ошибка", "Введите название продукта")
            return
        
        self.display_search_status(f"🔍 Поиск: '{query}'...")
        
        try:
            # Показываем детальную информацию о запросе
            self.results_display.append(f"📡 Запрос поиска: '{query}'")
            
            result = self.search_products(query, page_size=3)
            
            if result and result.get("products"):
                products = result.get("products", [])
                
                if products:
                    # Показываем первый результат
                    product = products[0]
                    self.display_single_product(product, f"РЕЗУЛЬТАТ ПОИСКА: '{query}'")
                    
                    # Если есть еще результаты, предлагаем их посмотреть
                    if len(products) > 1:
                        self.results_display.append(f"\n📋 Найдено еще {len(products)-1} продуктов")
                else:
                    self.results_display.append("❌ Продукты не найдены")
                    self.results_display.append("💡 Попробуйте изменить запрос")
            else:
                self.results_display.append("❌ Продукты не найдены")
                self.results_display.append("💡 Попробуйте другой запрос")
                
        except Exception as e:
            self.results_display.append(f"❌ Ошибка: {str(e)}")
            self.results_display.append("🔧 Проверьте подключение к интернету")
    
    def get_product_by_barcode(self, barcode):
        """Получение продукта по штрихкоду через Open Food Facts API"""
        try:
            url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
            self.results_display.append(f"🌐 Запрос к: {url}")
            
            response = requests.get(url, timeout=10)
            self.results_display.append(f"📊 Статус ответа: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.results_display.append(f"📦 Статус продукта: {data.get('status_verbose', 'N/A')}")
                return data
            else:
                self.results_display.append(f"❌ HTTP ошибка: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.results_display.append(f"❌ Ошибка сети: {e}")
            return None
        except Exception as e:
            self.results_display.append(f"❌ Неожиданная ошибка: {e}")
            return None
    
    def search_products(self, query, page_size=3):
        """Поиск продуктов по названию через Open Food Facts API"""
        try:
            url = f"https://world.openfoodfacts.org/cgi/search.pl"
            params = {
                'search_terms': query,
                'page_size': page_size,
                'json': 1
            }
            
            self.results_display.append(f"🌐 Поисковый запрос...")
            
            response = requests.get(url, params=params, timeout=10)
            self.results_display.append(f"📊 Статус ответа: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.results_display.append(f"📦 Найдено продуктов: {data.get('count', 0)}")
                return data
            else:
                self.results_display.append(f"❌ HTTP ошибка: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.results_display.append(f"❌ Ошибка сети: {e}")
            return None
        except Exception as e:
            self.results_display.append(f"❌ Неожиданная ошибка: {e}")
            return None
    
    def display_search_status(self, message):
        """Отображает статус поиска"""
        self.results_display.clear()
        self.results_display.append(message)
    
    def display_single_product(self, product, header):
        """Отображение информации об одном продукте"""
        self.results_display.clear()
        
        self.results_display.append(f"🎯 {header}")
        self.results_display.append("=" * 50)
        
        # Основная информация
        product_name = product.get('product_name', 'Не указано')
        brand = product.get('brands', 'Не указан')
        quantity = product.get('quantity', 'Не указана')
        
        self.results_display.append(f"🍎 <b>Название:</b> {product_name}")
        self.results_display.append(f"🏷️ <b>Бренд:</b> {brand}")
        
        if quantity != 'Не указана':
            self.results_display.append(f"📦 <b>Упаковка:</b> {quantity}")
        
        # Размер порции
        serving_size = product.get('serving_size')
        if serving_size:
            self.results_display.append(f"🍽️ <b>Размер порции:</b> {serving_size}")
        
        # Категория
        categories = product.get('categories')
        if categories:
            # Берем только первую категорию
            main_category = categories.split(',')[0].strip()
            self.results_display.append(f"📋 <b>Категория:</b> {main_category}")
        
        # Нутриенты
        nutriments = product.get("nutriments", {})
        if nutriments:
            self.results_display.append("\n📊 <b>ПИЩЕВАЯ ЦЕННОСТЬ:</b>")
            self.results_display.append("-" * 30)
            
            # Основные нутриенты для показа
            important_nutrients = {
                'energy-kcal_100g': 'Калории (на 100г)',
                'energy_100g': 'Энергия (на 100г)',
                'proteins_100g': 'Белки (на 100г)',
                'carbohydrates_100g': 'Углеводы (на 100г)',
                'sugars_100g': 'Сахар (на 100г)',
                'fat_100g': 'Жиры (на 100г)',
                'saturated-fat_100g': 'Насыщенные жиры (на 100г)',
                'fiber_100g': 'Клетчатка (на 100г)',
                'salt_100g': 'Соль (на 100г)',
                'sodium_100g': 'Натрий (на 100г)'
            }
            
            displayed_count = 0
            for key, description in important_nutrients.items():
                value = nutriments.get(key)
                if value is not None:
                    if 'energy' in key:
                        self.results_display.append(f"   • <b>{description}: {value}</b>")
                    else:
                        self.results_display.append(f"   • {description}: {value}")
                    displayed_count += 1
            
            if displayed_count == 0:
                self.results_display.append("   ⚠️ Основные нутриенты не указаны")
                
            # Показываем все доступные нутриенты для диагностики
            self.results_display.append(f"\n🔍 <i>Всего нутриентов в ответе: {len(nutriments)}</i>")
            
        else:
            self.results_display.append("\n⚠️ <b>Информация о пищевой ценности отсутствует</b>")
        
        # Ссылка на продукт
        if product.get('code'):
            self.results_display.append(f"\n🔗 <i>Код продукта: {product['code']}</i>")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)
    window = NutritionApp()
    window.show()
    sys.exit(app.exec())