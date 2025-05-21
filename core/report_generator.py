from PySide6.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout
from PySide6.QtCore import Qt

class ReportDialog(QDialog):
    def __init__(self, flagged: dict[str, float], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Plagiarism Report")
        # Table with two columns: Document | Similarity
        table = QTableWidget(len(flagged), 2, self)
        table.setHorizontalHeaderLabels(["Document", "Similarity"])
        for row, (name, score) in enumerate(flagged.items()):
            item_name = QTableWidgetItem(name)
            item_score = QTableWidgetItem(f"{score:.1%}")
            # highlight very high matches
            if score > 0.9:
                item_score.setBackground(Qt.red)
                item_score.setForeground(Qt.white)
            table.setItem(row, 0, item_name)
            table.setItem(row, 1, item_score)
        layout = QVBoxLayout(self)
        layout.addWidget(table)
        self.resize(400, 200)
