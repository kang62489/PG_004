## Author: Kang
## Last Update: 2025-Jan-20
## Usage: A class for build a dialog for confimation

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout

class Confirm(QDialog):
    def __init__(self, title="Dialog", msg="Question"):
        super().__init__()
        self.setWindowTitle(title)
        
        self.message = QLabel(msg)
        
        self.buttons = QDialogButtonBox.Yes | QDialogButtonBox.No
        self.buttonBox = QDialogButtonBox(self.buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)