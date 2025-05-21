import sys, threading, os, glob, datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QTreeWidget, QTreeWidgetItem,
    QMessageBox, QProgressDialog, QAbstractItemView
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
import datetime
from gui.compare_dialog import CompareDialog
from core.drive_watcher import watch_folder
from core.plagiarism_checker import PlagiarismChecker
from core.report_generator import ReportDialog
from core.embedder import get_embedding, similarity
import PyPDF2
# adjust to your actual watch folder
SUBMISSION_DIR = r"G:\My Drive\Assignments_test"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Assignment Manager")
        self.resize(600, 400)

        # Tree widget for file list with columns
        self.list_sub = QTreeWidget()
        self.list_sub.setHeaderLabels(["Name", "Size (KB)", "Modified"])
        self.list_sub.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_sub.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.list_sub.currentItemChanged.connect(
            lambda _, cur: self.btn_report.setEnabled(cur is not None)
        )
        self.list_sub.itemSelectionChanged.connect(self._update_compare_button)
        self.list_sub.setStyleSheet("""
QTreeWidget::item:selected {
    background: #0078d7;   /* Windows 10 blue */
    color: white;
}
""")

        # Icons (place suitable .png files in gui/icons/)
        self.icon_txt = QIcon(":/icons/txt.png")
        self.icon_pdf = QIcon(":/icons/pdf.png")

        self.btn_report = QPushButton("Generate Report")
        self.btn_report.setEnabled(False)
        self.btn_report.clicked.connect(self.on_report)

        self.btn_compare = QPushButton("Compare Files")
        self.btn_compare.setEnabled(False)
        self.btn_compare.clicked.connect(self.on_compare)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_report)
        btn_layout.addWidget(self.btn_compare)

        layout = QVBoxLayout()
        layout.addWidget(self.list_sub)
        layout.addLayout(btn_layout)
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

        # Load reference corpus
        refs = {
            os.path.basename(p): open(p, encoding="utf-8").read()
            for p in glob.glob("core/corpus/*.txt")
        }
        self.checker = PlagiarismChecker(refs, threshold=0.75)

        # Start folder watcher in background
        threading.Thread(target=watch_folder, args=(self.on_new_file,), daemon=True).start()

        # Populate existing files
        self.load_existing_files()

    def _update_compare_button(self):
        count = len(self.list_sub.selectedItems())
        self.btn_compare.setEnabled(count >= 2)

    def load_existing_files(self):
        if not os.path.isdir(SUBMISSION_DIR):
            return
        for fname in os.listdir(SUBMISSION_DIR):
            self.add_file_item(fname)

    def on_new_file(self, path):
        fname = os.path.basename(path)
        self.add_file_item(fname)

    def add_file_item(self, fname):
        full = os.path.join(SUBMISSION_DIR, fname)
        if not os.path.isfile(full):
            return
        stat = os.stat(full)
        size_kb = stat.st_size // 1024
        modified = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
        item = QTreeWidgetItem([fname, str(size_kb), modified])
        icon = self.icon_pdf if fname.lower().endswith(".pdf") else self.icon_txt
        item.setIcon(0, icon)
        # Make item selectable
        item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        # avoid duplicates
        for i in range(self.list_sub.topLevelItemCount()):
            if self.list_sub.topLevelItem(i).text(0) == fname:
                return
        self.list_sub.addTopLevelItem(item)

    def _extract_text(self, path: str, fname: str) -> str:
        if fname.lower().endswith(".pdf"):
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                return "".join(page.extract_text() or "" for page in reader.pages)
        else:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()

    def on_report(self):
        item = self.list_sub.currentItem()
        fname = item.text(0)
        path = os.path.join(SUBMISSION_DIR, fname)

        # extract text
        try:
            text = self._extract_text(path, fname)
        except Exception as e:
            QMessageBox.critical(self, "File Error", f"Could not read file:\n{e}")
            return

        # show progress
        dlg = QProgressDialog("Analyzing…", "Cancel", 0, 0, self)
        dlg.setWindowModality(Qt.WindowModal)
        dlg.show()
        QApplication.processEvents()

        # perform check
        flagged = self.checker.check(text)
        dlg.close()

        # display results
        if not flagged:
            QMessageBox.information(self, "Report", "✅ No similar documents found.")
        else:
            dlg = ReportDialog(flagged, self)
            dlg.exec()

    def on_compare(self):
        items = self.list_sub.selectedItems()
        names = [it.text(0) for it in items]
        texts = {}
        embs = {}
        for n in names:
            path = os.path.join(SUBMISSION_DIR, n)
            try:
                texts[n] = self._extract_text(path, n)
                embs[n] = get_embedding(texts[n])
            except Exception as e:
                QMessageBox.critical(self, "File Error", f"Could not read file {n}:\n{e}")
                return
        scores = {}
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                sc = similarity(embs[a], embs[b])
                scores[(a, b)] = sc
        dlg = CompareDialog(names, scores, self)
        dlg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
