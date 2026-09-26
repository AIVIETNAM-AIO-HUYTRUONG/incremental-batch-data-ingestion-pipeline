# YouTube Video, Audio & Subtitle Crawler

Crawler thu thập video, audio, phụ đề và metadata từ YouTube.

Crawler sử dụng hai lớp chính:

1. **YouTube Data API v3** thông qua `googleapiclient`

   - Tìm kiếm video theo keyword.
   - Giới hạn theo thời gian đăng.
   - Lấy metadata của video.
   - Lọc theo ngôn ngữ.
   - Lọc theo thời lượng.
   - Loại bỏ những video đã được crawl trước đó.

2. **yt-dlp**

   - Tải video.
   - Tải audio.
   - Tải subtitle.
   - Lưu `info.json`.
   - Sử dụng `ffmpeg` để merge video + audio thành MP4.

---

## 1. Architecture

```text
crawl_yt_video_audio/
│
├── __init__.py
├── __main__.py
├── main.py
│
├── cli.py
├── config.py
├── filters.py
├── youtube_api.py
├── downloader.py
├── crawler.py
│
├── config.yaml
├── .env
├── .env.example
└── README.md
```

### Responsibility

```text
main.py
    Entry point
       │
       ▼
cli.py
    Parse CLI arguments
       │
       ▼
crawler.py
    Application workflow
       │
       ├───────────────┐
       ▼               ▼
youtube_api.py     downloader.py
       │               │
       ▼               ▼
YouTube API        yt-dlp
       │               │
       └───────┬───────┘
               ▼
          Data Lake
```

---

## 2. Search and filtering flow

Crawler không tải ngay toàn bộ video tìm được.

Thay vào đó, pipeline thực hiện:

```text
YouTube Search API
       │
       ▼
Candidate videos
       │
       ▼
Video details API
       │
       ├── Already downloaded?
       │       └── Skip
       │
       ├── English?
       │       └── Reject
       │
       ├── Duration valid?
       │       └── Reject
       │
       ▼
Qualified videos
       │
       ▼
yt-dlp
```

Cách này giúp tránh tải những video không phù hợp và giảm chi phí bandwidth cũng như thời gian xử lý.

---

## 3. Requirements

Python packages:

```text
google-api-python-client
yt-dlp
PyYAML
python-dotenv
```

Project cũng sử dụng các utility dùng chung trong thư mục:

```text
common/
```

bao gồm:

```text
config_utils
logging_utils
retry_utils
state_store
```

Ngoài Python packages, máy cần cài:

```text
ffmpeg
```

`ffmpeg` được `yt-dlp` sử dụng để merge video stream và audio stream thành file MP4.

---

## 4. Environment variables

Tạo file:

```text
.env
```

dựa trên:

```text
.env.example
```

Ví dụ:

```dotenv
YOUTUBE_API_KEY=your_youtube_api_key_here
```

Không commit `.env` lên Git.

Nên thêm:

```text
.env
```

vào `.gitignore`.

---

## 5. Configuration

File:

```text
config.yaml
```

Ví dụ:

```yaml
query: "AI Research Papers"

days_back: 1

min_duration_seconds: 120
max_duration_seconds: 720

require_english: true
exclude_shorts: true

max_results: 10

relevance_language: "en"

search_timeout_seconds: 60

download:
  video_format: "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best"
  audio_format: "bestaudio[ext=m4a]/bestaudio"

  subtitle_langs:
    - "en"
```

### Configuration fields

| Field                    | Ý nghĩa                                      |
| ------------------------ | -------------------------------------------- |
| `query`                  | Keyword tìm kiếm                             |
| `days_back`              | Chỉ lấy video trong N ngày gần nhất          |
| `min_duration_seconds`   | Thời lượng tối thiểu                         |
| `max_duration_seconds`   | Thời lượng tối đa                            |
| `require_english`        | Có yêu cầu video tiếng Anh hay không         |
| `exclude_shorts`         | Có loại YouTube Shorts hay không             |
| `max_results`            | Số video tối đa cần lấy                      |
| `relevance_language`     | Ngôn ngữ dùng cho ranking của YouTube Search |
| `search_timeout_seconds` | Timeout của quá trình tìm kiếm               |
| `video_format`           | Format video của yt-dlp                      |
| `audio_format`           | Format audio của yt-dlp                      |
| `subtitle_langs`         | Danh sách ngôn ngữ subtitle                  |

Lưu ý: `relevance_language` chỉ ảnh hưởng đến thứ hạng kết quả tìm kiếm. Nó không đảm bảo rằng tất cả kết quả đều là video tiếng Anh. Vì vậy crawler vẫn thực hiện bước language filtering sau khi lấy metadata.

---

## 6. Running independently

Từ project root:

```powershell
python -m crawl_yt_video_audio
```

Hoặc chỉ định configuration:

```powershell
python -m crawl_yt_video_audio --config crawl_yt_video_audio/config.yaml
```

Cũng có thể chạy trực tiếp:

```powershell
python crawl_yt_video_audio/main.py
```

---

## 7. Running through Orchestrator

Crawler được thiết kế để có thể chạy độc lập hoặc được điều phối bởi Data Pipeline Orchestrator.

Chạy YouTube job:

```powershell
python -m orchestrator --job yt
```

Chạy nhiều jobs:

```powershell
python -m orchestrator --job arxiv yt
```

Chạy toàn bộ pipeline:

```powershell
python -m orchestrator --job all
```

Flow:

```text
Orchestrator
      │
      ▼
YouTube Job
      │
      ▼
crawler.run()
      │
      ├── YouTube Data API
      │
      ├── Filtering
      │
      └── yt-dlp
```

---

## 8. Data Lake structure

Output được lưu tại:

```text
data_lake_local/youtube/
```

Ví dụ:

```text
data_lake_local/
└── youtube/
    │
    ├── state/
    │   ├── downloaded_ids.json
    │   └── crawl_2026-09-26.log
    │
    └── 2026-09-26/
        │
        ├── video/
        │   └── <video_id>.mp4
        │
        ├── audio/
        │   └── <video_id>.m4a
        │
        ├── info/
        │   └── <video_id>.info.json
        │
        └── subs/
            └── <video_id>.en.vtt
```

### `video/`

Lưu video MP4.

### `audio/`

Lưu audio M4A.

### `info/`

Lưu metadata của video dưới dạng JSON.

### `subs/`

Lưu subtitle dạng VTT.

### `state/`

Lưu trạng thái crawler để tránh tải lại những video đã xử lý.

---

## 9. State management

Crawler sử dụng:

```text
state/downloaded_ids.json
```

để lưu các video đã download.

Ví dụ:

```json
{
  "abc123": {
    "url": "https://www.youtube.com/watch?v=abc123",
    "downloaded_at": "2026-09-26T05:00:00Z",
    "video": "2026-09-26/video/abc123.mp4",
    "audio": "2026-09-26/audio/abc123.m4a",
    "info": "2026-09-26/info/abc123.info.json",
    "subtitle": "2026-09-26/subs/abc123.en.vtt"
  }
}
```

State được cập nhật sau từng video thay vì chờ toàn bộ batch hoàn thành.

Điều này giúp pipeline có thể tiếp tục an toàn nếu process bị dừng giữa chừng.

---

## 10. Error handling

Crawler được thiết kế để:

- Retry các request tới YouTube API.
- Ghi exception vào log.
- Bỏ qua video lỗi.
- Tiếp tục xử lý các video tiếp theo.
- Lưu state ngay sau khi một video hoàn thành.

Ví dụ:

```text
Video A → SUCCESS → save state
Video B → ERROR   → log error
Video C → SUCCESS → save state
Video D → SUCCESS → save state
```

Một video lỗi không làm mất toàn bộ batch.

---

## 11. Logging

Crawler tạo log trong:

```text
data_lake_local/youtube/state/
```

Ví dụ:

```text
crawl_2026-09-26.log
```

Log có thể chứa:

```text
Bat dau crawl YouTube
Tim thay 10 video phu hop
Da tai xong video abc123
Bo qua video xyz456 vi la YouTube Shorts
Loi khi tai video ...
Hoan tat crawl YouTube
```

---

## 12. Design principles

Crawler được chia thành các module theo **single responsibility**:

```text
cli.py
    CLI

config.py
    Configuration

filters.py
    Pure business logic

youtube_api.py
    YouTube Data API

downloader.py
    yt-dlp + filesystem

crawler.py
    Application workflow

main.py
    Entry point
```

Mục tiêu là tránh một file `main.py` chứa toàn bộ:

```text
configuration
+ API
+ filtering
+ downloading
+ state
+ logging
+ CLI
```

Thay vào đó mỗi module có một trách nhiệm rõ ràng và có thể test độc lập.

---

## 13. Execution flow

Toàn bộ crawler:

```text
                    ┌──────────────────┐
                    │   CLI / main.py  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    crawler.py    │
                    └────────┬─────────┘
                             │
                 ┌───────────┴───────────┐
                 ▼                       ▼
        ┌─────────────────┐      ┌─────────────────┐
        │ youtube_api.py  │      │    config.py    │
        └────────┬────────┘      └─────────────────┘
                 │
                 ▼
        YouTube Data API
                 │
                 ▼
          Candidate videos
                 │
                 ▼
        ┌─────────────────┐
        │   filters.py    │
        └────────┬────────┘
                 │
                 ▼
        Qualified videos
                 │
                 ▼
        ┌─────────────────┐
        │  downloader.py  │
        └────────┬────────┘
                 │
                 ▼
              yt-dlp
                 │
        ┌────────┼─────────┐
        ▼        ▼         ▼
      Video    Audio    Subtitle
                 │
                 ▼
              info.json
                 │
                 ▼
          Data Lake Local
```

---

## 14. Production considerations

Các phần hiện tại đã được tách để dễ mở rộng.

Các hướng cải tiến tiếp theo có thể bao gồm:

- Unit tests cho `filters.py`.
- Integration tests cho YouTube API.
- Structured logging.
- Download concurrency.
- Rate-limit handling.
- Schema validation cho configuration.
- Data quality checks sau khi download.
- Manifest/catalog cho Data Lake.
- Monitoring pipeline runs.
- Retry riêng theo loại lỗi HTTP/API.
- Checksum hoặc file integrity validation.

Những cải tiến này nên được thực hiện từng bước thay vì đưa tất cả vào crawler ngay từ đầu.
