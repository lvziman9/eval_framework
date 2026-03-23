# Explainability Benchmark Framework - Roadmap

## 🎯 目标
统一评估 PGPR、CAFE、KGIN、VRKG4Rec、RippleNet 等模型的可解释性

---

## 📁 项目结构

```
explainability-benchmark/
├── data/                           # 共享数据集
│   ├── ml1m/
│   └── lastfm/
│
├── models/                         # 各模型代码 (git submodule)
│   ├── pgpr/
│   ├── cafe/
│   ├── kgin/
│   ├── vrkg4rec/
│   └── ripplenet/
│
├── adapters/                       # 输出格式转换器
│   ├── __init__.py
│   ├── base_adapter.py
│   ├── vrkg4rec_adapter.py
│   ├── pgpr_adapter.py
│   └── ...
│
├── outputs/                        # 标准格式输出
│   ├── vrkg4rec/
│   │   ├── ml1m/
│   │   │   ├── pred_paths.csv
│   │   │   ├── uid_topk.csv
│   │   │   └── uid_pid_explanation.csv
│   │   └── lastfm/
│   ├── pgpr/
│   └── ...
│
├── evaluation/                     # 评估框架
│   ├── __init__.py
│   ├── pyg_metrics.py             # PyG标准指标
│   ├── recsys_metrics.py          # 推荐系统指标 (LIR, SEP, ETD)
│   ├── unified_evaluator.py       # 统一评估接口
│   └── utils.py
│
├── scripts/                        # 运行脚本
│   ├── run_all.py                 # 一键评估所有模型
│   ├── compare_models.py          # 模型对比
│   └── visualize.py               # 结果可视化
│
├── results/                        # 评估结果
│   ├── ml1m_comparison.csv
│   ├── lastfm_comparison.csv
│   └── figures/
│
├── config/
│   ├── datasets.yaml
│   └── models.yaml
│
├── requirements.txt
└── README.md
```

---

## 🔧 核心组件

### 1. 标准输出格式

所有模型必须输出3个CSV文件：

#### pred_paths.csv
```csv
uid,pid,path_score,path_prob,path
4942,998,0.6243,1.6027,user 4942 watched movie 328 produced_by producer 197 produced_by movie 998
```

#### uid_topk.csv
```csv
uid,topk_pids
1,946 518 513 309 742 93 31 944 274 417
```

#### uid_pid_explanation.csv
```csv
uid,pid,explanation
1,946,user 1 watched movie 2289 watched user 266 watched movie 946
```

---

### 2. Adapter基类

```python
# adapters/base_adapter.py

from abc import ABC, abstractmethod
import pandas as pd
from pathlib import Path

class BaseAdapter(ABC):
    """所有模型适配器的基类"""
    
    def __init__(self, model_name, dataset_name):
        self.model_name = model_name
        self.dataset_name = dataset_name
        self.output_dir = Path(f"outputs/{model_name}/{dataset_name}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def load_model_output(self, model_output_path):
        """加载模型原始输出"""
        pass
    
    @abstractmethod
    def convert_to_standard_format(self, raw_output):
        """转换为标准格式"""
        pass
    
    def save_standard_output(self, pred_paths, uid_topk, uid_pid_explanation):
        """保存标准格式"""
        pred_paths.to_csv(self.output_dir / "pred_paths.csv", index=False)
        uid_topk.to_csv(self.output_dir / "uid_topk.csv", index=False)
        uid_pid_explanation.to_csv(self.output_dir / "uid_pid_explanation.csv", index=False)
    
    def convert(self, model_output_path):
        """完整转换流程"""
        print(f"Converting {self.model_name} output...")
        raw_output = self.load_model_output(model_output_path)
        pred_paths, uid_topk, uid_pid_explanation = self.convert_to_standard_format(raw_output)
        self.save_standard_output(pred_paths, uid_topk, uid_pid_explanation)
        print(f"✓ Saved to {self.output_dir}")
```

---

### 3. 统一评估器

```python
# evaluation/unified_evaluator.py

import pandas as pd
from torch_geometric.explain import Explainer, GNNExplainer
from torch_geometric.explain.metric import fidelity, unfaithfulness
from .recsys_metrics import avg_LIR, avg_SEP, avg_ETD

class UnifiedEvaluator:
    """统一评估接口"""
    
    def __init__(self, dataset_name):
        self.dataset_name = dataset_name
    
    def load_standard_output(self, model_name):
        """加载标准格式数据"""
        base_path = f"outputs/{model_name}/{self.dataset_name}"
        return {
            'pred_paths': pd.read_csv(f"{base_path}/pred_paths.csv"),
            'uid_topk': pd.read_csv(f"{base_path}/uid_topk.csv"),
            'uid_pid_explanation': pd.read_csv(f"{base_path}/uid_pid_explanation.csv")
        }
    
    def evaluate_gnn_metrics(self, model, data):
        """评估GNN标准指标 (PyG)"""
        explainer = Explainer(
            model=model,
            algorithm=GNNExplainer(epochs=200),
            explanation_type='model',
            node_mask_type='object',
            edge_mask_type='object',
        )
        
        explanation = explainer(data.x, data.edge_index)
        fid_pos, fid_neg = fidelity(explainer, explanation)
        unfaith = unfaithfulness(explainer, explanation)
        
        return {
            'fidelity_pos': fid_pos.item(),
            'fidelity_neg': fid_neg.item(),
            'unfaithfulness': unfaith.item()
        }
    
    def evaluate_recsys_metrics(self, paths_data):
        """评估推荐系统指标"""
        return {
            'LIR': avg_LIR(paths_data)['Overall'],
            'SEP': avg_SEP(paths_data)['Overall'],
            'ETD': avg_ETD(paths_data)['Overall']
        }
    
    def evaluate_validity(self, paths_data, kg_graph):
        """评估路径有效性"""
        # 你的现有实现
        pass
    
    def evaluate_model(self, model_name, model=None, data=None):
        """全面评估一个模型"""
        print(f"\n{'='*60}")
        print(f"评估模型: {model_name}")
        print(f"{'='*60}")
        
        # 加载标准格式数据
        paths_data = self.load_standard_output(model_name)
        
        metrics = {'model': model_name}
        
        # 1. GNN标准指标 (如果提供了模型)
        if model is not None and data is not None:
            print("计算GNN标准指标...")
            gnn_metrics = self.evaluate_gnn_metrics(model, data)
            metrics.update(gnn_metrics)
        
        # 2. 推荐系统指标
        print("计算推荐系统指标...")
        recsys_metrics = self.evaluate_recsys_metrics(paths_data)
        metrics.update(recsys_metrics)
        
        # 3. 路径有效性
        print("计算Path Validity...")
        validity = self.evaluate_validity(paths_data, None)
        metrics['validity'] = validity
        
        print(f"✓ {model_name} 评估完成")
        return metrics
```

---

## 🚀 实施步骤

### Phase 1: 基础设施 (Day 1, 2-3小时)

1. **创建项目结构**
```bash
mkdir explainability-benchmark
cd explainability-benchmark
mkdir -p data models adapters outputs evaluation scripts results config
```

2. **安装依赖**
```bash
# requirements.txt
torch>=1.10.0
torch-geometric>=2.0.0
pandas>=1.3.0
numpy>=1.21.0
pyyaml>=5.4.0
matplotlib>=3.5.0
seaborn>=0.11.0
easydict>=1.9
```

3. **复制评估框架**
```bash
# 复制推荐系统metrics
git clone https://github.com/giacoballoccu/explanation-quality-recsys.git
cp explanation-quality-recsys/metrics.py evaluation/recsys_metrics.py
cp explanation-quality-recsys/myutils.py evaluation/
```

### Phase 2: 实现Adapters (Day 2-3, 每个2小时)

**优先级排序：**
1. ✅ VRKG4Rec (你最熟悉)
2. ✅ PGPR (有现成路径输出)
3. ⭐ CAFE 
4. ⭐ KGIN
5. ⭐ RippleNet

**VRKG4Rec Adapter示例：**
```python
# adapters/vrkg4rec_adapter.py

from .base_adapter import BaseAdapter
import pickle
import pandas as pd

class VRKG4RecAdapter(BaseAdapter):
    
    def load_model_output(self, model_output_path):
        """加载VRKG4Rec输出"""
        with open(f"{model_output_path}/paths.pkl", 'rb') as f:
            return pickle.load(f)
    
    def convert_to_standard_format(self, raw_output):
        """转换为标准格式"""
        pred_paths_list = []
        uid_topk_dict = {}
        uid_pid_explanation_dict = {}
        
        for uid, user_paths in raw_output.items():
            topk_items = []
            
            for item_id, paths in user_paths.items():
                topk_items.append(item_id)
                
                # 取最佳路径
                if len(paths) > 0:
                    best_path = paths[0]  # 假设已排序
                    path_str = ' '.join([str(node) for node in best_path[0]])
                    
                    pred_paths_list.append({
                        'uid': uid,
                        'pid': item_id,
                        'path_score': best_path[1],
                        'path_prob': -1,  # VRKG4Rec没有概率
                        'path': path_str
                    })
                    
                    uid_pid_explanation_dict[(uid, item_id)] = path_str
            
            uid_topk_dict[uid] = ' '.join(map(str, topk_items[:10]))
        
        # 转换为DataFrame
        pred_paths = pd.DataFrame(pred_paths_list)
        
        uid_topk = pd.DataFrame([
            {'uid': uid, 'topk_pids': pids} 
            for uid, pids in uid_topk_dict.items()
        ])
        
        uid_pid_explanation = pd.DataFrame([
            {'uid': uid, 'pid': pid, 'explanation': exp}
            for (uid, pid), exp in uid_pid_explanation_dict.items()
        ])
        
        return pred_paths, uid_topk, uid_pid_explanation
```

### Phase 3: 批量评估 (Day 4, 2小时)

```python
# scripts/run_all.py

from evaluation.unified_evaluator import UnifiedEvaluator
import pandas as pd

MODELS = ['pgpr', 'cafe', 'kgin', 'vrkg4rec', 'ripplenet']
DATASETS = ['ml1m', 'lastfm']

def run_benchmark():
    all_results = []
    
    for dataset in DATASETS:
        print(f"\n{'='*70}")
        print(f"数据集: {dataset}")
        print(f"{'='*70}")
        
        evaluator = UnifiedEvaluator(dataset)
        
        for model_name in MODELS:
            try:
                metrics = evaluator.evaluate_model(model_name)
                metrics['dataset'] = dataset
                all_results.append(metrics)
            except Exception as e:
                print(f"✗ {model_name} 评估失败: {e}")
    
    # 保存结果
    df = pd.DataFrame(all_results)
    
    for dataset in DATASETS:
        dataset_df = df[df['dataset'] == dataset]
        dataset_df.to_csv(f"results/{dataset}_comparison.csv", index=False)
        print(f"\n{'='*70}")
        print(f"{dataset.upper()} Results:")
        print(f"{'='*70}")
        print(dataset_df.to_string(index=False))
    
    return df

if __name__ == '__main__':
    results = run_benchmark()
    print("\n✓ Benchmark完成！")
```

### Phase 4: 可视化 (Day 5, 2小时)

```python
# scripts/visualize.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_comparison(csv_path, output_path):
    df = pd.read_csv(csv_path)
    
    metrics = ['LIR', 'SEP', 'ETD', 'validity', 'fidelity_pos']
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    for idx, metric in enumerate(metrics):
        if metric in df.columns:
            ax = axes[idx]
            df.plot(x='model', y=metric, kind='bar', ax=ax, legend=False)
            ax.set_title(f'{metric}')
            ax.set_xlabel('')
            ax.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ 保存可视化: {output_path}")

if __name__ == '__main__':
    for dataset in ['ml1m', 'lastfm']:
        plot_comparison(
            f'results/{dataset}_comparison.csv',
            f'results/figures/{dataset}_comparison.png'
        )
```

---

## 📊 核心指标

### PyG标准指标 (GNN通用)
- **Fidelity+**: 移除重要边后准确度下降
- **Fidelity-**: 保留重要边后准确度
- **Unfaithfulness**: 解释偏离度

### 推荐系统指标 (SIGIR 2022)
- **LIR** (Link Interaction Recency): 交互新鲜度 ↑
- **SEP** (Shared Entity Popularity): 实体惊喜度 ↑
- **ETD** (Explanation Type Diversity): 路径多样性 ↑

### 知识图谱指标
- **Path Validity**: 路径在KG中存在性 ↑

---

## 🎯 预期输出

```
=== ML1M Comparison ===
Model       Fidelity+ Fidelity- LIR↑  SEP↑  ETD↑  Validity↑
PGPR        0.245     0.678     0.81  0.43  0.12  0.87
CAFE        0.289     0.712     0.75  0.51  0.15  0.92
KGIN        0.198     0.645     0.70  0.38  0.10  0.85
VRKG4Rec    0.267     0.695     0.88  0.48  0.18  0.90  ⭐
RippleNet   0.176     0.623     0.65  0.41  0.13  0.83

Best:
- Recency: VRKG4Rec
- Diversity: VRKG4Rec
- Validity: CAFE
- Overall: VRKG4Rec
```

---

## ⚡ 快速开始

```bash
# 1. 克隆/创建项目
git clone <your-repo> explainability-benchmark
cd explainability-benchmark

# 2. 安装依赖
pip install -r requirements.txt

# 3. 添加模型 (git submodule)
git submodule add <vrkg4rec-repo> models/vrkg4rec
git submodule add https://github.com/orcax/PGPR.git models/pgpr

# 4. 转换模型输出
python adapters/vrkg4rec_adapter.py --input path/to/vrkg_output --dataset ml1m

# 5. 运行评估
python scripts/run_all.py

# 6. 可视化
python scripts/visualize.py
```

---

## 📚 论文引用

```latex
\subsection{Evaluation Framework}
We develop a unified benchmark to systematically evaluate 
explanation quality across multiple models using:

\textbf{GNN Standard Metrics:}
Fidelity \cite{graphframex} via PyTorch Geometric

\textbf{Recommendation Metrics:}
LIR, SEP, ETD \cite{balloccu2022post}

\textbf{KG Metrics:}
Path Validity in knowledge graph
```

```bibtex
@article{abrate2022graphframex,
  title={GraphFramEx: Towards systematic evaluation of explainability methods for graph neural networks},
  author={Abrate, Carlo and Bonchi, Francesco},
  journal={arXiv:2206.09677},
  year={2022}
}

@inproceedings{balloccu2022post,
  title={Post processing recommender systems with knowledge graphs for recency, popularity, and diversity of explanations},
  author={Balloccu, Giacomo and Boratto, Ludovico and Fenu, Gianni and Marras, Mirko},
  booktitle={SIGIR},
  pages={646--656},
  year={2022}
}
```

---

## ✅ Checklist

### Week 1
- [ ] 创建项目结构
- [ ] 安装依赖 (PyG, pandas等)
- [ ] 实现BaseAdapter
- [ ] 实现VRKG4RecAdapter
- [ ] 测试VRKG4Rec转换

### Week 2
- [ ] 实现PGPRAdapter
- [ ] 实现其他adapters
- [ ] 复制recsys_metrics.py
- [ ] 实现UnifiedEvaluator
- [ ] 测试单个模型评估

### Week 3
- [ ] 实现批量评估脚本
- [ ] 运行完整benchmark
- [ ] 实现可视化
- [ ] 生成对比表格
- [ ] 撰写README

---

## 💡 关键提示

1. **先做VRKG4Rec**: 你最熟悉，作为template
2. **PGPR有现成输出**: 优先级第二
3. **标准格式很重要**: 所有模型必须统一
4. **分阶段测试**: 每个adapter独立测试
5. **保存中间结果**: 避免重复计算

---

## 🔗 相关资源

- PyG Explainability: https://pytorch-geometric.readthedocs.io/en/latest/modules/explain.html
- explanation-quality-recsys: https://github.com/giacoballoccu/explanation-quality-recsys
- PGPR: https://github.com/orcax/PGPR
- DIG (可选): https://github.com/divelab/DIG

---

## 📞 下一步

1. 在新窗口创建项目
2. 从VRKG4RecAdapter开始
3. 测试转换→评估流程
4. 逐步添加其他模型
5. 运行完整benchmark

**预计总工作量**: 1-2周
**论文价值**: 可发独立benchmark论文！
