import sys
import requests
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTextEdit, QTabWidget, QFrame, QMessageBox, QGroupBox,
                             QScrollArea, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

# Стилизация приложения
style_sheet = """
QMainWindow {
    background-color: #F5F5F5;
}

QWidget#Tabs {
    background-color: #FFFFFF;
    border-radius: 8px;
    margin: 5px;
    padding: 5px;
}

QWidget#Side {
    background-color: #E8F4FD;
    border-radius: 8px;
    margin: 5px;
    padding: 5px;
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

QLabel#ProductHeader {
    background-color: #2196F3;
    color: white;
    border-radius: 5px;
    padding: 6px;
    font-weight: bold;
    font-size: 12px;
    margin: 2px;
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
    padding: 8px 12px;
    font-weight: bold;
    font-size: 12px;
    margin: 2px;
}

QPushButton:hover {
    background-color: #45a049;
}

QPushButton:pressed {
    background-color: #3d8b40;
}

QPushButton#Similar {
    background-color: #FF9800;
}

QPushButton#Similar:hover {
    background-color: #F57C00;
}

QTextEdit {
    background-color: #FFFFFF;
    border: 2px solid #CCCCCC;
    border-radius: 5px;
    padding: 8px;
    font-size: 12px;
    line-height: 1.4;
}

QGroupBox {
    font-weight: bold;
    font-size: 12px;
    color: #333333;
    border: 2px solid #CCCCCC;
    border-radius: 8px;
    margin-top: 8px;
    padding-top: 8px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 5px;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QWidget#SimilarProduct {
    background-color: #FFFFFF;
    border: 1px solid #DDDDDD;
    border-radius: 5px;
    padding: 8px;
    margin: 3px;
}

QProgressBar {
    border: 2px solid #CCCCCC;
    border-radius: 5px;
    text-align: center;
    color: white;
}

QProgressBar::chunk {
    background-color: #4CAF50;
    border-radius: 3px;
}
"""

class SearchThread(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, search_type, query):
        super().__init__()
        self.search_type = search_type
        self.query = query
    
    def run(self):
        try:
            if self.search_type == "barcode":
                result = self.get_product_by_barcode(self.query)
            else:
                result = self.search_products_by_name(self.query)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
    
    def get_product_by_barcode(self, barcode):
        """Получение продукта по штрихкоду"""
        try:
            print(f"🔍 Запрос штрихкода: {barcode}")
            url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
            response = requests.get(url, timeout=15)
            print(f"📊 Статус ответа: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📦 Статус продукта: {data.get('status_verbose', 'N/A')}")
                return data
            else:
                return {"error": f"HTTP ошибка: {response.status_code}"}
        except Exception as e:
            return {"error": f"Ошибка запроса: {str(e)}"}
    
    def search_products_by_name(self, query):
        """Поиск продуктов ТОЛЬКО по названию"""
        try:
            print(f"🔍 Поиск товара: '{query}'")
            url = "https://world.openfoodfacts.org/cgi/search.pl"
            params = {
                'search_terms': query,
                'page_size': 15,
                'json': 1,
                'search_simple': 1,
                'sort_by': 'unique_scans_n',
                'fields': 'code,product_name,brands,categories,quantity,serving_size,nutriments,product_name_en'
            }
            
            response = requests.get(url, params=params, timeout=15)
            print(f"📊 Статус ответа: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                products = data.get("products", [])
                
                # Фильтруем товары: оставляем только те, где название содержит искомое слово
                filtered_products = []
                query_lower = query.lower()
                
                for product in products:
                    product_name = product.get('product_name', '').lower()
                    product_name_en = product.get('product_name_en', '').lower()
                    
                    # Проверяем, содержит ли название искомое слово
                    if (query_lower in product_name or 
                        query_lower in product_name_en or
                        any(query_lower in word for word in product_name.split()) or
                        any(query_lower in word for word in product_name_en.split())):
                        filtered_products.append(product)
                
                print(f"📦 Найдено товаров: {len(products)}")
                print(f"🎯 Отфильтровано по названию: {len(filtered_products)}")
                
                data["products"] = filtered_products
                return data
            else:
                return {"error": f"HTTP ошибка: {response.status_code}"}
        except Exception as e:
            return {"error": f"Ошибка запроса: {str(e)}"}

class SimilarProductWidget(QWidget):
    def __init__(self, product, parent=None):
        super().__init__(parent)
        self.product = product
        self.parent = parent
        self.initUI()
    
    def initUI(self):
        self.setObjectName("SimilarProduct")
        layout = QVBoxLayout(self)
        
        # Название продукта
        product_name = self.product.get('product_name', 'Неизвестный продукт')
        if not product_name or product_name == 'None':
            product_name = self.product.get('product_name_en', 'Продукт без названия')
        
        if len(product_name) > 35:
            product_name = product_name[:35] + "..."
        
        name_label = QLabel(product_name)
        name_label.setObjectName("ProductHeader")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
        # Бренд
        brand = self.product.get('brands', '')
        if brand and brand != 'None':
            brand_label = QLabel(f"🏷️ {brand}")
            brand_label.setStyleSheet("color: #666; font-size: 11px;")
            layout.addWidget(brand_label)
        
        # Калории
        nutriments = self.product.get('nutriments', {})
        calories = nutriments.get('energy-kcal_100g')
        if calories:
            calories_label = QLabel(f"🔥 {calories} ккал/100г")
            calories_label.setStyleSheet("color: #E91E63; font-weight: bold; font-size: 11px;")
            layout.addWidget(calories_label)
        
        # Кнопка для просмотра деталей
        details_btn = QPushButton("Подробнее")
        details_btn.setObjectName("Similar")
        details_btn.clicked.connect(self.show_details)
        layout.addWidget(details_btn)
    
    def show_details(self):
        """Показать детали этого продукта в основном окне"""
        if self.parent:
            self.parent.display_single_product(self.product, "ВЫБРАННЫЙ ТОВАР")

class NutritionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_search_results = []
        self.search_thread = None
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Поиск товаров - по названию и штрихкоду")
        self.setFixedSize(1200, 700)
        
        # Центральный виджет
        central_widget = QWidget()
        central_widget.setObjectName("Tabs")
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Левая панель - поиск (25%)
        left_widget = QWidget()
        left_widget.setObjectName("Tabs")
        left_widget.setFixedWidth(300)
        left_layout = QVBoxLayout(left_widget)
        
        # Заголовок приложения
        title_label = QLabel("ПОИСК ТОВАРОВ")
        title_label.setObjectName("Header")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        
        left_layout.addWidget(title_label)
        
        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        left_layout.addWidget(self.progress_bar)
        
        # Создаем вкладки
        tabs = QTabWidget()
        tabs.setFont(QFont("Arial", 10))
        left_layout.addWidget(tabs)
        
        # Вкладка поиска по названию
        search_tab = self.createSearchTab()
        
        # Вкладка поиска по штрихкоду
        barcode_tab = self.createBarcodeTab()
        
        # Добавляем вкладки
        tabs.addTab(search_tab, "По названию")
        tabs.addTab(barcode_tab, "По штрихкоду")
        
        # Статистика
        self.stats_label = QLabel("🔍 Выберите способ поиска")
        self.stats_label.setStyleSheet("color: #666; font-size: 10px; padding: 5px; background-color: #f9f9f9; border-radius: 5px;")
        self.stats_label.setWordWrap(True)
        left_layout.addWidget(self.stats_label)
        
        left_layout.addStretch()
        
        # Центральная панель - основной результат (35%)
        center_widget = QWidget()
        center_widget.setObjectName("Tabs")
        center_layout = QVBoxLayout(center_widget)
        
        # Заголовок для центральной панели
        results_label = QLabel("ОСНОВНОЙ ТОВАР")
        results_label.setObjectName("Header")
        results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        center_layout.addWidget(results_label)
        
        # Область для отображения основного результата
        self.main_result_display = QTextEdit()
        self.main_result_display.setReadOnly(True)
        self.main_result_display.setPlaceholderText("Здесь будет отображаться информация о найденном товаре...")
        
        center_layout.addWidget(self.main_result_display)
        
        # Правая панель - найденные товары (40%)
        right_widget = QWidget()
        right_widget.setObjectName("Side")
        right_layout = QVBoxLayout(right_widget)
        
        # Заголовок для правой панели
        similar_label = QLabel("НАЙДЕННЫЕ ТОВАРЫ")
        similar_label.setObjectName("Header")
        similar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        right_layout.addWidget(similar_label)
        
        # Scroll area для товаров
        self.products_scroll = QScrollArea()
        self.products_scroll.setWidgetResizable(True)
        self.products_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.products_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Контейнер для товаров
        self.products_container = QWidget()
        self.products_layout = QVBoxLayout(self.products_container)
        self.products_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.products_scroll.setWidget(self.products_container)
        right_layout.addWidget(self.products_scroll)
        
        # Добавляем все панели в основной layout
        main_layout.addWidget(left_widget)      # 25% - поиск
        main_layout.addWidget(center_widget)    # 35% - основной результат
        main_layout.addWidget(right_widget)     # 40% - найденные товары
    
    def createSearchTab(self):
        """Создает вкладку для поиска по названию"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Группа для поиска по названию
        search_group = QGroupBox("Поиск товара по названию")
        search_layout = QVBoxLayout(search_group)
        
        # Поле для поиска
        search_frame = QFrame()
        search_frame_layout = QHBoxLayout(search_frame)
        
        search_label = QLabel("Название:")
        search_label.setFont(QFont("Arial", 10))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите название товара...")
        self.search_input.setFont(QFont("Arial", 10))
        self.search_input.returnPressed.connect(lambda: self.search_by_name())
        
        search_frame_layout.addWidget(search_label)
        search_frame_layout.addWidget(self.search_input)
        
        search_layout.addWidget(search_frame)
        
        # Кнопка поиска
        self.search_btn = QPushButton("Найти по названию")
        self.search_btn.clicked.connect(lambda: self.search_by_name())
        search_layout.addWidget(self.search_btn)
        
        layout.addWidget(search_group)
        
        # Примеры названий
        examples_label = QLabel("📋 Примеры поиска:\n• apple - яблоки\n• milk - молоко\n• bread - хлеб\n• chocolate - шоколад\n• pasta - паста\n• cheese - сыр\n• yogurt - йогурт\n• juice - сок\n• water - вода\n• rice - рис")
        examples_label.setFont(QFont("Arial", 9))
        examples_label.setStyleSheet("color: #666; background-color: #f9f9f9; padding: 10px; border-radius: 5px;")
        examples_label.setWordWrap(True)
        
        layout.addWidget(examples_label)
        layout.addStretch()
        
        return tab
    
    def createBarcodeTab(self):
        """Создает вкладку для поиска по штрихкоду"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Группа для поиска по штрихкоду
        barcode_group = QGroupBox("Поиск товара по штрихкоду")
        barcode_layout = QVBoxLayout(barcode_group)
        
        # Поле для ввода штрихкода
        barcode_frame = QFrame()
        barcode_frame_layout = QHBoxLayout(barcode_frame)
        
        barcode_label = QLabel("Штрихкод:")
        barcode_label.setFont(QFont("Arial", 10))
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Введите штрихкод...")
        self.barcode_input.setFont(QFont("Arial", 10))
        self.barcode_input.returnPressed.connect(lambda: self.search_by_barcode())
        
        barcode_frame_layout.addWidget(barcode_label)
        barcode_frame_layout.addWidget(self.barcode_input)
        
        barcode_layout.addWidget(barcode_frame)
        
        # Кнопка поиска
        self.barcode_btn = QPushButton("Найти по штрихкоду")
        self.barcode_btn.clicked.connect(lambda: self.search_by_barcode())
        barcode_layout.addWidget(self.barcode_btn)
        
        layout.addWidget(barcode_group)
        
        # Примеры штрихкодов
        examples_label = QLabel("📋 Рабочие штрихкоды:\n• 3017620422003 - Nutella\n• 5449000000996 - Coca-Cola\n• 7613032629994 - Nesquik\n• 5000159459224 - KitKat\n• 3017620402673 - Ferrero Rocher\n• 8000500310427 - Barilla Pasta")
        examples_label.setFont(QFont("Arial", 9))
        examples_label.setStyleSheet("color: #666; background-color: #f9f9f9; padding: 10px; border-radius: 5px;")
        examples_label.setWordWrap(True)
        
        layout.addWidget(examples_label)
        layout.addStretch()
        
        return tab
    
    def search_by_name(self):
        """Поиск товаров по названию"""
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Ошибка", "Введите название товара")
            return
        
        self.start_search("name", query)
    
    def search_by_barcode(self):
        """Поиск товара по штрихкоду"""
        barcode = self.barcode_input.text().strip()
        if not barcode:
            QMessageBox.warning(self, "Ошибка", "Введите штрихкод")
            return
        
        self.start_search("barcode", barcode)
    
    def start_search(self, search_type, query):
        """Запуск поиска в отдельном потоке"""
        if self.search_thread and self.search_thread.isRunning():
            self.search_thread.terminate()
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        if search_type == "name":
            self.display_search_status(f"🔍 Ищем товары: '{query}'...")
            self.stats_label.setText(f"🔍 Поиск по названию: '{query}'")
        else:
            self.display_search_status(f"🔍 Ищем товар по штрихкоду: {query}...")
            self.stats_label.setText(f"🔍 Поиск по штрихкоду: {query}")
        
        self.clear_products()
        
        self.search_thread = SearchThread(search_type, query)
        self.search_thread.finished.connect(self.on_search_finished)
        self.search_thread.error.connect(self.on_search_error)
        self.search_thread.start()
    
    def on_search_finished(self, result):
        """Обработка завершения поиска"""
        self.progress_bar.setVisible(False)
        
        if "error" in result:
            self.main_result_display.append(f"❌ {result['error']}")
            self.stats_label.setText("❌ Ошибка при поиске")
            return
        
        # Обработка поиска по штрихкоду
        if result.get("status") == 1 and result.get("product"):
            product = result["product"]
            self.display_single_product(product, "НАЙДЕННЫЙ ТОВАР")
            self.stats_label.setText(f"✅ Товар найден по штрихкоду\n📦 {product.get('product_name', 'Неизвестно')}")
            
            # Для штрихкода ищем похожие товары по категории
            self.find_similar_products(product)
        
        # Обработка поиска по названию
        elif result.get("products"):
            products = result.get("products", [])
            self.current_search_results = products
            
            if products:
                self.stats_label.setText(f"✅ Найдено товаров: {len(products)}\n🔍 По названию: '{self.search_input.text()}'")
                
                # Показываем первый товар как основной
                main_product = products[0]
                self.display_single_product(main_product, f"ТОВАР: {self.search_input.text().title()}")
                
                # Показываем все остальные товары в правой панели
                self.show_all_products(products)
            else:
                self.main_result_display.append("❌ Товары не найдены")
                self.stats_label.setText("❌ Товары не найдены")
                self.add_products_message("Товары не найдены. Попробуйте другой запрос.")
        else:
            self.main_result_display.append("❌ Товар не найден")
            self.stats_label.setText("❌ Товар не найден")
            self.add_products_message("Товар не найден. Проверьте штрихкод или название.")
    
    def find_similar_products(self, product):
        """Поиск похожих товаров по категории (для штрихкода)"""
        categories = product.get('categories')
        if categories:
            main_category = categories.split(',')[0].strip()
            if main_category:
                try:
                    # Ищем товары из той же категории
                    url = "https://world.openfoodfacts.org/cgi/search.pl"
                    params = {
                        'search_terms': main_category,
                        'page_size': 10,
                        'json': 1,
                        'fields': 'code,product_name,brands,categories,quantity,serving_size,nutriments'
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        similar_products = data.get("products", [])
                        
                        # Убираем текущий продукт из похожих
                        current_code = product.get('code')
                        similar_products = [p for p in similar_products if p.get('code') != current_code]
                        
                        if similar_products:
                            self.show_all_products(similar_products[:8], "ПОХОЖИЕ ТОВАРЫ")
                        else:
                            self.add_products_message("Похожие товары не найдены")
                except Exception as e:
                    self.add_products_message("Не удалось найти похожие товары")
    
    def on_search_error(self, error_message):
        """Обработка ошибки поиска"""
        self.progress_bar.setVisible(False)
        self.main_result_display.append(f"❌ Ошибка: {error_message}")
        self.main_result_display.append("🔧 Проверьте подключение к интернету")
        self.stats_label.setText("❌ Ошибка сети")
    
    def show_all_products(self, products, title="НАЙДЕННЫЕ ТОВАРЫ"):
        """Отображает все найденные товары в правой панели"""
        if not products:
            self.add_products_message("Товары не найдены")
            return
        
        # Добавляем заголовок
        title_label = QLabel(f"{title} ({len(products)})")
        title_label.setStyleSheet("font-weight: bold; color: #2196F3; font-size: 12px; margin: 5px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.products_layout.addWidget(title_label)
        
        # Добавляем товары
        for i, product in enumerate(products):
            product_widget = SimilarProductWidget(product, self)
            self.products_layout.addWidget(product_widget)
    
    def add_products_message(self, message):
        """Добавляет сообщение в панель товаров"""
        message_label = QLabel(message)
        message_label.setStyleSheet("color: #666; font-style: italic; margin: 10px;")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.products_layout.addWidget(message_label)
    
    def clear_products(self):
        """Очищает панель товаров"""
        while self.products_layout.count():
            child = self.products_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def display_search_status(self, message):
        """Отображает статус поиска"""
        self.main_result_display.clear()
        self.main_result_display.append(message)
    
    def display_single_product(self, product, header):
        """Отображение информации об одном товаре"""
        self.main_result_display.clear()
        
        self.main_result_display.append(f"🎯 {header}")
        self.main_result_display.append("=" * 50)
        
        # Название товара
        product_name = product.get('product_name', 'Не указано')
        if not product_name or product_name == 'None':
            product_name = product.get('product_name_en', 'Не указано')
        
        self.main_result_display.append(f"🍎 <b>Название:</b> {product_name}")
        
        # Бренд
        brand = product.get('brands', 'Не указан')
        if brand and brand != 'None':
            self.main_result_display.append(f"🏷️ <b>Бренд:</b> {brand}")
        
        # Штрихкод (если есть)
        code = product.get('code')
        if code:
            self.main_result_display.append(f"📱 <b>Штрихкод:</b> {code}")
        
        # Упаковка
        quantity = product.get('quantity')
        if quantity:
            self.main_result_display.append(f"📦 <b>Упаковка:</b> {quantity}")
        
        # Размер порции
        serving_size = product.get('serving_size')
        if serving_size:
            self.main_result_display.append(f"🍽️ <b>Размер порции:</b> {serving_size}")
        
        # Категория
        categories = product.get('categories')
        if categories:
            main_category = categories.split(',')[0].strip()
            self.main_result_display.append(f"📋 <b>Категория:</b> {main_category}")
        
        # Пищевая ценность
        nutriments = product.get("nutriments", {})
        if nutriments:
            self.main_result_display.append("\n📊 <b>ПИЩЕВАЯ ЦЕННОСТЬ (на 100г):</b>")
            self.main_result_display.append("-" * 30)
            
            # Основные нутриенты
            nutrients_to_show = {
                'energy-kcal_100g': ('🔥 Калории', '#E91E63'),
                'proteins_100g': ('🥚 Белки', '#4CAF50'),
                'carbohydrates_100g': ('🍞 Углеводы', '#FF9800'),
                'sugars_100g': ('🍭 Сахар', '#9C27B0'),
                'fat_100g': ('🥑 Жиры', '#795548'),
                'fiber_100g': ('🌾 Клетчатка', '#8BC34A'),
                'salt_100g': ('🧂 Соль', '#607D8B')
            }
            
            for key, (name, color) in nutrients_to_show.items():
                value = nutriments.get(key)
                if value is not None:
                    self.main_result_display.append(f"<span style='color: {color};'>   • {name}: <b>{value}</b></span>")
            
        else:
            self.main_result_display.append("\n⚠️ <b>Информация о пищевой ценности отсутствует</b>")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)
    window = NutritionApp()
    window.show()
    sys.exit(app.exec())