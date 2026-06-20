# AGENTS.md — Workspace 管理与路由规则

> 本文件是 Agent 的核心路由手册。所有分析任务通过本文件决定走哪条路径。

---

## Session 启动检查（每次启动必须执行）

Before doing anything else, in this exact order:

1. **Read `SOUL.md`** — this is who I am
2. **Read `IDENTITY.md`** — my role and capability boundary
3. **Read `USER.md`** — this is who I'm helping
4. **Read `TOOLS.md`** — when to use which skill
5. **Read `memory/YYYY-MM-DD.md`** (today + yesterday) for recent context
6. **If in MAIN SESSION**: Also read `MEMORY.md`

Don't ask permission. Just do it.

---

## 策略库状态检查（每次 P1/P2 任务前必做）

```
检查 strategies/index.json
  → 是否有当前标的的历史策略版本？
  → 有 → 加载最新版本 readme.md，读取 v<N> 目录内容
  → 无 → 正常执行新分析
```

**策略版本命名**：`strategies/<ticker>_<strategy_alias>/v<N>/`

---

## 路由决策树

```
用户说什么？
  │
  ├─「扫描」「市场」「看看今天」「P0」
  │   └─→ 走 P0 前哨扫描（genesis-scan）
  │
  ├─「分析 XX」「融合分析」「共振」「深度」
  │   └─→ 走 P1 深度分析（genesis-v22 或 quant-backtest-lab）
  │
  ├─「复盘」「证伪」「事后」「XX 为什么跌了」
  │   └─→ 走 P2 复盘迭代（review-engine）
  │
  ├─「回测 XX」「策略回测」「测试 XX」
  │   └─→ 走 quant-backtest-lab（7步回测流程）
  │
  ├─「选股」「筛选」「哪些股票」
  │   └─→ 走 westock-tool 选股 + 选完若用户要求分析则进 P1
  │
  ├─「事件研究」「持有 X 天收益」
  │   └─→ 走 quant-backtest-lab（事件研究形态）
  │
  └─「组合」「持仓」「仓位」「再平衡」
      └─→ 走 portfolio-manager
```

---

## P0 — 前哨扫描

> **触发**：用户说「扫描」「市场扫描」「看看今天有什么机会」

**执行文件**：`skills/genesis-scan/SKILL.md`

**核心流程**：
```
Step 0: M因子快检（大盘否决权）
Step 1: 指数行情快照
Step 2: 板块热点排行 + 材料短缺扫描（新增）
Step 3: 新闻资讯 + 宏观事件日历
Step 4: 市场情绪（涨停/跌停）
Step 5: 脱水研报热点
→ 输出扫描报告
→ 问：「可以进入深度分析吗？」
```

**材料短缺扫描关键词**（Step 2c）：
```
硅片, 稀土, 锂, 钴, 镍, 铜, 铝, 芯片材料,
光刻胶, 靶材, 电子树脂, HBM, 半导体设备,
碳化硅, 磷化铟, 锗镓, 封装, 先进封装
```

---

## P1 — 深度分析

> **触发**：用户确认进入分析，或说「分析 XX」「融合分析」

**分支判断**：

```
用户是否描述了具体策略？
  ├─ 是（"MA金叉买""布林带回归"）→ quant-backtest-lab（规则回测）
  ├─ 否（"分析一下这只股"）→ genesis-v22（四框架共振分析）
  └─ 是（"持有X天"事件描述）→ quant-backtest-lab（事件研究）
```

**quant-backtest-lab 流程**（规则回测 / 事件研究）：
```
1. 读 pitfalls/pandas.md + common_pitfalls.md（必须）
2. 解析策略 → 结构化形式
3. 写 <prefix>_backtest.py（纯 Python + pandas）
4. 导出三件套（equity.csv / trades.csv / summary.json）
5. 渲染 index.html 仪表盘
6. 自检4步（运行 / pitfalls / sanity / 渲染）
7. 三段式回复 A/B/C
8. 若策略模式可复用 → 保存到 strategies/
```

**genesis-v22 流程**（融合派四框架分析）：
```
1. M因子快检
2. 四个框架并行拉取数据
3. 独立评分（缠论40% / 波浪25% / 板块20% / 事件15%）
4. 宪法约束检查（缠论≤2则综合分≤2.0）
5. 融合评分 + 操作建议
6. 保存到 portfolio/plans/
7. 三段式回复
```

**分析前检查策略库**：
```
strategies/index.json → 有该标的记录？
  → 有 → 加载最新版本 v<N>/readme.md
  → 与当前分析对比，说明「相比 v<N> 的变化」
  → 无 → 正常分析
```

---

## P2 — 复盘迭代

> **触发**：用户说「复盘」「证伪」或每次交付后自动执行

**执行文件**：`skills/review-engine/SKILL.md`

**核心流程**：
```
1. 调取 portfolio/plans/ 中的历史分析报告
2. 拉取实际走势数据（对比当时的预测 vs 现实）
3. 四维度归因（技术面 / 基本面 / 资金面 / 情绪面）
4. 提炼规则 → 创建 v<N+1>/ 策略版本
5. 更新 memory/YYYY-MM-DD.md 和 MEMORY.md
6. 问用户是否采纳新规则
```

---

## 策略版本管理

```
strategies/
├── index.json                    ← 策略总索引（每次保存必须更新）
├── <ticker>_<alias>/
│   ├── v1/
│   │   ├── readme.md           ← 策略说明 + self_refutation
│   │   ├── <prefix>_equity.csv
│   │   ├── <prefix>_trades.csv
│   │   └── <prefix>_summary.json
│   └── v2/
│       ├── readme.md
│       ├── changelog.md         ← 改了什么、为什么改、效果
│       └── ...
```

**index.json 格式**：
```json
{
  "strategies": [
    {
      "id": "sz688126_silicon_v1",
      "ticker": "sh688126",
      "name": "沪硅产业四框架分析",
      "version": "v1",
      "created": "2026-06-20",
      "score": 3.7,
      "outcome": "pending",
      "path": "sh688126_silicon_v1/v1/"
    }
  ]
}
```

---

## Memory 管理规则

### 每日日志（memory/YYYY-MM-DD.md）

每次完成分析/回测后写入：
- 用户策略描述 + 澄清问题 + 最终选择
- 实际调用的 skill 和数据范围
- 自检中发现的 bug + 修复方式
- 交付物关键指标（总收益 / Sharpe / 最大回撤 / 交易次数）

### 长期记忆（MEMORY.md）

仅在主会话（direct chat）中加载。蒸馏原则：
- 用户偏好（语言 / 详细度 / 默认参数）
- 反复踩过的坑（具体 bug + 修复方式）
- 数据源限制（westock-data / westock-tool 已知限制）
- 策略积累（成功/失败的策略模式）

**写作原则**：Text > Brain。"Mental notes" 不存在，只有文件里的东西才算数。

---

## Red Lines

- Don't exfiltrate private data. Ever.
- Don't run destructive commands without asking.
- `trash` > `rm`（可恢复 > 永久删除）
- 实盘下单代码：不写
- 把回测结果分享到外部平台：不主动做

---

## 外部 vs 内部

**可以自由执行**：
- 读文件、跑取数 CLI、写脚本、跑回测、生成 HTML/PNG
- workspace 内 / cwd 内做任何操作
- 调用当前 `<available_skills>` 列表中的 skill

**必须先问**：
- 写实盘下单代码
- 把回测结果分享到外部平台 / 公开渠道
- 任何带"自动执行真实交易"语义的操作

---

## Skill 可用性原则（最高优先级）

OpenClaw 允许用户关闭任何技能。关闭后该 skill 不出现在 `<available_skills>` 列表中。

**调用前必须检查**：不在列表 = 已关闭，按 TOOLS.md 降级方案处理。

**不得硬依赖**：文件里提及的 skill 名称是理想配置，不是强制存在。

---

## Make It Yours

This is a starting point. Add your own conventions as you figure out what works.
