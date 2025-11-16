import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTextEdit, QTabWidget, QFrame, QMessageBox, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
from main import get_product_by_barcode, search_products, extract_kcal

# Стилизация приложения в соответствии с главой 6
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

QPushButton#Warning {
    background-color: #FF9800;
}

QPushButton#Warning:hover {
    background-color: #F57C00;
}

QPushButton#Warning:pressed {
    background-color: #EF6C00;
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

QTabWidget::pane {
    border: 1px solid #CCCCCC;
    border-radius: 8px;
    background-color: #FFFFFF;
}

QTabWidget::tab-bar {
    alignment: center;
}

QTabBar::tab {
    background-color: #E0E0E0;
    color: #333333;
    padding: 8px 16px;
    margin: 2px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
}

QTabBar::tab:selected {
    background-color: #4CAF50;
    color: white;
}

QTabBar::tab:hover:!selected {
    background-color: #BDBDBD;
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
        
        # Правая панель - история/результаты
        right_widget = QWidget()
        right_widget.setObjectName("Side")
        right_layout = QVBoxLayout(right_widget)
        
        # Заголовок для правой панели
        history_label = QLabel("РЕЗУЛЬТАТЫ ПОИСКА")
        history_label.setObjectName("Header")
        history_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        right_layout.addWidget(history_label)
        
        # Область для отображения результатов
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setPlaceholderText("Здесь будут отображаться результаты вашего поиска...")
        
        right_layout.addWidget(self.results_display)
        
        # Добавляем обе панели в основной layout
        main_layout.addWidget(left_widget, 2)  # Левая панель занимает 2/3
        main_layout.addWidget(right_widget, 1)  # Правая панель занимает 1/3
    
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
        self.barcode_input.setPlaceholderText("Введите штрихкод продукта...")
        self.barcode_input.setFont(QFont("Arial", 11))
        
        barcode_frame_layout.addWidget(barcode_label)
        barcode_frame_layout.addWidget(self.barcode_input)
        
        barcode_layout.addWidget(barcode_frame)
        
        # Кнопка поиска
        self.barcode_btn = QPushButton("Найти по штрихкоду")
        self.barcode_btn.clicked.connect(self.search_by_barcode)
        barcode_layout.addWidget(self.barcode_btn)
        
        layout.addWidget(barcode_group)
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
        self.search_input.setPlaceholderText("Введите название продукта...")
        self.search_input.setFont(QFont("Arial", 11))
        
        search_frame_layout.addWidget(search_label)
        search_frame_layout.addWidget(self.search_input)
        
        search_layout.addWidget(search_frame)
        
        # Кнопка поиска
        self.search_btn = QPushButton("Найти по названию")
        self.search_btn.clicked.connect(self.search_by_name)
        search_layout.addWidget(self.search_btn)
        
        layout.addWidget(search_group)
        layout.addStretch()
        
        return tab
    
    def search_by_barcode(self):
        """Поиск продукта по штрихкоду"""
        barcode = self.barcode_input.text().strip()
        if not barcode:
            QMessageBox.warning(self, "Ошибка", "Введите штрихкод")
            return
        
        self.display_search_status("Поиск по штрихкоду...")
        
        try:
            result = get_product_by_barcode(barcode)
            
            if result.get("product"):
                product = result["product"]
                self.display_product_info(product, "РЕЗУЛЬТАТ ПОИСКА ПО ШТРИХКОДУ")
            else:
                self.results_display.append("❌ Продукт не найден")
                
        except Exception as e:
            self.results_display.append(f"❌ Ошибка: {str(e)}")
    
    def search_by_name(self):
        """Поиск продуктов по названию"""
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Ошибка", "Введите название продукта")
            return
        
        self.display_search_status("Поиск по названию...")
        
        try:
            result = search_products(query, page_size=5)
            products = result.get("products", [])
            
            if not products:
                self.results_display.append("❌ Продукты не найдены")
                return
            
            self.display_multiple_products(products, query)
                
        except Exception as e:
            self.results_display.append(f"❌ Ошибка: {str(e)}")
    
    def display_search_status(self, message):
        """Отображает статус поиска"""
        self.results_display.clear()
        self.results_display.append(f"🔍 {message}")
    
    def display_multiple_products(self, products, query):
        """Отображает несколько найденных продуктов"""
        self.results_display.clear()
        self.results_display.append(f"📋 Найдено продуктов по запросу '{query}': {len(products)}\n")
        
        for i, product in enumerate(products, 1):
            self.results_display.append(f"{'='*60}")
            self.results_display.append(f"📦 Результат {i}:")
            self.display_product_info(product, "")
    
    def display_product_info(self, product, header):
        """Отображение информации о продукте"""
        if header:
            self.results_display.append(f"\n🎯 {header}")
            self.results_display.append("="*50)
        
        # Основная информация
        self.results_display.append(f"🍎 Название: {product.get('product_name', 'Не указано')}")
        self.results_display.append(f"🏷️ Бренд: {product.get('brands', 'Не указан')}")
        self.results_display.append(f"📦 Упаковка: {product.get('quantity', 'Не указана')}")
        self.results_display.append(f"🍽️ Порция: {product.get('serving_size', 'Не указана')}")
        
        # Нутриенты
        nutriments = extract_kcal(product.get("nutriments", {}))
        if nutriments:
            self.results_display.append("\n📊 Пищевая ценность:")
            for key, value in nutriments.items():
                # Преобразуем ключи в читаемый вид
                readable_key = key.replace('_', ' ').replace('100g', 'на 100г').replace('serving', 'на порцию')
                self.results_display.append(f"   • {readable_key}: {value}")
        else:
            self.results_display.append("\n⚠️ Информация о пищевой ценности отсутствует")
        
        self.results_display.append("\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)
    window = NutritionApp()
    window.show()
    sys.exit(app.exec())