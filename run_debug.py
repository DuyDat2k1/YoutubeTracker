import sys
import os
import traceback
from pathlib import Path

LOG_PATH = Path(__file__).parent / "debug.log"

def log(msg: str):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{msg}\n")

# Clear old log
if LOG_PATH.exists():
    LOG_PATH.unlink()

log("=== App starting ===")
log(f"Python: {sys.version}")
log(f"CWD: {os.getcwd()}")

try:
    log("Importing PySide6...")
    from PySide6.QtWidgets import QApplication
    log("PySide6 imported OK")
    
    from PySide6.QtCore import QTimer
    log("QtCore imported OK")
    
    from app.main_window import MainWindow
    log("MainWindow imported OK")
    
    app = QApplication(sys.argv or [""])
    app.setApplicationName("YouTube Competitor Tracker")
    log("QApplication created")
    
    window = MainWindow()
    log(f"MainWindow created, size: {window.size()}")
    
    window.show()
    log(f"Window shown, visible: {window.isVisible()}")
    
    window.raise_()
    window.activateWindow()
    log("Window raised and activated")
    
    def check_after_3s():
        log(f"After 3s - visible: {window.isVisible()}, active: {window.isActiveWindow()}")
    
    QTimer.singleShot(3000, check_after_3s)
    
    log("Entering event loop...")
    ret = app.exec()
    log(f"Event loop exited with code: {ret}")
    sys.exit(ret)
    
except Exception as e:
    log(f"ERROR: {e}")
    traceback.print_exc(file=open(LOG_PATH, "a"))
    sys.exit(1)
