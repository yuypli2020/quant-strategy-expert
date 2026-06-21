# AGENTS.md — Workspace 管理与路由规则

> 本文件是 Agent 的核心路由手册。所有分析任务通过本文件决定走哪条路径。
> **V26 新增**：Genesis SOP 七阶段完整流程 + 扫描归档机制 + 每日复盘闭环

---

## Session 启动检查（每次启动必须执行）

Before doing anything else, in this exact order:

1. **Read `SOUL.md`** — this is who I am (V26.2: 八学派+票代原则+信息层级)
2. **Read `CONFIDENCE.md`** — 🆕 认知诚实框架：信息四层级+盲区检查清单
3. **Read `TOOLS.md`** — when to use which skill
4. **Read `MEMORY.md`** — long-term memory
5. **Read `skills/genesis-v22/SKILL.md`** — V26.2 多情景裁决 + 八学派辩论 + 信息层级声明
6. **Read `skills/constitution-layer/SKILL.md`** — **宪法十二条**（含共识≠Alpha）
7. **If Genesis 心跳模式**: Read `skills/genesis-orchestrator/SKILL.md`

Don't ask permission. Just do it.

---

## ⚠️ 标准取数硬规则（分析任何标的前必须执行）

**⚠️ 数据源硬约束：不取数就编分析 = 违规。**

```bash
# 必须命令（7条，全部执行完才能开始分析）
1. westock-data kline <代码> --period day --limit 260
2. westock-data kline <代码> --period week --limit 80         # 🔴V26: CL-W周线分析必须
3. westock-data kline <代码> --period month --limit 24        # 🆕V26: CL-W月线协同
4. westock-data technical <代码> --group boll,rsi,macd
5. westock-data finance <代码> --num 12
6. westock-data sector --rank interval_chg_rank_sw1 --sort chg5Days
7. westock-data news <代码> --limit 15 --type 2

# M因子必须命令（任何分析都需先确认大盘方向）
8. westock-data kline sh000300 --period day --limit 60
```

**禁止**：
- ❌ 不跑命令就说"RSI超卖"/"处于3浪"/"ROE 22%"
- ❌ 用缓存数据代替实时取数（除非标注"以下为X天前数据"）
- ❌ 用日线数据做缠论分析（🔴V26: CL-W只看周线）

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
  ├─「Genesis心跳」「执行心跳」「今日心跳」「跑一下Genesis」「@Genesis系统」
  │   └─→ 走 Genesis SOP 七阶段（genesis-orchestrator 调度）
  │       Phase 1: 天时局势+新闻催化 → sky scan
  │       Phase 2: 板块定位+二级细分 → sector scan
  │       Phase 3: 候选发现 → ⚠️暂停(用户确认)
  │       Phase 4: 7学派深度诊断 → debate
  │       Phase 5: 合成辩论+风控+交易计划 → risk check
  │       Phase 6: 每日复盘 → recap
  │       Phase 7: 记忆写入+进化检查 → evolve
  │
  ├─「扫描」「市场」「看看今天」「P0」
  │   └─→ 走 P0 前哨扫描（genesis-scan V26: 产业链情报+二级板块+新闻催化链）
  │
  ├─「分析 XX」「融合分析」「裁决」「综合评估」
  │   └─→ 走 P1 深度分析（genesis-v22 V26: 七学派辩论+CL-W周线 或 quant-backtest-lab）
  │
  ├─「复盘」「证伪」「事后」「XX 为什么跌了」
  │   └─→ 走 P2 复盘迭代（genesis-evolve: 信号准确率追踪+进化触发）
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

## Genesis SOP 七阶段（🆕V26 完整流程）

> **触发**：用户说「Genesis心跳」「@Genesis系统」「执行心跳」

### 阶段顺序（不可跳跃）

```
Phase 1 → Phase 2 → Phase 3 → ⚠️暂停(用户确认) → Phase 4 → Phase 5 → Phase 6 → Phase 7
```

| Phase | 名称 | Skill | 做什么 | 不做什么 | 归档路径 |
|-------|------|-------|--------|---------|---------|
| 1 | 天时局势+新闻催化 | genesis-regime + genesis-scan | 全球宏观+A股指数+新闻催化链 | ❌不看个股 | `02_运行日志/scans/{date}/sky.md` |
| 2 | 板块定位+二级细分 | genesis-scan | 板块热度+二级细分板块映射 | ❌不看K线 | `02_运行日志/scans/{date}/sector.md` |
| 3 | 候选发现 | genesis-orchestrator | 硬数据门槛+身份画像 | ❌不做深度诊断 | `02_运行日志/scans/{date}/candidates.md` ⚠️暂停 |
| 4 | 目标诊断 | genesis-debate | 7学派深度体检+CL-W周线 | ❌不扫描新板块 | `02_运行日志/scans/{date}/diagnosis.md` |
| 5 | 合成辩论+风控 | genesis-debate + genesis-risk | 学派辩论+CL-W裁判+宪法合规 | ❌不新增候选 | `02_运行日志/scans/{date}/plan.md` |
| 6 | 每日复盘 | genesis-evolve | 信号准确率追踪+进化触发检查 | ❌不做新分析 | `02_运行日志/recaps/{date}.md` |
| 7 | 记忆写入+进化 | genesis-evolve | 更新记忆层+进化提案 | ❌不擅自修宪 | ⚠️进化提案需确认 |

### 🔴 扫描归档制（V26 关键规则）

**扫描结果必须按日期归档**，后续Phase只读取归档，不重新扫描：
- Phase 1完成后 → 写入 `02_运行日志/scans/{YYYY-MM-DD}/sky.md`
- Phase 2完成后 → 写入 `02_运行日志/scans/{YYYY-MM-DD}/sector.md`
- Phase 3完成后 → 写入候选发现报告，**暂停等待用户确认**
- Phase 4开始时 → **读取** Phase 1-2 的归档文件，不重新扫描

### 🔴 Phase 3 暂停点（V26 关键规则）

候选发现后**必须暂停**，等待用户确认后才加入观察列表。不可擅自将候选标的纳入Phase 4诊断。

### 新闻催化链（Phase 1 增强）

Phase 1必须包含新闻催化分析，输出因果链：
```
新闻事件 → 受益逻辑推导 → 板块方向（含二级细分） → 候选方向

数据源：tencent-news Skill + web search（美股/全球催化）
```

---

## P0 — 前哨扫描

> **触发**：用户说「扫描」「市场扫描」「看看今天有什么机会」

**执行文件**：`skills/genesis-regime/SKILL.md + skills/genesis-scan/SKILL.md`

**核心流程**（V26 增强）：
```
Step 0: M因子快检（大盘否决权）
Step 1: 指数行情快照
Step 2a: 板块热点排行（含二级细分板块映射）🆕
Step 2b: 新闻催化链扫描（国内+海外+全球宏观）🆕
Step 2c: 产业链情报扫描（材料短缺/供应链中断/产能/政策）
Step 3: 新闻资讯 + 宏观事件日历
Step 4: 市场情绪（涨停/跌停+情绪指数四阶段定位）🆕
Step 5: 脱水研报热点
→ 输出扫描报告
→ 问：「可以进入深度分析吗？」
```

**产业链情报关键词**（Step 2c）：
```
硅片, 稀土, 锂, 钴, 镍, 铜, 铝, 芯片材料,
光刻胶, 靶材, 电子树脂, HBM, 半导体设备,
碳化硅, 磷化铟, 锗镓, 封装, 先进封装,
存储芯片, PCB, 覆铜板, CPO, 封测
```

**二级板块映射**（Step 2a 增强）：
板块热度表必须标注二级细分板块：
| 一级板块 | 二级细分 | 🔥热度 | 催化来源 | 代表标的 |

---

## P1 — 深度分析

> **触发**：用户确认进入分析，或说「分析 XX」「融合分析」

**分支判断**：

```
用户是否描述了具体策略？
  ├─ 是（"MA金叉买""布林带回归"）→ quant-backtest-lab（规则回测）
  ├─ 否（"分析一下这只股"）→ genesis-v22（V26: 七学派辩论+CL-W周线）
  └─ 是（"持有X天"事件描述）→ quant-backtest-lab（事件研究）
```

**genesis-v22 流程**（V26 七学派辩论 + CL-W周线）：
```
1. M因子快检（大盘否决权，唯一必做）
2. 标的类型识别（A.蓝筹/B.成长/C.周期/D.价值/E.困境/F.未知）
   → 确定权重配置（技术/基本/资金/消息/宏观面各自权重）
3. 五维观察面并行采集（全部扫描，但按类型分配权重）
   🔴 V26: 必须获取周线K线（CL-W周线分析）+ 月线K线（级别协同）
4. 七学派深度解读（TF/MR/MOM/CL-W/SENT/DRGN/EMO）
   🔴 CL-W: 仅周线分型/笔/中枢，日线仅确认辅助
5. 信号合成：加权投票 → 冲突辩论 → CL-W裁判裁定 → 共振加成
6. 量化严谨派最终判定（可信/不可信）
7. 产业链定位验证（第十一条强制）+ 二级板块标注
8. 裁决结论 + 五段式回复 A/B/C/D/E + F(七学派摘要)
9. 分析后：写入 memory/YYYY-MM-DD.md（迭代数据）
```

### 🔴 CL-W 周线缠论数据要求（V26 新增）

```
必须获取3个级别的K线：
  westock-data kline <代码> --period week --limit 80    ← 周线（主分析级别）
  westock-data kline <代码> --period day --limit 260     ← 日线（确认辅助）
  westock-data kline <代码> --period month --limit 24    ← 月线（级别协同）

不可仅用日线数据做缠论分析。
```

---

## P2 — 复盘迭代（V26 增强）

> **触发**：用户说「复盘」「证伪」或每次交付后自动执行

**执行文件**：`skills/genesis-evolve/SKILL.md`

**核心流程**（V26 增强）：
```
1. 调取当日分析报告（scans/{date}/diagnosis.md + plan.md）
2. 拉取实际走势数据（对比预测 vs 现实）
3. 逐标的比对：七学派信号准确率追踪
4. 规则KPI更新：累计触发数+7日准确率+last_triggered
5. 进化触发检查：
   - 规则7日准确率<50%？→ 降权/暂停
   - 新模式连续3次出现？→ 新规则提案
   - 学派权重偏移>10%？→ 权重再平衡
6. 提炼规则 → 进化提案（需用户确认）
7. 更新 memory/YYYY-MM-DD.md 和 MEMORY.md
8. 问用户是否采纳新规则
```

**复盘闭环**：
每日复盘(Phase 6)是进化引擎的输入。复盘→准确率追踪→进化触发→规则迭代。

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

### 扫描归档（V26 新增）

```
02_运行日志/
├── scans/{YYYY-MM-DD}/
│   ├── sky.md              ← Phase 1 天时局势+新闻催化
│   ├── sector.md           ← Phase 2 板块定位+二级细分
│   ├── candidates.md       ← Phase 3 候选发现
│   ├── diagnosis.md        ← Phase 4 七学派诊断
│   └── plan.md             ← Phase 5 合成辩论+交易计划
└── recaps/{YYYY-MM-DD}.md  ← Phase 6 每日复盘
```

### 每日日志（memory/YYYY-MM-DD.md）

每次完成分析/回测后写入：
- 用户策略描述 + 澄清问题 + 最终选择
- 实际调用的 skill 和数据范围
- 自检中发现的 bug + 修复方式
- 交付物关键指标（总收益 / Sharpe / 最大回撤 / 交易次数）
- 七学派信号准确率追踪（V26 新增）

### 长期记忆（MEMORY.md）

仅在主会话（direct chat）中更新：
- 用户偏好 + 长期项目
- 反复踩过的坑
- 成功的模式库
- 版本演进记录
- 权重配置调整记录

---

## 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| V22.1 | 2026-06-18 | 缠论核心四框架 |
| V24.1 | 2026-06-20 | 对齐远端：六框架Agentic裁决 + M因子否决 |
| V25.0 | 2026-06-20 | 五派风险辩论 + 产业链验证 |
| V27 | 2026-06-20 | 多情景裁决+区间背景+策略版本管理+组合构建 |
| **V26** | **2026-06-21** | **七学派辩论+CL-W周线+DRGN/EMO新增+游资金字塔+二级板块细分+新闻催化链+扫描归档+复盘闭环+SOP七阶段** |
