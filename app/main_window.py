from __future__ import annotations

import base64
import csv
from datetime import datetime, timezone
from pathlib import Path

from PySide6.QtCore import QThread, Qt, Signal, Slot, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFileDialog, QGroupBox, QHeaderView, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMessageBox, QProgressBar, QPushButton, QScrollArea,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from .database import Database
from .models import ChannelModel
from .settings_dialog import SettingsDialog
from .youtube_service import YouTubeService

try:
    import matplotlib
    matplotlib.use("QtAgg")
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
    from matplotlib.figure import Figure
    HAS_MATPLOTLIB = True
except Exception:
    HAS_MATPLOTLIB = False

CONFIG_DIR = Path(__file__).resolve().parent.parent / "data"
CONFIG_PATH = CONFIG_DIR / "config.ini"


class ProgressWidget(QWidget):
    """Progress bar hiển thị tiến trình phân tích trong tab Channels."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        self.iconLabel = QLabel("⟳")
        self.iconLabel.setStyleSheet("font-size: 16pt; font-weight: bold; color: #2980b9;")
        layout.addWidget(self.iconLabel)

        self.textLabel = QLabel("Ready.")
        self.textLabel.setStyleSheet("font-size: 10pt; color: #2c3e50;")
        layout.addWidget(self.textLabel, 1)

        self.progressBar = QProgressBar()
        self.progressBar.setFixedWidth(120)
        self.progressBar.setFixedHeight(20)
        self.progressBar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                text-align: center;
                font-size: 9pt;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
            }
        """)
        layout.addWidget(self.progressBar)

        self.setVisible(False)

    def start(self, total: int) -> None:
        self.progressBar.setMaximum(total)
        self.progressBar.setValue(0)
        self.textLabel.setText("Analyzing...")
        self.setVisible(True)

    def update(self, current: int, url: str) -> None:
        self.progressBar.setValue(current)
        display_url = url if len(url) <= 50 else url[:47] + "..."
        self.textLabel.setText(f"Analyzing: {display_url}")

    def finish(self) -> None:
        self.progressBar.setValue(self.progressBar.maximum())
        self.textLabel.setText("Completed!")
        self.setVisible(False)


class UrlRow(QWidget):
    """Một dòng link: [X] [ô nhập link YouTube]."""
    removed = Signal(QWidget)

    def __init__(self, url_text: str = "", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        self.urlEdit = QLineEdit(url_text)
        self.urlEdit.setPlaceholderText("Enter YouTube channel URL...")
        self.urlEdit.setMinimumHeight(32)
        layout.addWidget(self.urlEdit, 1)

        self.removeBtn = QPushButton("✕")
        self.removeBtn.setFixedWidth(36)
        self.removeBtn.setFixedHeight(32)
        self.removeBtn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #c0392b; }
            QPushButton:pressed { background-color: #a93226; }
        """)
        layout.addWidget(self.removeBtn)

        self.removeBtn.clicked.connect(lambda: self.removed.emit(self))


class UrlListWidget(QGroupBox):
    """Group chứa danh sách link, có scroll khi nhiều."""
    imported = Signal()

    def __init__(self, parent=None):
        super().__init__("YouTube Channel List", parent)
        self.setStyleSheet("""
            QGroupBox {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 12px;
                font-weight: bold;
                color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px 0 6px;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 14, 8, 8)
        main_layout.setSpacing(6)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setMinimumHeight(280)
        self._scroll.setMaximumHeight(380)

        self._rows_container = QWidget()
        self._rows_container.setObjectName("rowsContainer")
        self._rows_layout = QVBoxLayout(self._rows_container)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(4)
        self._rows_layout.addStretch()

        self._scroll.setWidget(self._rows_container)
        main_layout.addWidget(self._scroll)

        btn_row = QHBoxLayout()
        self._add_btn = QPushButton("+ Add Link")
        self._import_btn = QPushButton("Import CSV")
        self._remove_all_btn = QPushButton("Clear All")
        btn_row.addWidget(self._add_btn)
        btn_row.addWidget(self._import_btn)
        btn_row.addWidget(self._remove_all_btn)
        btn_row.addStretch()
        main_layout.addLayout(btn_row)

        self._add_btn.clicked.connect(self._on_add)
        self._remove_all_btn.clicked.connect(self._on_remove_all)
        self._import_btn.clicked.connect(self._on_import_csv)

    def get_urls(self) -> list[str]:
        urls = []
        for i in range(self._rows_layout.count()):
            item = self._rows_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, UrlRow):
                text = widget.urlEdit.text().strip()
                if text:
                    urls.append(text)
        return urls

    def _on_add(self) -> None:
        row = UrlRow()
        row.removed.connect(self._on_row_removed)
        self._rows_layout.insertWidget(self._rows_layout.count() - 1, row)
        row.urlEdit.setFocus()
        self._scroll_to_bottom()
        main_window = self._get_main_window()
        if main_window and hasattr(main_window, "_save_urls"):
            main_window._save_urls()

    def _on_remove_all(self) -> None:
        while self._rows_layout.count() > 1:
            item = self._rows_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        main_window = self._get_main_window()
        if main_window and hasattr(main_window, "_save_urls"):
            main_window._save_urls()

    def _on_row_removed(self, row: QWidget) -> None:
        url = row.urlEdit.text().strip()
        main_window = self._get_main_window()
        if main_window and hasattr(main_window, "_delete_channel_by_url"):
            main_window._delete_channel_by_url(url)
        self._rows_layout.removeWidget(row)
        row.deleteLater()
        if main_window and hasattr(main_window, "_save_urls"):
            main_window._save_urls()

    def _get_main_window(self):
        widget = self
        while widget:
            if isinstance(widget, MainWindow):
                return widget
            widget = widget.parent()
        return None

    def _on_import_csv(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Import CSV", "", "CSV (*.csv);;All (*)"
        )
        if not path:
            return
        count = 0
        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                for idx, row in enumerate(reader):
                    if not row:
                        continue
                    if idx == 0 and self._is_header_row(row):
                        continue
                    url = self._extract_url(row)
                    if url and self._is_youtube_url(url):
                        url_row = UrlRow(url)
                        url_row.removed.connect(self._on_row_removed)
                        self._rows_layout.insertWidget(self._rows_layout.count() - 1, url_row)
                        count += 1
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        QMessageBox.information(self, "Import", f"Imported {count} links.")
        self._scroll_to_bottom()
        self.imported.emit()
        if hasattr(self.parent(), "_save_urls"):
            self.parent()._save_urls()

    @staticmethod
    def _is_header_row(row: list[str]) -> bool:
        if not row:
            return False
        first = row[0].strip().lower()
        return first in {"url", "channel", "link", "urls", "channels"}

    @staticmethod
    def _extract_url(row: list[str]) -> str:
        if len(row) >= 2:
            return row[1].strip()
        return row[0].strip() if row else ""

    @staticmethod
    def _is_youtube_url(text: str) -> bool:
        t = text.lower()
        return any(k in t for k in ["youtube.com", "youtu.be", "@"])

    def _scroll_to_bottom(self) -> None:
        self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        )

    def highlight_url(self, url: str) -> None:
        for i in range(self._rows_layout.count()):
            item = self._rows_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, UrlRow):
                row_url = widget.urlEdit.text().strip()
                if row_url == url:
                    widget.urlEdit.setStyleSheet("""
                        QLineEdit {
                            background-color: #d4edda;
                            border: 2px solid #28a745;
                        }
                    """)
                    self._scroll.ensureWidgetVisible(widget)
                    QTimer.singleShot(2000, lambda w=widget: self._clear_highlight(w))
                    break

    def _clear_highlight(self, widget: QWidget) -> None:
        widget.urlEdit.setStyleSheet("")


class AnalyzeWorker(QThread):
    progress = Signal(str)
    finished = Signal(int, int)
    error = Signal(str)

    def __init__(self, yt: YouTubeService, db: Database, urls: list[str]):
        super().__init__()
        self._yt = yt
        self._db = db
        self._urls = urls

    def run(self) -> None:
        ok = 0
        total = len(self._urls)
        try:
            for idx, url in enumerate(self._urls, start=1):
                self.progress.emit(f"done|{url}|{idx}")
                ch = self._yt.get_channel(url)
                if ch is None:
                    continue
                db_id = self._db.upsert_channel(ch)
                self._db.add_snapshot(db_id, ch.subscribers)
                latest = self._yt.get_latest_videos(ch.channel_id, db_id)
                self._db.upsert_videos(latest)
                ok += 1
            self.finished.emit(ok, total)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._db = Database()
        self._api_key = ""
        self._yt = YouTubeService("")
        self._worker: AnalyzeWorker | None = None

        self._build_ui()
        self._connect_signals()
        self._load_api_key()
        self._load_saved_urls()
        self._load_channels()

    @staticmethod
    def _encrypt_key(key: str) -> str:
        return base64.b64encode(key.encode("utf-8")).decode("utf-8")

    @staticmethod
    def _decrypt_key(encoded: str) -> str:
        try:
            return base64.b64decode(encoded.encode("utf-8")).decode("utf-8")
        except Exception:
            return ""

    def _load_api_key(self) -> None:
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("api_key="):
                            encoded = line.split("=", 1)[1].strip()
                            self._api_key = self._decrypt_key(encoded)
                            break
            except Exception:
                pass
        self._yt = YouTubeService(self._api_key)

    def _save_api_key(self, key: str) -> None:
        if not key:
            return
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        encoded = self._encrypt_key(key)
        lines = []
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.startswith("api_key="):
                        lines.append(line.rstrip("\n"))
        lines.append(f"api_key={encoded}")
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    def _save_urls(self) -> None:
        self._db.clear_saved_urls()
        for url in self.urlList.get_urls():
            if url:
                self._db.add_saved_url(url)

    def _load_saved_urls(self) -> None:
        urls = self._db.get_saved_urls()
        for url in urls:
            row = UrlRow(url)
            row.removed.connect(self.urlList._on_row_removed)
            self.urlList._rows_layout.insertWidget(self.urlList._rows_layout.count() - 1, row)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        self.setWindowTitle("YouTube Competitor Tracker")
        self.resize(1250, 800)

        top_layout = QHBoxLayout()

        self.urlList = UrlListWidget()
        self.urlList.setMaximumWidth(675)
        top_layout.addWidget(self.urlList)

        right_layout = QVBoxLayout()

        self.analyzeBtn = QPushButton("ANALYZE")
        self.analyzeBtn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                font-size: 12pt;
                padding: 10px;
            }
            QPushButton:hover { background-color: #229954; }
            QPushButton:pressed { background-color: #1e8449; }
        """)
        self.settingsBtn = QPushButton("API SETTINGS")
        self.exportBtn = QPushButton("EXPORT CSV")
        right_layout.addWidget(self.analyzeBtn)
        right_layout.addWidget(self.settingsBtn)
        right_layout.addWidget(self.exportBtn)

        right_layout.addStretch()

        top_layout.addLayout(right_layout)
        main_layout.addLayout(top_layout)

        self.tabWidget = QTabWidget()
        self.channelsTable = QTableWidget()
        self.channelsTable.setSelectionBehavior(QTableWidget.SelectRows)
        self.channelsTable.setSelectionMode(QTableWidget.SingleSelection)
        self.channelsTable.setAlternatingRowColors(True)
        self.channelsTable.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)

        channels_container = QWidget()
        channels_layout = QVBoxLayout(channels_container)
        channels_layout.setContentsMargins(0, 0, 0, 0)
        channels_layout.setSpacing(0)
        self._progress_widget = ProgressWidget()
        channels_layout.addWidget(self._progress_widget)
        channels_layout.addWidget(self.channelsTable)
        self.tabWidget.addTab(channels_container, "Channels")

        self.videosTable = QTableWidget()
        self.videosTable.setSelectionBehavior(QTableWidget.SelectRows)
        self.videosTable.setAlternatingRowColors(True)
        self.videosTable.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.tabWidget.addTab(self.videosTable, "3 Latest Videos")

        chart_tab = QWidget()
        self.tabWidget.addTab(chart_tab, "Subscriber Trend")

        main_layout.addWidget(self.tabWidget)

        if HAS_MATPLOTLIB:
            self._chart_fig = Figure(figsize=(8, 4), dpi=100)
            self._chart_canvas = FigureCanvasQTAgg(self._chart_fig)
            layout = QVBoxLayout(chart_tab)
            layout.addWidget(self._chart_canvas)
        else:
            self._chart_fig = None
            self._chart_canvas = None

    def _connect_signals(self) -> None:
        self.analyzeBtn.clicked.connect(self._on_analyze)
        self.settingsBtn.clicked.connect(self._on_settings)
        self.exportBtn.clicked.connect(self._on_export)
        self.channelsTable.currentCellChanged.connect(self._on_channel_selected)
        self.urlList.imported.connect(self._on_analyze)

    def _load_channels(self) -> None:
        channels = self._db.get_channels()
        self.channelsTable.setRowCount(len(channels))
        self.channelsTable.setColumnCount(7)
        headers = ["TITLE", "CHANNEL ID", "SUBSCRIBERS", "VIDEOS", "VIEWS", "PUBLISHED", "LAST CHECKED"]
        self.channelsTable.setHorizontalHeaderLabels(headers)
        self.channelsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        col_widths = [305, 185, 145, 105, 145, 125, 135]
        for col, width in enumerate(col_widths):
            self.channelsTable.setColumnWidth(col, width)

        font = self.channelsTable.horizontalHeader().font()
        font.setPointSize(11)
        font.setFamily("Times New Roman")
        font.setBold(True)
        self.channelsTable.horizontalHeader().setFont(font)

        for row, ch in enumerate(channels):
            self._set_cell(row, 0, ch.title)
            self._set_cell(row, 1, ch.channel_id)
            self._set_cell(row, 2, f"{ch.subscribers:,}")
            self._set_cell(row, 3, f"{ch.video_count:,}")
            self._set_cell(row, 4, f"{ch.view_count:,}")
            self._set_cell(row, 5, ch.published_at.strftime("%Y-%m-%d") if ch.published_at else "")
            self._set_cell(row, 6, ch.last_checked.strftime("%Y-%m-%d %H:%M") if ch.last_checked else "")

    def _set_cell(self, row: int, col: int, text: str) -> None:
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.channelsTable.setItem(row, col, item)

    def _delete_channel_by_url(self, url: str) -> None:
        channels = self._db.get_channels()
        ch = next((c for c in channels if c.url == url), None)
        if ch:
            self._db.delete_channel(ch.id)
            self._load_channels()
            self.videosTable.setRowCount(0)
            if HAS_MATPLOTLIB and self._chart_fig is not None:
                self._chart_fig.clear()
                self._chart_canvas.draw()

    @Slot(int, int, int, int)
    def _on_channel_selected(self, row: int, _col: int, _prev_row: int, _prev_col: int) -> None:
        if row < 0:
            return
        channels = self._db.get_channels()
        if row >= len(channels):
            return
        ch = channels[row]
        self.urlList.highlight_url(ch.url)
        self._load_videos(ch.id)
        self._load_chart(ch.id)

    def _load_videos(self, channel_db_id: int) -> None:
        videos = self._db.get_latest_videos(channel_db_id)
        self.videosTable.setRowCount(len(videos))
        self.videosTable.setColumnCount(5)
        self.videosTable.setHorizontalHeaderLabels(["TITLE", "PUBLISHED", "VIEWS", "LIKES", "COMMENTS"])
        self.videosTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        vcol_widths = [345, 125, 125, 125, 125]
        for col, width in enumerate(vcol_widths):
            self.videosTable.setColumnWidth(col, width)

        vfont = self.videosTable.horizontalHeader().font()
        vfont.setPointSize(11)
        vfont.setFamily("Times New Roman")
        vfont.setBold(True)
        self.videosTable.horizontalHeader().setFont(vfont)

        for row, v in enumerate(videos):
            self._set_cell(row, 0, v.title)
            self._set_cell(row, 1, v.published_at.strftime("%Y-%m-%d") if v.published_at else "")
            self._set_cell(row, 2, f"{v.views:,}")
            self._set_cell(row, 3, f"{v.likes:,}")
            self._set_cell(row, 4, f"{v.comments:,}")

    def _load_chart(self, channel_db_id: int) -> None:
        if not HAS_MATPLOTLIB or self._chart_fig is None:
            return
        self._chart_fig.clear()
        ax = self._chart_fig.add_subplot(111)
        snapshots = self._db.get_snapshots(channel_db_id)

        if snapshots:
            dates = [s.captured_at for s in snapshots if s.captured_at]
            subs = [s.subscribers for s in snapshots if s.captured_at]
            if dates:
                ax.plot(dates, subs, marker="o", linewidth=2)
                ax.set_title("Subscriber Trend")
                ax.set_ylabel("Subscribers")
                self._chart_fig.autofmt_xdate()
        else:
            ax.text(0.5, 0.5, "No data available", ha="center", va="center", transform=ax.transAxes)

        self._chart_canvas.draw()

    @Slot()
    def _on_analyze(self) -> None:
        if not self._yt.is_configured:
            QMessageBox.warning(self, "Notice", "Please go to API SETTINGS and enter your YouTube Data API v3 key.")
            return

        urls = self.urlList.get_urls()
        if not urls:
            QMessageBox.warning(self, "Notice", "Please enter a YouTube URL.")
            return

        self._start_analysis(urls)

    def _start_analysis(self, urls: list[str]) -> None:
        self.analyzeBtn.setEnabled(False)
        self._progress_widget.start(len(urls))

        self._worker = AnalyzeWorker(self._yt, self._db, urls)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_analyze_done)
        self._worker.error.connect(self._on_analyze_error)
        self._worker.start()

    @Slot(str)
    def _on_progress(self, msg: str) -> None:
        if msg.startswith("done|"):
            parts = msg.split("|")
            url = parts[1]
            current = int(parts[2])
            self._progress_widget.update(current, url)
        else:
            self._progress_widget.update(0, msg)

    @Slot(int, int)
    def _on_analyze_done(self, ok: int, total: int) -> None:
        self.analyzeBtn.setEnabled(True)
        self._progress_widget.finish()
        self._load_channels()

    @Slot(str)
    def _on_analyze_error(self, msg: str) -> None:
        self.analyzeBtn.setEnabled(True)
        self._progress_widget.finish()
        QMessageBox.critical(self, "API Error", msg)

    @Slot()
    def _on_settings(self) -> None:
        dlg = SettingsDialog(self._api_key, self)
        if dlg.exec() == SettingsDialog.Accepted:
            self._api_key = dlg.api_key
            self._yt = YouTubeService(self._api_key)
            self._save_api_key(self._api_key)

    @Slot()
    def _on_export(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", "youtube_channels.csv", "CSV (*.csv)"
        )
        if not path:
            return

        channels = self._db.get_channels()
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Channel", "URL", "Subscribers", "Videos", "Views", "LastChecked"])
            for c in channels:
                writer.writerow([
                    c.title, c.url, c.subscribers, c.video_count, c.view_count,
                    c.last_checked.strftime("%Y-%m-%d %H:%M") if c.last_checked else "",
                ])
        QMessageBox.information(self, "Export", f"Exported {len(channels)} channels.")
