# Optional agent 計畫（本次試跑）

狀態：草稿；2026-10-26 使用者授權 agent 處理歧義，團隊正式接受關卡尚未完成。

## 任務

以 Mini Moodle 的五個 Jira Story 作來源，產生需求分析所需的規格、歧義審查、UML 與人類審核清單。和 Agile 原型共用同一題目，但不把原型程式碼當作 Optional 需求分析的完成條件。

## 輸入快照

- Moodle `Midterm_Project_2026.pdf`，本地參考副本位於課程資料夾 `reference/`。
- Jira MM-1、MM-2、MM-9、MM-3、MM-4 及 MM-5～MM-8。
- GitHub Mini-moodle 的起始 commit `5edb827`。

## Agent 執行步驟與輸出

1. 提取明確需求，並在 `requirements.md` 標示來源。
2. 找出矛盾和未定義行為，寫入 `user_stories.md`；不可自稱為已接受的需求。
3. 依需求草稿繪製 `uml/system_diagrams.md`。
4. 在 `ai_usage_log.md` 保留 AI 的作用、檢查和人工審核狀態。
5. 記錄人類授權的範圍；把 agent 的實作選擇與團隊正式接受分開。

## 停止條件

若來源衝突，先標記並向人類說明。2026-10-26 使用者已授權 agent 處理上述歧義並更新 Jira；其餘未獲授權的重大範圍變更仍需另行記錄。草稿分支與正式合併、繳交分開。
