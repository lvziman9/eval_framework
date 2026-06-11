# xrecsys 路径格式与三大指标说明

本文件用于指导未来模型（如 PGPR、VRKG4Rec、CAFE 等）接入 xrecsys 评估框架。

---

## 一、路径字符串格式

xrecsys 的所有指标（LIR、SEP、ETD）均基于**路径字符串**计算。路径以空格分隔的三元组序列表示：

```
rel_0 etype_0 eid_0  rel_1 etype_1 eid_1  rel_2 etype_2 eid_2  rel_3 etype_3 eid_3
```

每三个 token 构成一个节点三元组 `(relation, entity_type, entity_id)`，由 `normalize_path()` 解析为列表：

```python
# myutils.py – normalize_path()
path = path_str.split(" ")
normalized_path = [(path[i], path[i+1], path[i+2]) for i in range(0, len(path), 3)]
```

### lastfm 标准路径（长度 4 个节点 = 12 个 token）

```
self_loop  user  {uid}  listened  song  {seed_song_id}  {relation}  {etype}  {bridge_eid}  {relation}  song  {pid}
```

| 位置       | 三元组                              | 含义                          |
|-----------|-------------------------------------|-----------------------------|
| `path[0]` | `(self_loop, user, uid)`            | 起始用户                      |
| `path[1]` | `(listened, song, seed_song_id)`    | 用户训练集中听过的歌（LIR锚点）  |
| `path[2]` | `(relation, etype, bridge_eid)`     | KG 桥接实体（SEP锚点）          |
| `path[3]` | `(relation, song, pid)`             | 推荐目标歌曲（ETD锚点）         |

### lastfm 9 种合法关系（ETD 分母 = 9）

| relation 名称              | bridge entity type | 含义          |
|---------------------------|--------------------|--------------|
| `belong_to`               | `category`         | 曲风归属      |
| `related_to`              | `related_song`     | 关联曲目      |
| `sang_by`                 | `artist`           | 演唱者        |
| `mixed_by`                | `engineer`         | 混音工程师    |
| `produced_by_producer`    | `producer`         | 制作人        |
| `original_version_of`     | `related_song`     | 原版本        |
| `alternative_version_of`  | `related_song`     | 变奏版本      |
| `featured_by`             | `artist`           | 特邀艺术家    |
| `listened`                | `user`             | 协同过滤路径  |

---

## 二、LIR（Linked Interaction Recency）

**衡量推荐路径"锚点交互"的时间近期性。**

路径中 `path[1]` 是用户在训练集中真实听过的"共同歌曲"（seed song），通过该歌曲 ID 查找用户的交互时间戳，再按 EMA 归一化到 [0,1]。越接近 1 说明该推荐来自用户最近的兴趣。

```python
# metrics.py
seed_song_id = int(path[1][-1])                          # path[1] = (listened, song, seed_id)
timestamp = uid_pid_timestamp[uid][seed_song_id]         # 从 train.txt 读取
LIR = LIR_matrix[uid][timestamp]                         # EMA 归一化后的时间权重
```

**数据依赖：**
- `datasets/lastfm/train.txt` → 格式：`uid  item_id  timestamp`（空格分隔三列）
- `models/PGPR/tmp/lastfm/train_label.pkl`

**⚠ 注意：**
- 若模型路径中的 `path[1]` 对应的歌曲不在用户训练集里，LIR 计为 0。
- `datasets/lastfm/train.txt` 中 uid 和 item_id 必须是 xrecsys 内部整数 ID，与 `train_label.pkl` 中的 key 一致。
- LIR 对单交互用户自动跳过（`len(uid_timestamp[uid]) <= 1`）。

---

## 三、SEP（Serendipity of Explanation Path）

**衡量桥接实体的"冷门程度"（低度节点 = 更有惊喜性）。**

`path[-2]`（倒数第二节点）是桥接实体，SEP 取该实体在 KG 中的入度，按全局归一后再 EMA 变换，度越低则 SEP 越高。

```python
# metrics.py
bridge_etype, bridge_eid = path[-2][1], int(path[-2][2])   # 倒数第二节点
SEP = SEP_matrix[bridge_etype][bridge_eid]                  # 预计算的归一化入度权重
```

**数据依赖：**
- `models/PGPR/tmp/{dataset}/kg.pkl` → `KnowledgeGraph.degrees` 字典
  - 格式：`{entity_type: {entity_id: in_degree}}`

---

## 四、ETD（Explanation Type Diversity）

**衡量一个用户的 Top-K 推荐中，路径类型的多样性。**

`path[-1][0]`（最后节点的 relation）就是路径类型。ETD = 该用户 Top-K 中不重复路径类型数 / 全部合法路径类型数。

```python
# metrics.py
path_type = path[-1][0]                      # 最后三元组的 relation 名称，如 'sang_by'
unique_types = set(path_type for each pid)
ETD = len(unique_types) / TOTAL_PATH_TYPES[dataset]   # lastfm: 分母=9
```

**数据依赖：**
- `uid_pid_explanation.csv` 中每个 pid 对应一条路径
- `myutils.py::SELECTED_RELATIONS` / `TOTAL_PATH_TYPES`

---

## 五、接入新模型的 Checklist

新模型要输出 xrecsys 兼容的三个 CSV 文件，存放路径为：

```
xrecsys/paths/{dataset}/agent_topk={tag}/
    pred_paths.csv           # uid, pid, path_score, path_prob, path
    uid_topk.csv             # uid, top10  (空格分隔的 pid 列表)
    uid_pid_explanation.csv  # uid, pid, path
```

路径字符串必须满足：
1. **格式**：`rel etype eid` 三元组，空格分隔，每段恰好 3 个 token
2. **长度**：lastfm 标准为 12 个 token（4 个三元组）
3. **起点**：`(self_loop, user, uid)`
4. **终点**：`(relation, song, pid)` 其中 relation 是合法的 9 种之一
5. **LIR 要求**：`path[1]` 必须是该用户训练集中真实交互过的歌曲
6. **SEP 要求**：`path[-2]` 的 etype 和 eid 必须存在于 xrecsys KG 的 entities 文件中（匹配 xrecsys 的 0-indexed entity ID）
7. **uid/pid**：使用 xrecsys 的内部整数 ID（从 `train_label.pkl` / `test_label.pkl` 中取）

### 各指标对路径要求总结

| 指标 | 依赖路径位置 | 依赖外部数据 | 无法满足时 |
|------|------------|------------|----------|
| NDCG/HR | `uid_topk.csv` 中的 pid 排序 | `test_label.pkl` | — |
| LIR | `path[1][-1]` = seed song ID | `train.txt` 时间戳 | 计为 0 |
| SEP | `path[-2]` = bridge entity | `kg.pkl` degrees | 计为 0 |
| ETD | `path[-1][0]` = last relation | `TOTAL_PATH_TYPES` | 计为 0 |

---

## 六、ml1m 路径格式

### 标准路径（12 个 token = 4 个三元组）

```
self_loop  user  {uid}  watched  movie  {seed_movie_id}  {relation}  {etype}  {bridge_eid}  {relation}  movie  {pid}
```

| 位置       | 三元组                                  | 含义                          |
|-----------|-----------------------------------------|-----------------------------|
| `path[0]` | `(self_loop, user, uid)`                | 起始用户                      |
| `path[1]` | `(watched, movie, seed_movie_id)`       | 用户训练集中看过的电影（LIR锚点）|
| `path[2]` | `(relation, etype, bridge_eid)`         | KG 桥接实体（SEP锚点）          |
| `path[3]` | `(relation, movie, pid)`                | 推荐目标电影（ETD锚点）         |

### ml1m 10 种合法关系（ETD 分母 = 10）

| relation_id | relation 名称        | bridge entity type   | 含义          |
|------------|---------------------|----------------------|--------------|
| 0          | `cinematography`    | `cinematographer`    | 摄影师        |
| 1          | `produced_by_company` | `production_company` | 制作公司    |
| 2          | `composed_by`       | `composer`           | 作曲家        |
| 3          | `belong_to`         | `category`           | 类型归属      |
| 8          | `belong_to`         | `category`           | 类型归属（同3）|
| 10         | `starring`          | `actor`              | 主演演员      |
| 14         | `edited_by`         | `editor`             | 剪辑师        |
| 15         | `produced_by_producer` | `producer`        | 制片人        |
| 16         | `wrote_by`          | `writter`            | 编剧          |
| 18         | `directed_by`       | `director`           | 导演          |

> 注：`SELECTED_RELATIONS[ML1M] = [0,1,2,3,8,10,14,15,16,18]`，共 10 种，但 3 和 8 均为 `belong_to`（均指向 `category`），实际路径类型为 9 种唯一关系。`relation_id=20`（协同过滤 `watched→user→watched`）存在于 `ML1M_PATH_PATTERN` 但不在 `SELECTED_RELATIONS` 中，ETD 计算不包含它。

### ml1m 实体类型列表

```
user, movie, actor, director, producer, production_company, category, editor, writter, cinematographer, composer
```

### 数据文件位置

```
datasets/ml1m/
    train.txt                      # uid  movie_id  timestamp（三列，制表符分隔）
    test.txt
    entities/movie.txt, actor.txt, ...
    relations/starring_m_a.txt, directed_by_m_d.txt, ...
    mappings/uid2gender.txt, uid2age_map.txt, uid2occupation.txt
models/PGPR/tmp/ml1m/
    train_label.pkl                # {uid: [movie_id, ...]}
    test_label.pkl
    kg.pkl                         # KnowledgeGraph，含 .degrees
    transe_embed.pkl
```

### ml1m 指标数据依赖

| 指标 | 依赖 `path` 位置 | 依赖外部文件 |
|------|----------------|------------|
| NDCG/HR | `uid_topk.csv` pid 排序 | `test_label.pkl` |
| LIR | `path[1][-1]` = seed movie ID | `datasets/ml1m/train.txt` 时间戳 |
| SEP | `path[-2]` = (relation, etype, bridge_eid) | `kg.pkl` `.degrees[etype][eid]` |
| ETD | `path[-1][0]` = last relation 名称 | `TOTAL_PATH_TYPES[ml1m]` = 10 |

### ml1m 路径字符串示例

```
# 通过导演推荐：用户看了《黑客帝国》→ 导演沃卓斯基 → 《云图》
self_loop user 42  watched movie 1234  directed_by director 56  directed_by movie 789

# 通过演员推荐：
self_loop user 42  watched movie 1234  starring actor 101  starring movie 456

# 协同过滤路径（不计入 ETD）：
self_loop user 42  watched movie 1234  watched user 99  watched movie 789
```
