# app.py - PyQt5 desktop version
import sys, os, json
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox, QInputDialog
from models import load_menu, save_menu
from billing import compute_bill, generate_bill_number, build_receipt_text, format_currency

BILLS_DIR = "bills"
os.makedirs(BILLS_DIR, exist_ok=True)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Restaurant Billing - PyQt")
        self.resize(800, 600)
        self.menu = load_menu() or {}
        self.item_widgets = {}
        self._init_ui()

    def _init_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QHBoxLayout(central)

        # Left: menu list
        left = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left)
        self.menu_list = QtWidgets.QScrollArea()
        self.menu_list.setWidgetResizable(True)
        self.menu_container = QtWidgets.QWidget()
        self.menu_layout = QtWidgets.QVBoxLayout(self.menu_container)
        self.menu_list.setWidget(self.menu_container)
        left_layout.addWidget(self.menu_list)

        btn_add = QtWidgets.QPushButton("Add Item")
        btn_add.clicked.connect(self.add_item)
        btn_update = QtWidgets.QPushButton("Update Item")
        btn_update.clicked.connect(self.update_item)
        btn_remove = QtWidgets.QPushButton("Remove Item")
        btn_remove.clicked.connect(self.remove_item)

        left_layout.addWidget(btn_add)
        left_layout.addWidget(btn_update)
        left_layout.addWidget(btn_remove)

        # Right: actions & receipt
        right = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right)
        btn_calc = QtWidgets.QPushButton("Calculate Bill")
        btn_calc.clicked.connect(self.calculate_bill)
        btn_save = QtWidgets.QPushButton("Save Receipt")
        btn_save.clicked.connect(self.save_receipt)
        self.receipt = QtWidgets.QTextEdit()

        right_layout.addWidget(btn_calc)
        right_layout.addWidget(btn_save)
        right_layout.addWidget(self.receipt)

        layout.addWidget(left, 1)
        layout.addWidget(right, 1)
        self._populate_menu()

    def _populate_menu(self):
        # clear
        for i in reversed(range(self.menu_layout.count())):
            w = self.menu_layout.itemAt(i).widget()
            if w: w.setParent(None)
        self.item_widgets.clear()
        for name, price in self.menu.items():
            row = QtWidgets.QWidget()
            row_layout = QtWidgets.QHBoxLayout(row)
            lbl = QtWidgets.QLabel(f"{name} - ₹{price:.2f}")
            spin = QtWidgets.QSpinBox()
            spin.setRange(0, 100)
            row_layout.addWidget(lbl)
            row_layout.addWidget(spin)
            self.menu_layout.addWidget(row)
            self.item_widgets[name] = spin

    def add_item(self):
        name, ok = QInputDialog.getText(self, "Add Item", "Item name:")
        if not ok or not name: return
        price, ok = QInputDialog.getDouble(self, "Add Item", "Price:", decimals=2)
        if not ok: return
        if name in self.menu:
            QMessageBox.warning(self, "Exists", "Item already exists")
            return
        self.menu[name] = price
        save_menu(self.menu)
        self._populate_menu()

    def update_item(self):
        name, ok = QInputDialog.getText(self, "Update Item", "Existing item name:")
        if not ok or not name: return
        if name not in self.menu:
            QMessageBox.warning(self, "Not found", "Item not found")
            return
        price, ok = QInputDialog.getDouble(self, "Update Item", f"New price for {name}:", decimals=2)
        if not ok: return
        self.menu[name] = price
        save_menu(self.menu)
        self._populate_menu()

    def remove_item(self):
        name, ok = QInputDialog.getText(self, "Remove Item", "Item name to remove:")
        if not ok or not name: return
        if name not in self.menu:
            QMessageBox.warning(self, "Not found", "Item not found")
            return
        del self.menu[name]
        save_menu(self.menu)
        self._populate_menu()

    def calculate_bill(self):
        ordered = {}
        for name, spin in self.item_widgets.items():
            qty = spin.value()
            if qty > 0:
                ordered[name] = qty
        bill = compute_bill(ordered, self.menu)
        bill_no = generate_bill_number()
        ts = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        text = build_receipt_text(bill_no, ts, bill)
        self.current_receipt = {'text': text, 'bill_no': bill_no}
        self.receipt.setPlainText(text)

    def save_receipt(self):
        if not hasattr(self, 'current_receipt'):
            QMessageBox.warning(self, "No receipt", "Please calculate the bill first.")
            return
        filename = os.path.join(BILLS_DIR, f"bill_{self.current_receipt['bill_no']}.txt")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.current_receipt['text'])
        QMessageBox.information(self, "Saved", f"Saved to {filename}")

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
