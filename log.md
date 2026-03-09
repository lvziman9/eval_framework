# Eval Framework 开发日志

## 项目目标
为知识图谱增强推荐模型（PGPR、VRKG4Rec、CAFE 等）构建统一的可解释性评估框架，集成 Balloccu et al. SIGIR 2022 的 LIR/SEP/ETD 指标。

---

## 2026-02-24

### 架构决策

**初始设计 → 重构**

最初设计了完整的 `evaluation/`、`scripts/`、`config/` 目录，但复查后发现 [giacoballoccu/explanation-quality-recsys](https://github.com/giacoballoccu/explanation-quality-recsys) 已实现全套指标，重复造轮子。

**最终架构**：
```
eval_framework/
├── xrecsys/                  # clone 原始 xrecsys 库（原封不动为主）
│   ├── datasets/ml1m/        # ML1M 数据集（从 Google Drive 下载）
│   ├── datasets/lastfm/      # LastFM 数据集（从 Google Drive 下载）
│   ├── paths/ml1m/           # 预计算路径 CSV（从 Google Drive 下载）
│   ├── paths/lastfm/         # 预计算路径 CSV（从 Google Drive 下载）
│   ├── models/PGPR/          # PGPR 模型代码 + tmp/ml1m/ + tmp/lastfm/
│   ├── metrics.py            # LIR / SEP / ETD / NDCG / HR / Recall / Precision
│   ├── path_data_loader.py   # 加载 CSV → path_data 对象
│   ├── myutils.py            # 辅助函数
│   └── main.py               # 入口
├── adapters/                 # 各模型输出 → xrecsys 标准 CSV 格式转换器
│   ├── base_adapter.py
│   ├── pgpr_adapter.py
│   └── vrkg4rec_adapter.py
├── results/                  # 评估结果输出
└── log.md                    # 本文件
```

**核心原则**：各模型在自己的 conda 环境里训练/推理，输出标准 3-CSV 格式；`eval_frame` 环境统一跑 xrecsys 评估。

---

### 环境配置

| 环境 | Python | Torch | 用途 |
|------|--------|-------|------|
| `eval_frame` | 3.8.20 | 1.10.1+cu102 | 统一评估框架 |
| `pgpr_env` | 3.7.12 | 1.10.1 | PGPR 训练推理 |
| `vrkg4rec` | 3.8.20 | 1.10.1 | VRKG4Rec 训练推理 |

**eval_frame 已安装包**：pandas 1.4.3, numpy 1.24.4, scipy 1.10.1, networkx 3.1, matplotlib 3.7.5, seaborn 0.13.2, pyyaml 6.0.3, easydict 1.13, tqdm 4.67.3, torch 1.10.1, gdown

---

### 数据准备

**下载来源（Google Drive）**：
| 文件 | ID | 大小 | 内容 |
|------|----|------|------|
| datasets.zip | `1P2TOG_6Rrmsp6oK9aH3mNSb_i3TLF-d1` | 467M | ml1m + lastfm 预处理数据集 |
| paths_ml1m.zip | `1b6HgNJvHGPZs6q3PMaMBHT89pW46Lw7J` | 143M | ml1m 预计算路径 CSV |
| paths_lastfm.zip | `1gf9TyRN39Tc0I8immOzn9FK3e14pUpvi` | 232M | lastfm 预计算路径 CSV |
| tmp_ml1m.zip | `1HWp7I-0qW1XesUE_WZ6nZ0DHFALnfRrJ` | 332M | ml1m kg.pkl + labels + agent ckpts |
| tmp_lastfm.zip | `17EUgh299U8y0bqPYT39sdMzhjjzlahSG` | 2.0G | lastfm kg.pkl + labels + agent ckpts |

**最终目录结构**：
- `xrecsys/datasets/{ml1m,lastfm}/` — 数据集文件（train.txt, test.txt, mappings/, entities/ 等）
- `xrecsys/paths/{ml1m,lastfm}/agent_topk={10-12-1,25-50-1}/` — pred_paths.csv, uid_topk.csv, uid_pid_explanation.csv
- `xrecsys/models/PGPR/tmp/{ml1m,lastfm}/` — kg.pkl, train_label.pkl, test_label.pkl, transe_embed.pkl

**备注**：原作者预计算的 kg.pkl（ml1m: 5.5M, lastfm: 12M）与我们用 preprocess.py 重新生成的（ml1m: 5.3M, lastfm: 11M）有差异，路径 CSV 中的实体 ID 与原作者 kg.pkl 对应，因此使用原作者版本。自生成的备份保留为 `*.generated.pkl`。

---

### Bug 修复记录

所有修改均在 `xrecsys/` 内部，不影响原库外部接口。

#### 1. `models/PGPR/utils.py` — torch 非必要强依赖
**问题**：`import torch` 在模块顶层，preprocess.py 不需要 torch 也无法导入。  
**修复**：改为 try/except，torch 不可用时降级为 `None`。
```python
# 修改前
import torch
# 修改后
try:
    import torch
except ImportError:
    torch = None
```

#### 2. `models/PGPR/data_utils.py` — import 路径冲突
**问题**：`from models.PGPR.utils import ...` 假设工作目录是 xrecsys 根目录，但 preprocess.py 假设工作目录是 PGPR 目录，两者矛盾。  
**修复**：改为相对 import `from utils import ...`，统一从 PGPR 目录运行。

#### 3. `models/PGPR/knowledge_graph.py` — 同上 + KeyError
**问题①**：同 data_utils.py 的 import 路径矛盾。  
**问题②**：`_add_edge()` 不检查节点是否存在就直接索引，lastfm 数据集中某些 review 里的 uid 不在实体表里导致 KeyError。  
**修复①**：`from models.PGPR.utils import *` → `from utils import *` 等。  
**修复②**：在 `_add_edge()` 开头加节点存在性检查。
```python
def _add_edge(self, etype1, eid1, relation, etype2, eid2):
    if eid1 not in self.G[etype1] or eid2 not in self.G[etype2]:
        return  # 新增：跳过不存在的节点
    ...
```

#### 4. `path_data_loader.py` — generate_SEP_matrix 除以零
**问题**：ml1m 中 `composed_by` 关系为空（0条边），max - min = 0，归一化时除以零。  
**修复**：加 `if range_val > 0` 判断，为零时直接置 0.0。

#### 5. `path_data_loader.py` — normalized_ema 除以零
**问题**：LIR 和 SEP 矩阵计算中 `normalized_ema` 函数同样可能 max == min。  
**修复**：两处均加 `if max_res == min_res: return [0.0] * len(ema_vals)`。

#### 6. `metrics.py` — SEP_matrix KeyError
**问题**：预计算路径中的实体 ID 不在 SEP_matrix 里（路径和 kg.pkl 版本不对应）。  
**修复**：`SEP_matrix[type][id]` → `SEP_matrix.get(type, {}).get(id, 0.0)`。

#### 7. `path_data_loader.py` — LIR/SEP 矩阵无 cache，每次重算导致运行超慢
**问题**：`generate_SEP_matrix()` 需要遍历整个 KG 所有实体节点做 EMA，`generate_LIR_matrix()` 遍历所有 test user 的历史时间戳，每次启动都重算，耗时极长。  
**修复**：增加 `_load_or_generate_SEP_matrix()` 和 `_load_or_generate_LIR_matrix()` 方法，第一次计算后 pickle 到 `tmp/{dataset}/sep_matrix.pkl` 和 `lir_matrix.pkl`，后续直接加载。

---

### 当前状态（截至 2026-02-24 02:33）

- [x] xrecsys repo clone 到 `eval_framework/xrecsys/`
- [x] 数据集和预计算路径全部下载解压到位
- [x] preprocess.py 成功生成 ml1m + lastfm 的 kg/label pkl（备份用）
- [x] 原作者预计算 pkl 替换到位（与路径 CSV 实体 ID 匹配）
- [x] 所有 Bug 修复完成
- [⏳] ml1m 基线评估后台运行中（PID 2139480）—— 第一次运行需生成 SEP/LIR cache
- [ ] adapters 重写（输出直接到 `xrecsys/paths/` 格式）
- [ ] run_eval.py 统一入口
- [ ] README.md 更新

### 下一步
1. 等 ml1m 评估完成，确认 LIR/SEP/ETD/NDCG 数值
2. 重写 `adapters/pgpr_adapter.py` 和 `adapters/vrkg4rec_adapter.py`，改为输出到 `xrecsys/paths/{dataset}/` 目录（xrecsys 的标准格式）
3. 写 `run_eval.py` — 调用 PathDataLoader + metrics，输出汇总 CSV
4. 跑 lastfm 评估

---

## 参考资料

- xrecsys 论文：[Balloccu et al. SIGIR 2022](https://dl.acm.org/doi/10.1145/3477495.3532041)
- xrecsys repo：https://github.com/giacoballoccu/explanation-quality-recsys
- PGPR 原论文：[Xian et al. SIGIR 2019](https://arxiv.org/abs/1906.00091)
- VRKG4Rec 原论文：待补充
