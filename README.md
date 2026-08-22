# YouTube Competitor Tracker

Ứng dụng desktop để theo dõi và phân tích kênh YouTube bằng YouTube Data API v3. Xây dựng với PySide6, SQLite và matplotlib.

## Tính năng

- Thêm danh sách URL kênh YouTube ở panel bên trái
- Click **ANALYZE** để lấy dữ liệu qua YouTube API
- Xem kết quả ở các tab: **Channels**, **Latest Videos**, **Video Analytics**
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

## Chạy bằng Docker (khuyên dùng - chạy mọi hệ điều hành)

Cách này không cần cài Python, hiển thị app ngay trong trình duyệt và hoạt động giống nhau trên **Windows, macOS và Linux** — không cần chỉnh sửa gì sau khi clone.

### Yêu cầu

- Cài Docker Desktop: https://www.docker.com/products/docker-desktop/

### Các bước

```bash
cd YouTubeTracker
docker compose up -d --build
```

Sau đó mở trình duyệt và truy cập:

> **http://localhost:6080/**

Giao diện app sẽ tự kết nối và tự scale theo cửa sổ trình duyệt. Nhấn **F11** để full màn hình nếu muốn.

### Quản lý container

```bash
docker compose down      # Dừng app
docker compose restart   # Khởi động lại
docker logs youtubetracker-tracker-1   # Xem log
```

## Hướng dẫn sử dụng chi tiết

### 1. Cấu hình API key

- Click nút **API SETTINGS** ở góc trên
- Dán YouTube Data API v3 key của bạn (lấy tại https://console.cloud.google.com/)
- Key được mã hóa và lưu vào `data/config.ini`

### 2. Thêm kênh cần theo dõi

- Nhập URL kênh vào panel bên trái rồi nhấn nút **+**
- Hoặc click **Import CSV** để thêm hàng loạt (định dạng xem mục bên dưới)
- Danh sách URL được lưu tự động — lần mở app sau vẫn còn

### 3. Phân tích dữ liệu

- Click **ANALYZE** để lấy dữ liệu mới nhất qua YouTube API
- Trong lúc phân tích: bảng kênh hiện spinner xanh "Đang tải kênh..."
- Sau khi xong, danh sách kênh tự động cập nhật

### 4. Xem dữ liệu

- Tab **Channels**: tổng quan kênh (sub, video, view...)
- Click một dòng kênh → tab **Latest Videos** tải 10 video mới nhất (spinner cam "Đang tải dữ liệu...")
- Click một video → tab **Video Analytics** vẽ biểu đồ Views/Likes/Comments 7 ngày (spinner cam "Đang tải thống kê video...")
- Trục X của biểu đồ luôn hiển thị theo ngày (dd/mm/yyyy)

### 5. Tự động làm mới khi khởi động

Khi bật app, chương trình tự động chạy nền làm mới dữ liệu của tất cả kênh trong danh sách — bạn thấy ngay dữ liệu cũ từ DB trong lúc chờ dữ liệu mới.

### 6. Dữ liệu lưu ở đâu?

Tất cả dữ liệu (kênh, video, lịch sử sub/view/like) lưu trong SQLite tại:

```
data/tracker.db
```

Thư mục `data/` được mount ra ngoài container nên **dữ liệu không mất** khi tắt/xóa container hay build lại image.

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
├── start-vnc.sh               # Script khởi động VNC + app trong container
├── docker/
│   └── novnc-index.html       # Trang web noVNC tùy chỉnh
├── run.bat                    # File chạy app (double-click)
└── .gitignore
```

## License

MIT
