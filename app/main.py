import sys
import traceback
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from PySide6.QtWidgets import QApplication
    from app.main_window import MainWindow

    app = QApplication(sys.argv or [""])
    app.setApplicationName("YouTube Competitor Tracker")
    app.setQuitOnLastWindowClosed(True)

    window = MainWindow()
    window.show()
    window.raise_()
    window.activateWindow()

    app.installEventFilter(window)

    sys.exit(app.exec())

except Exception as e:
    print(f"\n{'='*60}")
    print(f"ERROR: {e}")
    print(f"{'='*60}")
    traceback.print_exc()
    print(f"\n{'='*60}")
    input("Press Enter to exit...")
    sys.exit(1)
