import sys
from PyQt5.QtWidgets import QApplication, QListWidget, QListWidgetItem, QMainWindow

def handle_double_click(item):
    print(f"Double-clicked: {item.text()}")

app = QApplication(sys.argv)

window = QMainWindow()
window.setWindowTitle("Double-Click Example")

list_widget = QListWidget(window)

# Add items to the QListWidget
item1 = QListWidgetItem("Item 1")
item2 = QListWidgetItem("Item 2")
item3 = QListWidgetItem("Item 3")

list_widget.addItem(item1)
list_widget.addItem(item2)
list_widget.addItem(item3)

# Connect the double-click event to the handle_double_click function
list_widget.itemDoubleClicked.connect(handle_double_click)

window.setCentralWidget(list_widget)
window.show()

sys.exit(app.exec_())