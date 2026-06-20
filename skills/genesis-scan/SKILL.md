# genesis-scan — P0 前哨扫描入口

> **版本**：V24.1 对齐版
> **触发**：用户说「扫描」「市场扫描」「看看今天有什么机会」「看看市场」
> **Skill 可用性**：`westock-data`（必须）| `westock-tool`（必须）| `online-search`（降级用）
> **对齐**：与 `skills/genesis-v22/` (V24.1) 无缝衔接，P0 扫描结果自动作为 P1 的情报输入

---

## 执行流程

```
触发 P0
  → Step 0: M因子快检（大盘否决权，唯一必做）
  → Step 1: 指数行情快照
  → Step 2: 板块热点排行 + 材料短缺扫描 🆕
  → Step 3: 新闻资讯 + 宏观事件日历
  → Step 4: 市场情绪（涨停/跌停/涨跌家数）
  → Step 5: 脱水研报热点
  → Step 6: 输出扫描报告 + 问用户「需要深度分析哪个？」
```

---

## Step 0：M因子快检（必须，立即执行）

```bash
node skills/westock-data/scripts/index.js kline sh000300 --period day --limit 60
```

| M评分 | 大盘状态 | 仓位上限 |
|-------|----------|----------|
| 8-10 | 强势 | 100% |
| 6-7 | 偏强 | 80% |
| 4-5 | 中性 | 60% |
| 2-3 | 偏弱 | **30%** ⚠️ |
| 0-1 | 弱势 | **10%** 🔴 |

**M < 4 时报告顶部必须标注**：⚠️ 大盘偏弱，仓位上限 30%，以观察为主。

---

## Step 1：指数行情快照

```bash
node skills/westock-data/scripts/index.js quote sh000001 sz399001 sz399006 sh000688
```

读取：上证 / 深证 / 创业板 / 科创50 的涨跌幅、成交量。

---

## Step 2：板块热点排行 + 材料短缺扫描

### 2a：申万一级行业排行
```bash
node skills/westock-data/scripts/index.js sector --rank interval_chg_rank_sw1 --sort chg5Days --limit 30
```

### 2b：聚源概念排行（取前50，筛材料类）
```bash
node skills/westock-data/scripts/index.js sector --rank interval_chg_rank_industry --sort chg5Days --limit 50
```

### 2c：材料短缺关键词扫描（新增核心逻辑）

从上一步 50 个概念板块结果中，**按关键词过滤**：

```
材料短缺热点关键词：
硅片, 稀土, 锂, 钴, 镍, 铜, 铝, 芯片材料,
光刻胶, 靶材, 电子树脂, 电子布, HBM,
半导体设备, 大硅片, 碳化硅, 磷化铟, 锗镓,
封装, 先进封装, 硅锰, 锆, 铋, 锡
```

**判断规则**：

| 材料板块5日涨幅 | 信号等级 | 标注 |
|---------------|---------|------|
| > 15% | 🔴 热点过热的材料 | 短期可能回调，等回调再入 |
| 8% ~ 15% + 有供给侧催化 | 🟡 重点关注材料短缺 | 纳入观察池 |
| 5% ~ 8% | 🟢 一般材料信号 | 纳入监控 |
| < 5% | ⚪ 暂无材料短缺信号 | 跳过 |

**供给侧催化来源**：westock-data `marketnews hs` + `calendar` 中关键词匹配：
- 限售 / 禁运 / 制裁 / 涨价 / 扩产 / 停产

### 2d：若发现材料短缺热点，进一步拉板块内代表标的行情
```bash
# 大硅片
node skills/westock-data/scripts/index.js sector pt02GN2441
# 半导体材料
node skills/westock-data/scripts/index.js sector pt02GN2323
# 具体标的价格快照
node skills/westock-data/scripts/index.js quote sh688126 sh688432 sh688783
```

---

## Step 3：新闻资讯 + 宏观事件日历

### 3a：沪深市场资讯
```bash
node skills/westock-data/scripts/index.js marketnews hs
```

### 3b：宏观事件日历（未来1周）
```bash
node skills/westock-data/scripts/index.js calendar --limit 10 --country 1 --indicator 2
```

关键词标注：降准 / 降息 / 美联储 / 加征关税 / 制裁 / 行业政策

---

## Step 4：市场情绪

### 4a：涨停 / 跌停 统计
```bash
node skills/westock-tool/scripts/index.js strategy daily_limit_up --limit 5
```

### 4b：热门板块
```bash
node skills/westock-data/scripts/index.js hot board --limit 10
```

---

## Step 5：脱水研报热点（降级：若 westock-data dehydrated 不可用则跳过）

```bash
node skills/westock-data/scripts/index.js dehydrated --limit 10
```

---

## 输出模板

```
【P0 扫描报告】YYYY-MM-DD

## 〇、M因子：X/10 | 仓位上限 XX% ⚠️[M<4时必须标注]

## 一、指数快照
[上证/深证/创业板/科创50 涨跌]

## 二、板块热点 + 材料短缺 🆕
### 热点板块 TOP5
| 排名 | 板块 | 5日涨幅 | 评分 |
|------|------|---------|------|

### 材料短缺扫描 🆕
| 材料类别 | 板块 | 5日涨幅 | 信号等级 | 供需催化 |
|---------|------|---------|---------|---------|
| [硅片/稀土等] | [板块名] | +X% | 🟡/🟢/🔴 | [有/无] |

## 三、新闻 + 宏观日历
[重要事件摘要]

## 四、市场情绪
[涨停/跌停/涨跌家数]

## 五、脱水研报热点
[机构关注方向]

## 六、观察池
[综合优先级排序，材料短缺热点若评分够高则纳入首位]

「可以进入深度分析吗？」
```

---

## 数据时效性声明（每次扫描必须包含）

```
数据获取时间：
- 指数行情：YYYY-MM-DD HH:MM（westock-data quote）
- 板块排行：YYYY-MM-DD HH:MM（westock-data sector --rank）
- 市场情绪：YYYY-MM-DD HH:MM（westock-tool strategy）
- 宏观日历：YYYY-MM-DD HH:MM（westock-data calendar）
```

---

## Self-Refutation（必须包含）

1. **材料短缺识别是否可能滞后？**
   → 板块涨幅反映的是过去5日，材料短缺新闻可能已提前定价。需对比 `marketnews` 中是否有相关报道。
2. **板块排行是否有幸存者偏差？**
   → 取前50名时只看了涨幅最大的，需注意跌幅大的板块也可能是重要信号。
3. **M因子判断是否准确？**
   → 仅看MA50方向，可能遗漏盘中剧烈波动。标注仅作参考。

---

## Skill 降级处理

| Skill 不可用 | 降级方案 |
|-------------|---------|
| `westock-data` | 无法执行 → 告知用户，无法完成扫描 |
| `westock-tool` | 用 `westock-data hot board` 替代涨停统计 |
| `dehydrated` | 跳过 Step 5，标注「研报数据不可用」 |
| `online-search` | 用 `marketnews hs` 替代新闻搜索 |

---

## 版本记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-06-20 | 基础版（指数+板块+新闻+涨停） |
| v2.0 | 2026-06-20 | 新增 Step 0 M因子快检 + Step 5 脱水研报 |
| v3.0 | 2026-06-20 | 新增 Step 2c 材料短缺扫描（核心新增） |
