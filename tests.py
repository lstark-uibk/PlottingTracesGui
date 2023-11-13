import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Button with Wrapped Text")

layout = QVBoxLayout()

button = QPushButton("")

# Create a QLabel to display the text with word wrapping
label = QLabel("This is a long text that should wrap to the next line if it's too long for the button's width.")
label.setWordWrap(True)  # Enable text wrapping

layout.addWidget(label)
layout.addWidget(button)

window.setLayout(layout)

window.setGeometry(100, 100, 400, 200)
window.show()

sys.exit(app.exec_())
