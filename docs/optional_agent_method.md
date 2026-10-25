# Optional：單人 AI-agent 方法（需求分析階段，本地草稿）

## 方法名稱與題目

**Human-gated Spec Loop**。同一個 Mini Moodle 題目，範圍到需求分析與 UML，不把程式碼量當成此方法的評分證據。由吳定栩一人承擔第三組的人工責任，Codex 擔任提案、檢查與整理的 AI agent。此法借用 spec-driven 的「先定規格再規劃」概念，並未聲稱使用 GitHub Spec Kit 或 AWS AI-DLC 工具。

## 角色與責任

| 角色 | 工作 | 可作的決定 |
| --- | --- | --- |
| 人類 Product Owner / 審核者：吳定栩 | 確定題目、範圍、優先順序，批准或退回每版規格；對結果負責 | 接受需求、批准進入下一關、批准提交 |
| AI agent：Codex | 從來源提取需求、提出故事與驗收條件、找歧義與衝突、繪 UML 草稿、保留工作紀錄 | 依人類授權執行和記錄決定；不能冒稱團隊已正式接受 |
| 既有 Agile 團隊 | 提供 Jira 故事與實作背景 | Agile 的估點、Sprint 承諾仍由團隊決定 |

## 工件與循環

1. **Collect**：固定來源版本，記錄 Moodle 簡報、Jira issue ID 與 Git commit SHA。
2. **Specify**：agent 草擬需求、使用者故事、驗收條件和 UML；逐條標來源。
3. **Challenge**：agent 對每條需求檢查歧義、遺漏、衝突和自行發明的功能；修訂來源須有明確授權與變更紀錄。
4. **Human gate A**：人類接受、修改或授權 agent 判斷需求草稿，記錄授權範圍和理由；團隊正式接受仍須另記。
5. **Plan**：agent 只根據已接受規格提出任務及依賴；人工再審核。這次課堂範圍到需求分析，計畫可作展示，不代表已執行。
6. **Human gate B**：人類決定是否把工件提供團隊審查；草稿 PR 與正式合併分開記錄。

## 本次實際試跑與審核證據

- 輸入：2026-10-25 Moodle 簡報、Jira MM-1/2/9/3/4 與 repo `5edb827`。
- Agent 工件：`requirements.md`、`user_stories.md`、`uml/system_diagrams.md`、`ai_usage_log.md`。
- Challenge 結果：MM-2 敘述錯置；MM-9 缺錯誤課碼與重複加入條件；「公告修改」範圍未定。
- Human gate A：2026-10-26 使用者說「人工判斷的部分，那看你要怎麼改，可以讓它全部動」，授權 agent 處理上述歧義。Agent 選擇修正 MM-2 誤貼文字、補 MM-9 拒絕路徑、將 MM-3 界定為原課教師可修改；已在 Jira 留下變更。這是授權決策，不等於其他團隊成員逐條接受。
- Human gate B：使用者授權先推進工作；正式合併及交作業的接受紀錄仍應獨立留下。

## 與另外兩種方法的比較欄位

| 證據 | Waterfall + AI | Agile + AI | Human-gated Spec Loop |
| --- | --- | --- | --- |
| 主要工件 | PRD/SRS 與變更審核 | Jira Story、Sprint/看板紀錄 | 帶來源的規格、agent 審查紀錄、人工關卡 |
| 人工接受點 | 每份文件進下一階段前 | PO 接受 Story、團隊承諾 Sprint | 每版規格與計畫前 |
| 本次待填實測 | 由 Waterfall 組提供 | Jira 與 Git 紀錄 | 本文件及審查表 |

## 規則

不在提示中放機密資料；只用公開課堂題目和虛構展示帳號。AI 的提案與測試不等於團隊接受；需清楚區分個人授權、團隊審閱、正式繳交。
