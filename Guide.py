 # food_order.py
 # Импортируем необходимые модули
import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel,
    QPushButton, QRadioButton, QButtonGroup, QTabWidget,
    QGroupBox, QVBoxLayout, QHBoxLayout, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initializeUI()
    def initializeUI(self):
        """Настройте графический интерфейс приложения."""
        self.setMinimumSize(700, 700)
        self.setWindowTitle("6.1 - GUI заказа еды")
        #self.setUpMainWindow()
        self.show()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

     # food_order.py
# Настройка таблицы стилей для всего графического интерфейса пользователя
style_sheet = """
QWidget{
    background-color: #C92108;
    }
    QWidget#Tabs{
        background-color: #FCEBCD;
        border-radius: 4px
    }
    QWidget#ImageBorder{
        background-color: #FCF9F3;
        border-width: 2px;
        border-style: solid;
        border-radius: 4px;
        border-color: #FABB4C
    }
    QWidget#Side{
        background-color: #EFD096;
        border-radius: 4px
    }

    # food_order.py
    QLabel{
        background-color: #EFD096;
        border-width: 2px;
        border-style: solid;
        border-radius: 4px;
        border-color: #EFD096
    }
    QLabel#Header{
        background-color: #EFD096;
        border-width: 2px;
        border-style: solid;
        border-radius: 4px;
        border-color: #EFD096;
        padding-left: 10px;
        color: #961A07
    }
    QLabel#ImageInfo{
        background-color: #FCF9F3;
        border-radius: 4px;
    }
    QGroupBox{
        background-color: #FCEBCD;
        color: #961A07
    }
    QRadioButton{
        background-color: #FCF9F3
    }
    QPushButton{
        background-color: #C92108;
        border-radius: 4px;
        padding: 6px;
        color: #FFFFFF
    }
    QPushButton:pressed{
        background-color: #C86354;
        border-radius: 4px;
        padding: 6px;
        color: #DFD8D7
    }
 """
# food_order.py
def setUpMainWindow(self):
    """Создайте и расположите виджеты в главном окне."""
    # Создайте панель вкладок, различные вкладки и задайте имена объектов
    self.tab_bar = QTabWidget()
    self.pizza_tab = QWidget()
    self.pizza_tab.setObjectName("Tabs")
    self.wings_tab = QWidget()
    self.wings_tab.setObjectName("Tabs")
    self.tab_bar.addTab(self.pizza_tab, "Пицца")
    self.tab_bar.addTab(self.wings_tab, "Крылышки")
    # Вызов методов, содержащих виджеты для каждой вкладки
    self.pizzaTab()
    self.wingsTab()

# food_order.py
        # Создание боковой панели в главном окне
    self.side_widget = QWidget()
    self.side_widget.setObjectName("Tabs")
    order_label = QLabel("ВАШ ЗАКАЗ")
    order_label.setObjectName("Header")
    items_box = QWidget()
    items_box.setObjectName("Side")
    pizza_label = QLabel("Тип пиццы: ")
    self.display_pizza_label = QLabel("")
    toppings_label = QLabel("Начинки: ")
    self.display_toppings_label = QLabel("")
    extra_label = QLabel("Дополнительно: ")
    self.display_wings_label = QLabel("")
    # Установите расположение сетки для объектов в боковом виджете
    items_grid = QGridLayout()
    items_grid.addWidget(pizza_label, 0, 0,
        Qt.AlignmentFlag.AlignRight)
    items_grid.addWidget(self.display_pizza_label, 0, 1)
    items_grid.addWidget(toppings_label, 1, 0,
        Qt.AlignmentFlag.AlignRight)
    items_grid.addWidget(self.display_toppings_label,
        1, 1)
    items_grid.addWidget(extra_label, 2, 0,
        Qt.AlignmentFlag.AlignRight)
    items_grid.addWidget(self.display_wings_label, 2, 1)
    items_box.setLayout(items_grid)
 # food_order.py
    # Установите основной макет для бокового виджета
    side_v_box = QVBoxLayout()
    side_v_box.addWidget(order_label)
    side_v_box.addWidget(items_box)
    side_v_box.addStretch()
    self.side_widget.setLayout(side_v_box)
    # Добавьте виджеты в главное окно и установите макет
    main_h_box = QHBoxLayout()
    main_h_box.addWidget(self.tab_bar, 1)
    main_h_box.addWidget(self.side_widget)
    self.setLayout(main_h_box)
# food_order.py
def pizzaTab(self):
    """Создаем вкладку пиццы. Позволяет пользователю выбрать
    тип пиццы и начинку с помощью радиокнопок."""
    # Настройте виджеты и макеты для отображения информации
    # пользователю о странице
    tab_pizza_label = QLabel("СОЗДАЙТЕ СВОЮ СОБСТВЕННУЮ ПИЦЦУ")
    tab_pizza_label.setObjectName("Header")
    description_box = QWidget()
    description_box.setObjectName("ImageBorder")
    pizza_image_path = "images/pizza.png"
    pizza_image = self.loadImage(pizza_image_path)
    pizza_desc = QLabel()
    pizza_desc.setObjectName("ImageInfo")
    pizza_desc.setText(
        """<p>Создаем для вас пиццу на заказ. Начните с
        вашего любимого коржа и добавьте любые начинки, а также
        идеальное количество сыра и соуса.</p>""")
    pizza_desc.setWordWrap(True)
    pizza_desc.setContentsMargins(10, 10, 10, 10)
    pizza_h_box = QHBoxLayout()
    pizza_h_box.addWidget(pizza_image)
    pizza_h_box.addWidget(pizza_desc, 1)
    description_box.setLayout(pizza_h_box)
    # Создайте групповой блок, который будет содержать варианты корочки
    crust_gbox = QGroupBox()
    crust_gbox.setTitle("ВЫБОР ВАШЕГО КОРЖА")
    # Групповое поле используется для группировки виджетов вместе,
    # в то время как группа кнопок используется для получения информации
    # о том, какая радиокнопка отмечена
    self.crust_group = QButtonGroup()
    gb_v_box = QVBoxLayout()
    crust_list = ["Ручной", "Плоский", "Фаршированный"]
    # Создайте радиокнопки для различных коржей и
    # добавляем в макет
    for cr in crust_list:
        crust_rb = QRadioButton(cr)
        gb_v_box.addWidget(crust_rb)
        self.crust_group.addButton(crust_rb)
    crust_gbox.setLayout(gb_v_box)

