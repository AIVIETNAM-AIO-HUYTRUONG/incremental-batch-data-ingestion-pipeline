# Flow chạy thực tế

```bash
python -m orchestrator --job yt
```

                python -m orchestrator --job yt
                              │
                              ▼
                         __main__.py
                              │
                              ▼
                            main()
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
        parse_args()    parse_job_argument()  create_run_log()
             │                │                │
             │             ["yt"]              │
             │                │                │
             └────────────────┼────────────────┘
                              ▼
                       run_pipeline()
                              │
                              ▼
                          run_job("yt")
                              │
                              ▼
                    JOB_SCRIPTS["yt"]
                              │
                              ▼
                   crawl_yt_video_audio/main.py

# Khi chạy `--job all`

```bash
python -m orchestrator --job all
```

```text
"all"
  │
  ▼
parse_job_argument()
  │
  ▼
JOB_ORDER
  │
  ├── arxiv
  ├── yt
  └── unsplash
        │
        ▼
   run_pipeline()
        │
        ├── run_job("arxiv")
        │
        ├── run_job("yt")
        │
        └── run_job("unsplash")

```
