# Eidos

Eidos 是一個研究工作區，目前包含可執行的文件治理工具，以及一份探索 ARC 專用推理架構的早期構想。工具處理文件的結構、權威狀態、關係與索引一致性；研究構想尚未形成可執行模型。

## 目前範圍

| 部分 | 內容與狀態 |
| --- | --- |
| 文件治理工具 | YAML 載入、schema 驗證、路徑邊界、文件 ID／關係與循環檢查、生成索引一致性檢查。 |
| ARC 構想 | 探索 mutable recurrent state、hypothesis revision 與 synthetic program induction；尚無模型、訓練程式或實驗結果。 |
| 正式研究紀錄 | 專案仍處於 bootstrap；[生成索引](docs/index.json) 的 `documents` 為空，正式 charter 與研究架構尚未核准。 |

## 從哪裡開始

- [ARC 概念筆記](docs/從通用%20LLM%20到%20ARC%20專用推理架構.md)：研究問題與待驗證假設。
- [文件系統實作](tools/docs/system.py)：依 `load_yaml` → `validate_sources` → `expected_index` → `validate_repository` 閱讀。
- [文件 schema](docs/schema/document.schema.json) 與 [測試](tests/docs/test_documents.py)：對照資料契約及 fixture 行為。
- [AGENTS.md](AGENTS.md) 與 [eidos.yaml](eidos.yaml)：修改文件時的工作流程與機器可讀入口。

## 執行文件檢查

在 repository 根目錄執行；依賴見 [requirements.txt](tools/docs/requirements.txt)。

```sh
python -m pip install -r tools/docs/requirements.txt
python -B -m tools.docs.validate
python -B -m unittest discover -s tests -v
```

新增或修改 governed YAML records 後，先產生索引，再驗證：

```sh
python -B -m tools.docs.build_index
python -B -m tools.docs.validate
```

`build_index` 會寫入 `docs/index.json`，不要手動修改生成索引。Markdown README 與概念筆記不是正式規範紀錄，也不取代 YAML 文件的核准狀態。

## 限制

測試與 validator 的通過範圍是文件工具，不是 ARC 正確率、模型泛化或研究假設的驗證。依賴目前只有版本範圍，尚未提供完整鎖定環境。概念筆記中的外部架構比較仍需補齊原始來源；repository 目前未附 LICENSE。
