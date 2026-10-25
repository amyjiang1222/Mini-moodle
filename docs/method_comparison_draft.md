# 三種方法比較：報告用證據草稿

此表是報告骨架；Waterfall 小組證據和人工工時仍須由該組提供，不能虛構。

| 比較項 | Waterfall + AI | Agile + AI | Optional：Human-gated Spec Loop |
| --- | --- | --- | --- |
| 本次主工件 | 待 Waterfall 組提供 PRD/SRS、UML 與至少三次經審查變更 | Jira MM-1/2/9/3/4、看板、`user_stories.md`、`sprint_records.md`、UML | `optional_agent_method.md`、規格、agent 計畫與紀錄摘錄 |
| AI 做了甚麼 | 待 Waterfall 組填寫實際提示與審核 | 整理故事、找需求矛盾、產生本地原型與測試 | 提取來源、提出規格、挑出矛盾、畫 UML 草稿 |
| 誰接受 | 每份文件的具名審核者；待填實際人名和證據 | 使用者授權 agent 處理歧義；團隊的 Story 接受和 Sprint 承諾仍待記錄 | 第三組負責人授權 agent 判斷三項歧義；逐條正式接受紀錄仍待完成 |
| 拒絕 / 修訂案例 | 待填真實案例 | MM-2 敘述與驗收條件衝突；已修正 Jira 敘述 | MM-2 衝突在 Challenge 關卡提出，經使用者授權後才修正來源 |
| 時間 | 待實測 | 待實測 | 待實測 |
| 版本連結 | 待 Waterfall 組提供 | [草稿 PR #1](https://github.com/amyjiang1222/Mini-moodle/pull/1)；Jira MM-2、MM-9、MM-3 已更新文字，仍待團隊審閱 | [草稿 PR #1](https://github.com/amyjiang1222/Mini-moodle/pull/1)；正式接受紀錄待補 |

報告結論須在實際比較後寫；測試通過只能證明原型行為，不能代替需求接受或宣稱 AI 節省了時間。
