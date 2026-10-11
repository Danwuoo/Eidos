# Eidos

Eidos is bootstrapping an agent-first research repository. The formal project charter and research architecture have not been approved yet.

Agents start with [`AGENTS.md`](AGENTS.md) and [`eidos.yaml`](eidos.yaml). Governed documents are YAML records discovered through the generated [`docs/index.json`](docs/index.json).

The Chinese ARC document currently in `docs/` is an early concept note only; it is not a formal project document.

## 教授閱讀入口

目前可審閱的是 **ARC 研究構想與可執行的文件治理工具**。本 checkout 沒有 ARC 模型、訓練程式、資料集或實驗結果；[`docs/index.json`](docs/index.json) 的 `documents` 仍為空。研究構想不能當作已實作或已驗證的能力。

建議依序閱讀：

1. [Professor-facing Repository Audit](PROFESSOR_AUDIT.md)：準備度、可核查範圍與公開前缺口。
2. [早期 ARC 構想](docs/從通用%20LLM%20到%20ARC%20專用推理架構.md)：mutable recurrent state、hypothesis revision 與 synthetic program induction 的待驗證假設。
3. [`tools/docs/system.py`](tools/docs/system.py)：依 `load_yaml` → `validate_sources` → `expected_index` → `validate_repository` 閱讀現有實作；再對照 [既有測試](tests/docs/test_documents.py)。

概念筆記與本次 audit 都是非規範敘述，不改變 YAML 文件治理或核准狀態。本人、AI 與第三方的既有貢獻歸屬尚未確認；根目錄也未找到 LICENSE，詳見 audit。

## Documentation commands

以下命令在 repo 根目錄執行，只檢查文件系統。本次於 Python 3.14.7 的既有環境執行 validator 與 5 項既有測試成功；安裝命令僅核對來源，未在全新環境重新安裝。依賴範圍見 [requirements.txt](tools/docs/requirements.txt)，目前沒有完整版本鎖定。

```powershell
python -m pip install -r tools/docs/requirements.txt
python -B -m tools.docs.validate
python -B -m unittest discover -s tests -v
```

新增或變更 governed YAML records 後，依 [`AGENTS.md`](AGENTS.md) 先執行 `python -B -m tools.docs.build_index`，再驗證。此命令會寫入生成索引；本次審閱沒有重建索引。以上通過不代表 ARC 研究假設成立。

