# Quick Start Guide

## 快速开始指南

### 1. 安装环境

```bash
# 安装基础依赖
pip install -r requirements.txt

# 或者运行 setup 脚本
python setup.py
```

### 2. 准备数据

将你的数据集放在 `data/` 目录下：

```
data/
├── ml1m/
│   ├── kg.csv          # 知识图谱 (head, relation, tail)
│   ├── train.csv       # 训练集
│   └── test.csv        # 测试集
└── lastfm/
    └── ...
```

### 3. 转换模型输出

使用适配器将模型输出转换为标准格式：

**VRKG4Rec:**
```bash
python adapters/vrkg4rec_adapter.py \
    --input /path/to/vrkg4rec/output/paths.pkl \
    --dataset ml1m
```

**PGPR:**
```bash
python adapters/pgpr_adapter.py \
    --input /path/to/pgpr/output/ \
    --dataset ml1m
```

转换后会在 `outputs/{model}/{dataset}/` 生成三个 CSV 文件。

### 4. 运行评估

**评估所有模型：**
```bash
python scripts/run_all.py
```

**评估特定模型：**
```bash
python scripts/run_all.py \
    --models vrkg4rec pgpr \
    --datasets ml1m
```

**对比模型：**
```bash
python scripts/compare_models.py \
    --dataset ml1m \
    --models vrkg4rec pgpr cafe
```

### 5. 可视化结果

```bash
# 可视化所有结果
python scripts/visualize.py

# 可视化特定文件
python scripts/visualize.py --input results/ml1m_comparison.csv
```

## 输出示例

### 评估结果 (results/ml1m_comparison.csv)

| model    | LIR↑  | SEP↑  | ETD↑  | validity↑ | diversity↑ |
|----------|-------|-------|-------|-----------|------------|
| VRKG4Rec | 0.88  | 0.48  | 0.18  | 0.90      | 0.75       |
| PGPR     | 0.81  | 0.43  | 0.12  | 0.87      | 0.68       |
| CAFE     | 0.75  | 0.51  | 0.15  | 0.92      | 0.72       |

### 可视化图表 (results/figures/)

- `ml1m_comparison.png` - 条形图对比
- `ml1m_comparison_radar.png` - 雷达图对比

## 自定义适配器

如果要添加新模型，创建一个适配器：

```python
# adapters/mymodel_adapter.py

from adapters.base_adapter import BaseAdapter
import pandas as pd

class MyModelAdapter(BaseAdapter):
    def __init__(self, dataset_name: str):
        super().__init__("mymodel", dataset_name)
    
    def load_model_output(self, model_output_path: str):
        # 加载你的模型输出
        return your_data
    
    def convert_to_standard_format(self, raw_output):
        # 转换为标准格式
        pred_paths = pd.DataFrame([...])
        uid_topk = pd.DataFrame([...])
        uid_pid_explanation = pd.DataFrame([...])
        
        return pred_paths, uid_topk, uid_pid_explanation

# 使用
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--dataset', required=True)
    args = parser.parse_args()
    
    adapter = MyModelAdapter(args.dataset)
    adapter.convert(args.input)
```

## Python API 使用

```python
from evaluation import UnifiedEvaluator

# 创建评估器
evaluator = UnifiedEvaluator(
    dataset_name="ml1m",
    kg_file="data/ml1m/kg.csv"  # 可选
)

# 评估单个模型
metrics = evaluator.evaluate_model("vrkg4rec")
print(metrics)

# 对比多个模型
df = evaluator.compare_models(
    model_names=["vrkg4rec", "pgpr", "cafe"],
    output_file="results/comparison.csv"
)
print(df)
```

## 常见问题

### Q: 如何添加 GNN 指标评估？

A: 安装 PyTorch Geometric 并在评估时提供模型：

```python
metrics = evaluator.evaluate_model(
    model_name="vrkg4rec",
    model=your_pytorch_model,  # 你的模型
    data=your_graph_data       # 图数据
)
```

### Q: 标准输出格式是什么？

A: 三个 CSV 文件：

1. **pred_paths.csv**: 包含 uid, pid, path_score, path_prob, path
2. **uid_topk.csv**: 包含 uid, topk_pids (空格分隔的推荐列表)
3. **uid_pid_explanation.csv**: 包含 uid, pid, explanation

### Q: 如何只评估特定指标？

A: 修改评估器代码或直接调用特定函数：

```python
from evaluation.recsys_metrics import avg_LIR, avg_SEP, avg_ETD
from evaluation.utils import compute_path_validity

paths_data = evaluator.load_model_output("vrkg4rec")

lir = avg_LIR(paths_data)
sep = avg_SEP(paths_data)
etd = avg_ETD(paths_data)
```

## 下一步

1. 查看 `README.md` 了解完整文档
2. 查看 `FRAMEWORK_ROADMAP.md` 了解设计细节
3. 查看 `config/` 目录的配置文件
4. 开始转换和评估你的模型！

---

有问题？请查看 README.md 或提交 Issue。
