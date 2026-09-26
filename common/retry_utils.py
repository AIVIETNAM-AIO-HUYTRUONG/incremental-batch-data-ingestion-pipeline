"""Decorator retry đơn giản cho các lời gọi KHÔNG đi qua `requests.Session`.

`common.http_utils.build_session` xử lý retry cho các request HTTP thô,
nhưng thư viện `googleapiclient` (dùng cho YouTube Data API) tự quản lý
kết nối HTTP riêng và ném ra `HttpError`/`socket.error` thay vì
`requests.exceptions.*`, nên không tận dụng được `urllib3.Retry`. Decorator
này cung cấp một cơ chế retry tương đương cho những trường hợp như vậy.
"""

import functools
import logging
import time
from typing import Callable, Optional, Tuple, Type, TypeVar

T = TypeVar("T")


def retry_on_exception(
    exceptions: Tuple[Type[BaseException], ...],
    max_attempts: int = 4,
    base_delay: float = 2.0,
    logger: Optional[logging.Logger] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Retry một hàm khi gặp exception thuộc `exceptions`.

    Dùng backoff theo cấp số nhân: `base_delay * 2**attempt` giây giữa các
    lần thử. Sau `max_attempts` lần thất bại liên tiếp, exception cuối
    cùng được ném lại cho tầng gọi xử lý.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exc: Optional[BaseException] = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:  # noqa: PERF203 - retry wrapper can can catch broadly by design
                    last_exc = exc
                    delay = base_delay * (2**attempt)
                    message = (
                        f"{func.__name__} Lỗi lần {attempt + 1}/{max_attempts}: "
                        f"{exc}. Thử lại sau {delay:.1f}s"
                    )
                    if logger:
                        logger.warning(message)
                    else:
                        print(message)
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
            assert last_exc is not None
            raise last_exc

        return wrapper

    return decorator
