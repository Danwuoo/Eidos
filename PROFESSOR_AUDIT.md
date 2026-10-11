# Professor-facing Repository Audit — Eidos

Eidos 目前適合以「研究構想與文件治理工具」展示。可執行的部分是文件載入、schema、關係與索引驗證；ARC 專用模型仍是未核准、未實驗的概念。此判斷依 [manifest](eidos.yaml)、[空的 governed-document 索引](docs/index.json)、[概念筆記](docs/從通用%20LLM%20到%20ARC%20專用推理架構.md) 與 [現有工具](tools/docs/system.py)。

- 審閱日期：2026-10-11。
- 審閱 HEAD：`df229adba549b26abd2dbc5a9c068e98aa12728e`。
- 文件角色：非規範、一次性的審閱敘述；不是 governed project record、研究結果或核准文件，不覆蓋 [AGENTS.md](AGENTS.md)。
- 起始工作樹乾淨；本次只修改 README 與本文件，未改程式、配置、資料、測試或生成索引。

## 評分與可核查依據

分數是本次 repository 審查判斷，不是研究成績。共用尺度：1＝入口或證據缺失；2＝部分具備且重要限制；3＝可沿文件核查但有公開前缺口；4＝易審閱且範圍內可重現；5＝獨立重現與個人歸屬完整。

| 面向 | 分數 | 本地依據與理由 |
|---|---:|---|
| Readiness | 2/5 | [README](README.md) 與 [eidos.yaml](eidos.yaml) 清楚標示 bootstrap；[索引](docs/index.json) 無正式研究紀錄。能展示工具與構想，無模型展示或研究完成紀錄。 |
| Readability | 3/5 | [README 閱讀入口](README.md#教授閱讀入口) 可沿 [概念筆記](docs/從通用%20LLM%20到%20ARC%20專用推理架構.md) 和 [system.py](tools/docs/system.py) 理解兩種內容；概念尚無正式問題定義、來源歸屬或實作對照。 |
| Verifiability | 3/5 | [validator](tools/docs/validate.py) 與 [5 項既有測試](tests/docs/test_documents.py) 本次通過；[依賴](tools/docs/requirements.txt) 僅設版本範圍，未做乾淨環境重建。可核查文件工具，無 ARC 結果可重現。 |
| Technical Depth | 2/5 | [system.py](tools/docs/system.py) 實作重複 YAML key、anchor/alias、路徑邊界、authority、ID 關係與循環檢查；[schema](docs/schema/document.schema.json) 定義文件合約。[ARC 筆記](docs/從通用%20LLM%20到%20ARC%20專用推理架構.md) 提出假設，但尚無 tokenizer、backbone 或實驗。 |
| Individual Contribution | 1/5 | [既有 README](README.md)、[筆記](docs/從通用%20LLM%20到%20ARC%20專用推理架構.md) 與 [工具](tools/docs/system.py) 沒有可逐項核查的本人／AI／第三方責任表。Git history 可追蹤版本，不能單獨證明全部由申請者完成。 |

## 教授可追問的技術路線

先讀 [構想](docs/從通用%20LLM%20到%20ARC%20專用推理架構.md) 最後的研究問題：較小模型能否透過狀態更新學會假說形成與修正？接著讀 [system.py](tools/docs/system.py) 的 `load_yaml`、`repo_path`、`validate_sources` 與 `validate_repository`，觀察如何防止文件 authority、關係與生成索引漂移。最後讀 [測試](tests/docs/test_documents.py)，區分「文件系統確實有可驗證行為」與「研究假設尚待測試」。

本次可讀性改善採閱讀導覽，未重構既有工具。

## 公開前必須處理

| 問題 | 依據 | 完成條件 |
|---|---|---|
| 個人貢獻與來源歸屬未確認 | [概念筆記](docs/從通用%20LLM%20到%20ARC%20專用推理架構.md)、[工具](tools/docs/system.py) | 由作者確認想法、文字、實作、測試各自的本人／AI／第三方範圍；只能引用既有真實紀錄。 |
| 根目錄未找到 LICENSE 或授權聲明 | 本次本地檔案盤點；[治理合約](AGENTS.md) 未指定公開授權 | 由權利人決定可公開與可再使用的範圍，釐清引用來源義務；本次不自行套用授權。 |
| 研究背景的技術來源與時點不足 | [概念筆記](docs/從通用%20LLM%20到%20ARC%20專用推理架構.md) 提及多個外部架構，未附原始來源 | 公開時將其明列為待驗證研究動機；若要作事實性比較，需由作者提供實際使用過的一手來源及日期。 |
| 乾淨環境重現尚未完成 | [requirements.txt](tools/docs/requirements.txt) | 若宣稱工具能獨立重現，需留下真實環境版本及乾淨安裝紀錄；目前只能宣稱本次既有環境檢查通過。 |

空的研究索引不是應由 README 補成成果的缺陷。正式 charter、模型、實驗與結果都不在本次外圍整理範圍；保持概念專案定位即可誠實展示。

## 可宣稱與不能宣稱

| 可由本 checkout 支持 | 目前不能支持 |
|---|---|
| 有可執行的文件治理工具及對應測試。[來源](tools/docs/system.py) | 已實作 ARC 專用模型、完成訓練或勝過通用 LLM。 |
| 有針對 mutable recurrent state／hypothesis revision 的研究構想。[來源](docs/從通用%20LLM%20到%20ARC%20專用推理架構.md) | 已證明泛化、效率、scaling law 或某 backbone 更適合 ARC。 |
| 在本次環境中 validator 與既有 5 項測試通過。[來源](tests/docs/test_documents.py) | 全新環境可完全重現研究結果，或這些測試證明研究假設。 |

既有想法與程式的本人／AI／第三方歸屬均未確認。本次 README 導覽與 audit 為 AI 協助撰寫，僅整理既有資料，不新增研究證據。

## 本次驗證與限制

在 repo 根目錄、Python 3.14.7 的既有環境執行：

```powershell
python -B -m tools.docs.validate
python -B -m unittest discover -s tests -v
```

validator 回傳 `Documentation system validation passed.`，5 項測試全數通過。測試依 [test_documents.py](tests/docs/test_documents.py) 在臨時目錄產生與驗證 fixture；`-B` 避免新增 Python bytecode。本次未執行依賴安裝、索引重建、模型實驗或外部技術來源查核；通過範圍僅是現有文件工具。
