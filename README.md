# Mini-moodle

## 專案目的

本專案為軟體工程課程的 Agile + AI 期中專案，由 3 人團隊於約 2 週內開發簡化版 Moodle。
預計功能包含教師與學生登入、教師建立課程、課程公告及課程留言板。

目前僅完成專案骨架與繁體中文首頁，四項功能皆尚未實作，也尚未建立資料模型或 SQLite 資料庫。

## 技術選擇

- Python 3.9 以上版本與 Flask。
- HTML、CSS、Bootstrap、Jinja2。
- SQLite（後續開發時整合，可使用 Python 內建的 `sqlite3`）。
- Git。

目前唯一直接依賴為 Flask，Jinja2 等必要套件會隨 Flask 安裝，不需另行加入資料庫或登入套件。
Bootstrap 樣式透過 CDN 載入，需要網路連線；本機 CSS 提供基本排版，無網路時首頁仍可顯示。

## 專案結構與用途

```text
Mini-moodle/
├── app/
│   ├── __init__.py          # 應用程式工廠與首頁路由
│   ├── models.py            # 資料模型預留位置
│   ├── routes/
│   │   ├── __init__.py      # 功能路由套件
│   │   ├── auth.py          # 登入功能預留位置
│   │   ├── courses.py       # 課程功能預留位置
│   │   ├── announcements.py # 公告功能預留位置
│   │   └── messages.py      # 留言板功能預留位置
│   ├── templates/
│   │   ├── base.html         # 共用頁面模板
│   │   ├── login.html        # 登入頁面預留模板
│   │   ├── dashboard.html    # 目前首頁
│   │   └── course_detail.html # 課程頁面預留模板
│   └── static/
│       └── css/
│           └── style.css    # 共用樣式
├── tests/
│   ├── __init__.py
│   └── test_app.py          # 首頁與靜態檔案煙霧測試
├── docs/
│   ├── requirements.md      # 需求說明
│   ├── user_stories.md      # 初步使用者故事草稿
│   ├── sprint_records.md    # 實際 Sprint 紀錄預留位置
│   ├── ai_usage_log.md      # 實際 AI 使用紀錄預留位置
│   └── uml/
│       └── .gitkeep         # 保留 UML 圖片目錄
├── config.py               # 共用設定
├── run.py                  # 本機啟動入口
├── requirements.txt        # Python 直接依賴
├── .gitignore              # 排除本機環境、快取、資料庫及機密設定
└── README.md
```

目前只有 `/` 首頁路由；登入與課程預留模板尚無對應路由。後續開發時再於 `app/routes/` 定義並註冊 Blueprint。

## 安裝環境

在 Repository 根目錄開啟 PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

直接使用虛擬環境的 Python，不需要啟用腳本或調整 PowerShell 執行原則。

macOS / Linux 可使用：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## 啟動方式

Windows PowerShell：

```powershell
.\.venv\Scripts\python.exe run.py
```

macOS / Linux：

```bash
.venv/bin/python run.py
```

開啟 <http://127.0.0.1:5000/>，應顯示「歡迎使用 Mini Moodle」。按 `Ctrl+C` 停止。
目前不需要 `.env`、帳號或資料庫初始化。此啟動方式使用 Flask 本機開發伺服器。

## 執行測試

Windows PowerShell：

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

macOS / Linux：

```bash
.venv/bin/python -m unittest discover -s tests -v
```

測試使用 Python 內建 `unittest` 與 Flask 測試用戶端，確認繁體中文首頁與本機 CSS 可正常回應；不需要額外測試套件。

## 團隊文件

需求與初步使用者故事位於 `docs/`。Sprint 與 AI 使用紀錄目前只有填寫指引，請依真實執行結果補充；UML 圖可放入 `docs/uml/`。
