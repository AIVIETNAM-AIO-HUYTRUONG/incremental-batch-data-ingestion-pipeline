"""
Tiện ích dùng chung: đọc cấu hình YAML và nạp biến môi trường (.env).
"""

import os
from pathlib import Path
from typing import Any, Dict, Union

import yaml
from dotenv import load_dotenv

PathLike = Union[str, Path]

def load_yaml_config(config_path: PathLike) -> Dict[str, Any]:
    """Đọc file cấu hình YAML và trả về dict.

    Raises:
        FileNotFoundError: nếu không tìm thấy file cấu hình.
        yaml.YAMLError: nếu file YAML sai định dạng.
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file cấu hình: {config_path}. "
            f"truyền --config đường-dẫn-tời-file.yaml"
        )

    with config_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if not isinstance(data, dict):
        raise yaml.YAMLError(f"File cấu hình {config_path} phải là một mapping (dict)")

    return data

def load_env(env_path: PathLike | None = None) -> None:
    """
    Nạp file .env vào biến môi trường của tiến trình hiện tại.

    Nếu `env_path` được chỉ định và tồn tại thì dùng file đó. Nếu không,
    `python-dotenv` sẽ tự tìm file `.env` ở thư mục hiện tại hoặc các thư
    mục cha (hành vi mặc định của `load_dotenv()`).

    `override=False`: biến môi trường đã được set từ trước (vd export
    trong shell, hoặc biến môi trường của CI/CD) luôn được ưu tiên hơn
    giá trị trong file .env.
    """
    if env_path is not None:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=False)
            return 
    load_dotenv(override=False)
    pass

def require_env(key: str) -> str:
    """Lấy biến môi trường bắt buộc; ném lỗi rõ ràng, dễ debug nếu thiếu."""
    value = os.environ.get(key)
    if not value:
        raise EnvironmentError(
            f"Thiếu biến môi trường bắt buộc: '{key}'. "
            f"Hãy tạo file .env (xem .env.example) và khai báo '{key}=...', "
        )
    return value