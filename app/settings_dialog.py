from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
)


class SettingsDialog(QDialog):
    def __init__(self, current_key: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("API Settings")
        self.setFixedWidth(600)
        self.setFixedHeight(160)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("YouTube Data API v3 Key:"))

        self._input = QLineEdit(current_key)
        self._input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self._input)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save = QPushButton("SAVE")
        save.clicked.connect(self.accept)
        cancel = QPushButton("CANCEL")
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(save)
        btn_row.addWidget(cancel)
        layout.addLayout(btn_row)

    @property
    def api_key(self) -> str:
        return self._input.text().strip()
