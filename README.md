# 量化策略专家 — Genesis V22.1 融合派交易系统

> 一个能把自然语言交易策略翻译成可运行回测的工程化 Agent。完整能力打包 + 自部署协议。

---

## 🎯 这是什么

一个完整的量化策略研究 Agent 的全部资产，包含：

- **Genesis V22.1 融合派分析系统** — 缠论周线 × 波浪理论 × 板块轮动 × 事件驱动
- **完整 Skill 库** — 14 个规则模块 + 回测骨架 + 数据工具 + 进化引擎
- **自部署协议** — 新 Agent 从零恢复的全部阶段指南
- **历史产出** — 已验证的回测策略和执行脚本

---

## 📦 仓库结构

```
quant-strategy-expert/
├── SELF_DEPLOYMENT_PROTOCOL.md    ← 核心：完整自部署文档（逐阶段恢复指南）
├── docs/
│   └── EXPERT_PACKAGE.md          ← 能力快照 + 状态报告
├── quant-strategy-expert/         ← Agent 人格与行为文件
│   ├── SOUL.md                    ← 人格 + 六阶段 + Iron Rules
│   ├── AGENTS.md                  ← 行为准则 + P0/P1/P2 工作流
│   ├── TOOLS.md                   ← Skill 使用指南
│   ├── TOOLS_PATCH.md             ← 回测流程补丁（self_refutation + 策略生命周期）
│   ├── DEPLOYMENT_MANUAL.md       ← Genesis 部署手册
│   ├── IDENTITY.md / MEMORY.md / USER.md / HEARTBEAT.md / BOOTSTRAP.md
├── skills/
│   ├── genesis/                    ← 融合派核心系统（14个模块）
│   │   ├── 00_宪法层/             ← 七条不可变规则
│   │   ├── 01_规则仓库/
│   │   │   ├── 融合派/            ← 共振算法 + 操作矩阵
│   │   │   ├── 缠论周线/          ← 买卖点 + MA20 + 回测模板
│   │   │   ├── 波浪理论/          ← 浪型 + 斐波那契
│   │   │   ├── 板块轮动/          ← 评分算法 + 过滤
│   │   │   ├── 事件驱动/          ← 事件分类 + 催化剂
│   │   │   ├── 新闻信号/          ← 黄金坑 + 板块早信号 + 宏观
│   │   │   └── 执行协议/          ← ATR/3R + 风险堡垒
│   │   ├── 03_进化引擎/           ← 进化协议 + changelog
│   │   └── 05_模板/
│   ├── genesis-scan/               ← P0 前哨扫描入口
│   ├── genesis-analyze/            ← P1 深度分析入口
│   ├── genesis-evolve/             ← P2 进化复盘入口
│   ├── quant-backtest-lab/         ← 回测主骨架（三件套 + 仪表盘）
│   ├── backtest-expert/            ← 鲁棒性评估
│   ├── quantitative-research/      ← Alpha 诊断 + 过拟合检测
│   ├── westock-data/               ← 结构化数据 CLI
│   ├── westock-tool/               ← 选股/板块 CLI
│   └── neodata-financial-search/  ← 金融语义搜索
├── strategies/                     ← 策略版本库
│   └── sz002463_ma20_week/       ← 沪电股份 MA20 周线策略
├── backtests/                      ← 历史回测产出
│   ├── ma20_week_sz399006.py     ← 创业板指 MA20 周线
│   ├── chanlun_week_sz002463.js  ← 沪电股份缠论周线
│   └── calculate_atr.js           ← ATR 计算脚本
└── tasks/
    └── tracker.md                 ← Genesis 任务追踪清单
```

---

## 🚀 快速开始

### 方式一：完全恢复（推荐）

1. 克隆本仓库
2. 阅读 `SELF_DEPLOYMENT_PROTOCOL.md`，按阶段 0→8 逐阶段执行
3. 完成验证后，从阶段九选择一个进化方向开始

### 方式二：选择性恢复

只恢复需要的部分：

```bash
# 只恢复 Genesis 融合派系统
cp -r skills/genesis/ <your_workspace>/skills/

# 只恢复回测骨架
cp -r skills/quant-backtest-lab/ <your_workspace>/skills/
```

---

## 🧠 Genesis V22.1 融合派框架

### 五框架共振

| 框架 | 用途 | 权重 |
|------|------|------|
| 缠论周线 | 判断方向（核心） | 30% |
| 波浪理论 | 定位浪型 | 20% |
| 板块轮动 | 资金验证 | 15% |
| 事件驱动 | 催化时机 | 15% |
| 新闻信号 | 情绪辅助 | 20% |

**核心约束**：缠论周线看空 → 其他框架再好也不做

### 六阶段执行路线

```
阶段0 初始化 → 阶段1 宏观扫描 → 阶段2 深度验证
→ 阶段3 信号融合 → 阶段4 执行协议 → 阶段5 风险堡垒
→ 阶段6 进化复盘
```

---

## 🔧 工具链

### 数据获取（降级优先级）

| 数据类型 | 首选工具 | 降级方案 |
|---------|---------|---------|
| K线 / 行情 | `westock-data` CLI | online-search |
| 选股 / 板块 | `westock-tool` CLI | — |
| 新闻资讯 | `online-search` / `tencent-news` | web_search |
| 语义搜索 | `neodata-financial-search` | `online-search` |

### westock-data 调用方式

```bash
node skills/westock-data/scripts/index.js quote sh600519
node skills/westock-data/scripts/index.js kline sh600519 --period day --limit 250
node skills/westock-data/scripts/index.js kline sh600519 --period week --limit 80
node skills/westock-data/scripts/index.js technical sh600519 --group ma,macd,rsi
```

---

## 📈 进化路线图

恢复完成后，按以下方向持续进化：

| 方向 | 内容 |
|------|------|
| E-1 缠论周线 | 从 MA20 → 完整分型/笔/中枢/买卖点 |
| E-2 波浪理论 | 从定性 → ZigZag 半自动识别 |
| E-3 板块轮动 | 从静态评分 → 动态轮动追踪 |
| E-4 新闻信号 | 从关键词 → NLP 情绪分析 |
| E-5 回测框架 | 从手动脚本 → 参数化一键回测 |
| E-6 风险管理 | 从固定 ATR → 多维度动态风控 |
| E-7 进化引擎 | 从手动 changelog → 自动归因+规则建议 |

---

## 📄 许可证

本项目仅供个人研究使用。回测结果不代表实盘收益。

---

## 🔗 链接

- **仓库**: https://github.com/yuypli2020/quant-strategy-expert
- **自部署文档**: `SELF_DEPLOYMENT_PROTOCOL.md`
- **能力快照**: `docs/EXPERT_PACKAGE.md`
