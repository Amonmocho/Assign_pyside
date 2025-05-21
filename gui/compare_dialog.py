from PySide6.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout 
from PySide6.QtCore import Qt 
class CompareDialog(QDialog):
    def __init__(self, names: list[str], scores: dict[tuple[str, str], float], parent=None):
        """
        :param names: list of filenames selected
        :param scores: dict mapping (name1,name2) → similarity score (0–1)
        """
        super().__init__(parent)
        self.setWindowTitle("File Comparison")
        n = len(names)
        table = QTableWidget(n, n, self)
        table.setHorizontalHeaderLabels(names)
        table.setVerticalHeaderLabels(names)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        for i, ni in enumerate(names):
            for j, nj in enumerate(names):
                if i == j:
                    item = QTableWidgetItem("—")
                else:  # ensure (min,max) ordering
                    key = (ni, nj) if (ni, nj) in scores else (nj, ni)
                    sc = scores.get(key, 0.0)
                    item = QTableWidgetItem(f"{sc:.1%}")  # highlight >90%
                    if sc > 0.9:
                        item.setBackground(Qt.red)
                        item.setForeground(Qt.white)
                table.setItem(i, j, item)
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        table.setAlternatingRowColors(True)
        layout = QVBoxLayout(self)
        layout.addWidget(table)
        self.resize(500, 400)
