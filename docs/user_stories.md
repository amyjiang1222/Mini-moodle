# Agile 使用者故事與驗收檢查（本地草稿）

來源：2026-10-25 起檢視 Jira [Mini moodle backlog](https://jiangguancih42173217amy.atlassian.net/jira/software/projects/MM/boards/2/backlog)。2026-10-26 使用者授權處理需求歧義，MM-2、MM-9、MM-3 描述已在 Jira 更新；故事狀態、估點與 Sprint 仍以 Jira 為準。團隊正式審閱仍待完成。

| Epic | Story | 目前目標 | 本地對應 |
| --- | --- | --- | --- |
| MM-5 登入 | [MM-1](https://jiangguancih42173217amy.atlassian.net/browse/MM-1) | 教師與學生以有效帳密登入，依角色限制功能，錯誤帳密提示 | `app/routes/auth.py` |
| MM-6 課程 | [MM-2](https://jiangguancih42173217amy.atlassian.net/browse/MM-2) | 教師建立課程：名稱、描述、非空名稱、清單顯示、2 大寫字母 + 7 數字課碼 | `app/routes/courses.py` |
| MM-6 課程 | [MM-9](https://jiangguancih42173217amy.atlassian.net/browse/MM-9) | 學生輸入課碼後加入並查看課程內容 | `app/routes/courses.py` |
| MM-7 公告 | [MM-3](https://jiangguancih42173217amy.atlassian.net/browse/MM-3) | 該課教師發布及修改公告，學生可查看但不能修改 | `app/routes/announcements.py` |
| MM-8 留言 | [MM-4](https://jiangguancih42173217amy.atlassian.net/browse/MM-4) | 課程成員留言、查看發言者與內容，禁止空白留言 | `app/routes/messages.py` |

## 已處理的需求歧義與仍待團隊核對的範圍

1. **MM-2 描述貼錯**：已在 Jira 將誤貼的公告敘述改為建課目標，保留原有驗收條件。
2. **MM-9 驗收條件不足**：已在 Jira 補上不存在課碼提示、重複加入，以及未加入者不可看課程內容；本地原型與測試涵蓋這三項。
3. **MM-1 帳號來源未定**：Jira 只要求「有效帳密」，沒有指定註冊或帳號管理流程。本地原型以管理者指令建立帳號，避免自行發明公開註冊功能。
4. **MM-3 的「修改」範圍**：已在 Jira 補上「該課教師可修改標題與內容」，本地原型也已實作並測試；不含刪除及版本歷史。
5. **Sprint 證據尚未形成**：檢視時五個 Story 都在 backlog，無故事點、受託人或 Sprint。估點與承諾應由團隊決定，不能用 AI 的數值直接代替。

## 本地驗收結果與限制

`python -m unittest discover -s tests -v` 的整合測試涵蓋五個故事的主要成功與拒絕路徑。這是本地原型驗證，**不代表** Product Owner 已接受故事，也不代表 Jira 已進入進行中或完成。
