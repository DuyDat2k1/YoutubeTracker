import sys
from PySide6.QtWidgets import QApplication
from .main_window import MainWindow


STYLE = """
QMainWindow {
    background-color: #f0f2f5;
}

QWidget {
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 10pt;
    color: #1a1a2e;
}

QPushButton {
    background-color: #4361ee;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 11pt;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    min-height: 38px;
}

QPushButton:hover {
    background-color: #3a56d4;
}

QPushButton:pressed {
    background-color: #3046b5;
}

QPushButton:disabled {
    background-color: #cbd5e1;
    color: #94a3b8;
}

QLineEdit {
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 12px;
    background-color: white;
    selection-background-color: #4361ee;
    selection-color: white;
    font-size: 10pt;
    min-height: 20px;
}

QLineEdit:focus {
    border: 2px solid #4361ee;
    background-color: #f8faff;
}

QGroupBox {
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    margin-top: 16px;
    padding-top: 18px;
    font-weight: 700;
    color: #1a1a2e;
    background-color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 10px 0 10px;
    color: #1a1a2e;
    font-size: 11pt;
    font-weight: 700;
}

QTabWidget::pane {
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    background-color: #ffffff;
    top: -1px;
}

QTabBar::tab {
    background-color: #f1f5f9;
    color: #64748b;
    border: 1px solid #e2e8f0;
    border-bottom: none;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    padding: 10px 24px;
    margin-right: 6px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-size: 10pt;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #4361ee;
    border-bottom: 3px solid #4361ee;
}

QTabBar::tab:hover:!selected {
    background-color: #e2e8f0;
    color: #1a1a2e;
}

QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    gridline-color: #f1f5f9;
    selection-background-color: #4361ee;
    selection-color: white;
    alternate-background-color: #f8fafc;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #f1f5f9;
    white-space: normal;
    word-wrap: break-word;
}

QTableWidget::item:selected {
    background-color: #4361ee;
    color: white;
    border: none;
    outline: none;
}

QTableWidget::item:hover {
    background-color: transparent;
    border: none;
    outline: none;
}

QHeaderView::section {
    background-color: #1e293b;
    color: white;
    padding: 10px;
    border: none;
    font-weight: 700;
    font-size: 10pt;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QHeaderView::section:horizontal {
    border-right: 1px solid #334155;
    border-bottom: 2px solid #334155;
}

QProgressBar {
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    text-align: center;
    font-weight: 700;
    font-size: 9pt;
    background-color: #f1f5f9;
    color: #1a1a2e;
    min-height: 22px;
}

QProgressBar::chunk {
    background-color: #10b981;
    border-radius: 6px;
    margin: 2px;
}

QScrollBar:vertical {
    border: none;
    background-color: #f1f5f9;
    width: 14px;
    margin: 0px 0px 0px 0px;
}

QScrollBar::handle:vertical {
    background-color: #cbd5e1;
    border-radius: 7px;
    min-height: 40px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #94a3b8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
    height: 0px;
}

QToolTip {
    background-color: #1e293b;
    color: white;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 9pt;
    font-weight: 500;
}

QMessageBox {
    background-color: #ffffff;
}

QMessageBox QLabel {
    color: #1a1a2e;
    font-size: 10pt;
}

QDialog {
    background-color: #ffffff;
}
"""


def main():
    app = QApplication(sys.argv or [""])
    app.setApplicationName("YouTube Competitor Tracker")
    app.setQuitOnLastWindowClosed(True)
    app.setStyleSheet(STYLE)
    window = MainWindow()
    window.show()
    window.raise_()
    window.activateWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
