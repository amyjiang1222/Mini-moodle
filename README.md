# Mini-moodle

## 專案目的

本專案為軟體工程課程的 Agile + AI 期中專案，由 3 人團隊於約 2 週內開發簡化版 Moodle。
預計功能包含教師與學生登入、教師建立課程、課程公告及課程留言板。

本地 `dingxu/agile-optional` 草稿分支已實作登入、建課、課碼加入、公告（含教師修改）與留言；此版本尚待團隊審查，Jira 狀態不代表已完成。

## 技術選擇

- Python 3.9 以上版本與 Flask。
- HTML、CSS、Bootstrap、Jinja2。
- SQLite（後續開發時整合，可使用 Python 內建的 `sqlite3`）。
- Git。

目前唯一直接依賴為 Flask；SQLite 使用 Python 內建 `sqlite3`，密碼雜湊使用 Flask 所依賴的 Werkzeug。
Bootstrap 樣式透過 CDN 載入，需要網路連線；本機 CSS 提供基本排版，無網路時首頁仍可顯示。

## 專案結構與用途

```text
Mini-moodle/
├── app/
│   ├── __init__.py          # 應用程式工廠與首頁路由
│   ├── models.py            # SQLite 結構與資料存取
│   ├── routes/
│   │   ├── __init__.py      # 功能路由套件
│   │   ├── auth.py          # 登入與角色權限
│   │   ├── courses.py       # 建課、加入與課程頁
│   │   ├── announcements.py # 課程公告
│   │   └── messages.py      # 課程留言板
│   ├── templates/
│   │   ├── base.html         # 共用頁面模板
│   │   ├── login.html        # 登入頁
│   │   ├── dashboard.html    # 首頁與課程清單
│   │   ├── course_new.html   # 建立課程
│   │   ├── course_detail.html # 課程、公告與留言
│   │   └── announcement_edit.html # 教師修改公告
│   └── static/
│       └── css/
│           └── style.css    # 共用樣式
├── tests/
│   ├── __init__.py
│   └── test_app.py          # 五個 Story 的流程與權限測試
├── docs/
│   ├── requirements.md      # 需求說明
│   ├── user_stories.md      # Jira Story 核對與修訂建議
│   ├── sprint_records.md    # 本地實際工作紀錄
│   ├── ai_usage_log.md      # AI 使用與人工審核狀態
│   ├── optional_agent_method.md # 第三種方法草稿
│   └── uml/system_diagrams.md   # 類別與循序圖
├── config.py               # 共用設定
├── run.py                  # 本機啟動入口
├── requirements.txt        # Python 直接依賴
├── .gitignore              # 排除本機環境、快取、資料庫及機密設定
└── README.md
```

本地原型使用 Flask Blueprint 實作上述流程。帳號由管理者在本機建立，沒有公開註冊頁；請使用虛構展示帳號。

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

先建立虛構展示帳號：

```powershell
.\.venv\Scripts\flask.exe --app run.py create-user
```

依提示建立至少一名 `teacher` 和一名 `student`。資料庫會自動建立在 `instance/mini_moodle.sqlite3`，並由 `.gitignore` 排除。開啟 <http://127.0.0.1:5000/>，登入後可建立課程並用課碼加入。按 `Ctrl+C` 停止。此啟動方式使用 Flask 本機開發伺服器；`MINI_MOODLE_SECRET_KEY` 可設定固定的本機 session 金鑰。

## 執行測試

Windows PowerShell：

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

macOS / Linux：

```bash
.venv/bin/python -m unittest discover -s tests -v
```

測試使用 Python 內建 `unittest` 與 Flask 測試用戶端，檢查登入、角色限制、課碼格式與加入、無效與重複課碼、公告發布及修改權限、留言、非成員存取和空白輸入；不需要額外測試套件。

## 團隊文件

需求、Jira 審核表、實際本地工作紀錄、AI 使用紀錄、Optional 方法與 UML 都在 `docs/`。尚未人工接受的項目均標為草稿，不能直接當成 Jira 完成紀錄。
