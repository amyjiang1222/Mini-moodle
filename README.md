# Mini-moodle

## 專案目的

本專案為軟體工程課程的 Agile + AI 期中專案，由 3 人團隊於約 2 週內開發簡化版 Moodle。
目前功能包含教師與學生登入、教師建立課程、學生使用課碼加入課程、課程公告（教師可修改）及課程留言板。

## 技術選擇

- Python 3.9 以上版本與 Flask。
- HTML、CSS、Bootstrap、Jinja2。
- SQLite（使用 Python 內建的 `sqlite3`）。
- Git。

目前唯一直接依賴為 Flask，Jinja2 等必要套件會隨 Flask 安裝。
Bootstrap 樣式透過 CDN 載入，需要網路連線。本機 CSS 提供基本排版。

## 專案結構與用途

```text
Mini-moodle/
├── app/
│   ├── __init__.py          # 應用程式工廠與首頁路由
│   ├── models.py            # 資料模型與資料存取
│   ├── routes/
│   │   ├── __init__.py      # 功能路由套件
│   │   ├── auth.py          # 登入功能
│   │   ├── courses.py       # 課程功能
│   │   ├── announcements.py # 公告功能
│   │   └── messages.py      # 留言板功能
│   ├── templates/
│   │   ├── base.html         # 共用頁面模板
│   │   ├── login.html        # 登入頁面
│   │   ├── dashboard.html    # 首頁
│   │   ├── course_new.html   # 建立課程
│   │   ├── course_detail.html # 課程頁面
│   │   └── announcement_edit.html # 修改公告
│   └── static/
│       └── css/
│           └── style.css    # 共用樣式
├── tests/
│   ├── __init__.py
│   └── test_app.py          # 功能測試
├── docs/
│   ├── requirements.md      # 需求說明
│   ├── user_stories.md      # 使用者故事
│   ├── sprint_records.md    # 工作紀錄
│   ├── ai_usage_log.md      # AI 使用紀錄
│   └── uml/system_diagrams.md   # UML 圖
├── config.py               # 共用設定
├── run.py                  # 本機啟動入口
├── requirements.txt        # Python 直接依賴
├── .gitignore              # 排除本機環境、快取、資料庫及機密設定
└── README.md
```

## 安裝環境

在 Repository 根目錄開啟 PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

macOS / Linux 可使用：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## 啟動方式

先建立帳號，執行兩次並分別選擇 `teacher` 和 `student`：

Windows PowerShell：

```powershell
.\.venv\Scripts\flask.exe --app run.py create-user
```

macOS / Linux：

```bash
.venv/bin/flask --app run.py create-user
```

Windows PowerShell：

```powershell
.\.venv\Scripts\python.exe run.py
```

macOS / Linux：

```bash
.venv/bin/python run.py
```

資料庫會建立在 `instance/mini_moodle.sqlite3`。開啟 <http://127.0.0.1:5000/> 登入，按 `Ctrl+C` 停止伺服器。

## 執行測試

Windows PowerShell：

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

macOS / Linux：

```bash
.venv/bin/python -m unittest discover -s tests -v
```

## 團隊文件

需求、使用者故事、工作紀錄、AI 使用紀錄與 UML 圖位於 `docs/`。
