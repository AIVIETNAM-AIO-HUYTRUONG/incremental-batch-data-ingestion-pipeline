from orchestrator.orchestrator import run_pipeline
from orchestrator.config import LOG_DIR
import sys

from pathlib import Path
from datetime import datetime
from typing import Optional, List
from .cli import parse_args
from .job_manager import parse_job_argument

def create_run_log() -> Path:
  """
  Tạo đường dẫn cho file log của mỗi lần chạy pipeline.

  Return:
    Path: Đường dẫn đến file log.
  """
  LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
  )

  return LOG_DIR / (
    f"run_{datetime.now():%Y-%m-%d_%H%M%S}.log"
  )

  pass

def main(
  argv:Optional[List[str]] = None
)->int:
  """
  Điều phối quá trình chạy Data Pipeline

  Args:
    - arvg: Danh sách tham số từ command line.
      - Nếu "None", argparse đọc từ "sys.argv".
  
  Return:
    int: Exit code của pipeline.
  """

  args = parse_args(argv)
  jobs = parse_job_argument(args.job)
  
  run_log_path = create_run_log()

  exit_code = run_pipeline(
    jobs=jobs,
    run_log_path=run_log_path,
  )
  
  print(
    f"Log đầy đủ của lần chạy này:"
    f"{run_log_path}"
  )
  
  return exit_code 
  
if __name__ == "__main__":
  sys.exit(main())