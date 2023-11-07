from PyQt5.QtWidgets import QApplication, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt

app = QApplication([])

list_widget = QListWidget()

item1 = QListWidgetItem("Item 1")
item2 = QListWidgetItem("Item 2")
item3 = QListWidgetItem("Item 3")

list_widget.addItem(item1)

# Get all items in the QListWidget
all_items = list_widget.findItems("", Qt.MatchContains)

# Print the text of each item
for item in all_items:
    print(item.text())

list_widget.show()

app.exec_()