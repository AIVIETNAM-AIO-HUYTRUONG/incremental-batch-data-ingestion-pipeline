"""Quản lý file trạng thái (state) dùng để tránh tải trùng dữ liệu.

Mỗi crawler có một thư mục state/ riêng, chứa file JSON ghi lại các ID
(video_id / photo_id) đã xử lý thành công. Trước khi thu thập, crawler
đọc file này để loại các ID đã có ra khỏi tập cần tải; sau khi tải xong
MỖI item, crawler ghi lại state ngay lập tức (không đợi đến cuối cùng)
để nếu tiến trình bị dừng giữa chừng (mất mạng, Task Scheduler bị kill,
mất điện...), lần chạy sau vẫn biết chính xác những gì đã xong.

Việc ghi file dùng chiến lược "ghi ra file tạm rồi rename" (atomic write)
để tránh trường hợp file JSON bị ghi dở dang (corrupt) nếu chương trình
bị ngắt đúng lúc đang ghi.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Union

PathLike = Union[str, Path]


def load_state(state_path: PathLike) -> Dict[str, Any]:
    """
    Đọc file trạng thái JSON.

    Trả về dict rỗng nếu file chưa tồn tại (lần chạy đầu tiên) hoặc nếu
    file bị hỏng (corrupt) - trong trường hợp này pipeline vẫn tiếp tục
    chạy được (có thể tải trùng vài item) thay vì crash hoàn toàn.
    """
    state_path = Path(state_path)
    if not state_path.exists():
        return {}
    try:
        with state_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_state(state_path: PathLike, data: Dict[str, Any]) -> None:
    """
    Ghi dict ra file JSON một cách atomic.

    Cách làm: ghi toàn bộ nội dung ra một file tạm (.tmp) trong CÙNG thư
    mục đích, sau đó dùng os.replace() để đổi tên đè lên file đích. Trên
    hầu hết hệ điều hành, os.replace() là một thao tác nguyên tử (atomic)
    ở cấp filesystem, nên tại bất kỳ thời điểm nào file đích hoặc là
    phiên bản cũ nguyên vẹn, hoặc là phiên bản mới nguyên vẹn - không bao
    giờ ở trạng thái ghi dở.
    """
    state_path = Path(state_path)
    state_path.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(dir=str(state_path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        os.replace(tmp_path, state_path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
