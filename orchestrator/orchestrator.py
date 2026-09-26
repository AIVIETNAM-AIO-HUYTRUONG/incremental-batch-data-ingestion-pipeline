from datetime import datetime
from pathlib import Path
from typing import List

from .runner import run_python
from .config import JOB_SCRIPTS


def run_job(
    job: str,
    run_log,
) -> int:
  """
  Thực thi một job và ghi lại kết quả vào log.
  
  Args:
      job: Tên job cần chạy.
      run_log: File object dùng để ghi log.
  
  Returns:
      int: Exit code của job.
  """
  start = datetime.now()

  run_log.write(
    f"[{start: %Y-%m-%d %H:%M:%S}]"
    f"Bắt đầu job={job}\n"
  )

  run_log.flush()

  print(f"Đang chạy job: {job} ...")

  rc = run_python(JOB_SCRIPTS[job])

  end = datetime.now()

  status = ("OK" if rc == 0 else f"Lỗi (exit code {rc})")

  run_log.write(
      f"[{end:%Y-%m-%d %H:%M:%S}] "
      f"Kết thúc job={job} - {status} "
      f"- thời gian chạy: {end - start}\n\n"
  )
  run_log.flush()
  
  print(
      f"<== Job '{job}' hoàn tất: {status}"
  )
  
  return rc


def run_pipeline(
  jobs:List[str],
  run_log_path:Path
)->int:
  """
  Thực thi theo thứ tự danh sách job của Data Pipeline.

  Pipeline không dừng khi một job thất bại. 
  Nó tiếp tục chạy các job còn lại và ghi nhận exit code của lỗi đầu tiên.
  
  Args:
    - jobs: Danh sách job cần chạy.
    - run_log_path: Đường dẫn đến file log của lần chạy.

  Returns:
    - int: Exit code của job thất bại đầu tiên,
      Trả về "0" nếu tất cả job thành công. 

  """

  exit_code = 0

  with run_log_path.open("w",encoding="utf-8") as run_log:
    run_log.write(
      f"Chạy pipeline với jobs = {jobs}\n\n"
    )

    for job in jobs:
      rc = run_job(
        job=job,
        run_log=run_log,
      )

      if rc != 0 and exit_code == 0:
        exit_code = rc

    run_log.write(
      f"Kết quả cuối cùng: "
      f"exit_code={exit_code}\n"
    )
    
  return exit_code