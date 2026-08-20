# YouTube Competitor Tracker

Ứng dụng desktop để theo dõi và phân tích kênh YouTube bằng YouTube Data API v3. Xây dựng với PySide6, SQLite và matplotlib.

## Tính năng

- Thêm danh sách URL kênh YouTube ở panel bên trái
- Click **ANALYZE** để lấy dữ liệu qua YouTube API
- Xem kết quả ở các tab: **Channels**, **3 Latest Videos**, **Subscriber Trend**
- **Import CSV** để thêm hàng loạt URL kênh
- **Export CSV** để xuất kết quả
- Tìm kiếm channel theo title (real-time)
- Lưu API key được mã hóa vào file config

## Yêu cầu

- Python 3.12+
- pip

## Cài đặt

```bash
cd YouTubeTracker
pip install -r requirements.txt
```

## Chạy trực tiếp (Khuyến nghị)

### Cách 1: Dùng file run.bat (Khuyến nghị)

Double-click file `run.bat` trong thư mục project. Terminal sẽ giữ mở để bạn đọc lỗi nếu có.

### Cách 2: Chạy bằng lệnh

```bash
cd YouTubeTracker
python -m app.main
```

## Chạy bằng Docker

### Yêu cầu

- Cài Docker Desktop: https://www.docker.com/products/docker-desktop/
- Trên Windows, cài X Server (VcXsrv hoặc X410) để hiển thị giao diện GUI

### Các bước

1. Mở VcXsrv với tùy chọn "Disable access control"
2. Mở PowerShell trong thư mục project:

```powershell
cd YouTubeTracker
docker compose up --build
```

## Cách sử dụng

1. Click **API SETTINGS** và nhập YouTube Data API v3 key
2. Thêm URL kênh YouTube ở panel bên trái, hoặc click **Import CSV**
3. Click **ANALYZE** để lấy dữ liệu
4. Xem kết quả ở các tab bên dưới

## Định dạng CSV

```csv
Channel,URL,Subscribers,Videos,Views,Published,LastChecked
Google for Developers,https://www.youtube.com/@GoogleDevelopers,2670000,6086,357253066,2007-08-23T00:00:00Z,2024-01-15T10:30:00+00:00
```

## Cấu trúc thư mục

```
YouTubeTracker/
├── app/
│   ├── __init__.py
│   ├── main.py              # Điểm vào ứng dụng
│   ├── main_window.py       # Giao diện chính
│   ├── models.py            # Data models
│   ├── database.py          # SQLite operations
│   ├── youtube_service.py   # YouTube API client
│   └── settings_dialog.py   # Dialog nhập API key
├── ui/
│   └── main_window.ui       # File Qt Designer
├── data/
│   ├── tracker.db           # SQLite database
│   └── config.ini           # API key đã mã hóa
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── run.bat                  # File chạy app (double-click)
└── .gitignore
```

## License

MIT
