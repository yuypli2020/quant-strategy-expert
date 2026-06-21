# TOOLS.md - Skill 使用指南

> **前置规则**：调用任何 skill 前，先确认它出现在当前 session 的 `<available_skills>` 列表中。不在列表 = 已关闭，按下方「降级方案」处理。本文件提到的所有 CLI 命令和调用流程，仅在对应 skill 可用时生效。

## 数据采集脚本（V26.1 新增）

> **角色**：独立于 Skills 的 Python 数据采集工具箱，用于无法调用 westock-data 时降级使用
> **依赖**：`pip install yahooquery`
> **位置**：`scripts/data_acquisition.py`

```bash
# 行情
python3 scripts/data_acquisition.py quote AAPL
python3 scripts/data_acquisition.py quote sh600519

# 财务报表 + 估值
python3 scripts/data_acquisition.py financials AAPL
python3 scripts/data_acquisition.py valuation MSFT

# 护城河评估（段永平五维）
python3 scripts/data_acquisition.py moat AMZN

# 财报信号提取（ROE/毛利率/PEG/负债）
python3 scripts/data_acquisition.py earnings AAPL

# DCF估值（三阶段模型）
python3 scripts/data_acquisition.py dcf MSFT

# 市场时钟（A股季节性+政策周期+板块轮动）
python3 scripts/data_acquisition.py seasonality
```

### 数据源优先级

```
1. yahooquery (pip install yahooquery) — 美股/港股优先
2. westock-data — A股优先
3. web scraping — 降级方案（精度下降须告知）
```

---

## 产业链情报采集 + 新闻催化链（V26 增强）

> **角色**：P0 前哨扫描的前置情报层 + P1 深度分析前的产业链定位验证
> **触发**：用户说「扫描」「产业链」「XX短缺/涨价」「板块分析」

### 采集清单与数据源（V26 增强）

| 情报类型 | 数据源 | 命令示例 |
|----------|--------|---------|
| 材料短缺/涨价 | web_search + westock-data marketnews | `web_search "硅料短缺 涨价 2026"` |
| 供应链中断 | web_search + neodata | `web_search "半导体 供应链中断 制裁"` |
| 产能投放/缩减 | westock-data news + neodata | `westock-data news <标的> --limit 10` |
| 政策/贸易事件 | web_search | `web_search "半导体 出口管制 关税"` |
| 新闻催化链 | tencent-news + web_search | `搜索国内A股催化 + 美股映射` 🆕 |
| 板块情绪 | westock-data hot + sector | `westock-data hot` / `westock-data sector` 🆕 |

### 新闻催化链分析（V26 新增）

每条催化必须写出完整因果链：
```
新闻事件 → 受益逻辑推导 → 板块方向（含二级细分） → 候选方向

数据源：
- tencent-news Skill：7×24国内新闻 + 板块热点
- web search：美股催化（"TACO" "NVDA" "美联储"）+ 全球宏观（"中东" "贸易"）
```

### 二级板块细分查询（V26 新增）

分析板块时必须标注二级细分板块：

| 一级板块 | 二级细分 | 代表标的查询 |
|---------|---------|------------|
| 电子 | 存储芯片 | `westock-data board --name 存储芯片` |
| 电子 | PCB | `westock-data board --name PCB` |
| 电子 | 封测 | `westock-data board --name 封测` |
| 电子 | 光通信/CPO | `westock-data board --name CPO` |
| 电子 | 消费电子/射频 | `westock-data board --name 消费电子` |
| 电子 | 半导体设备 | `westock-data board --name 半导体设备` |

完整映射表：`skills/genesis-scan/sector_taxonomy.md`

> **角色**：P0 前哨扫描的前置情报层 + P1 深度分析前的产业链定位验证
> **触发**：用户说「扫描」「产业链」「XX短缺/涨价」「板块分析」

### 采集清单与数据源

| 情报类型 | 数据源 | 命令示例 |
|----------|--------|---------|
| 材料短缺/涨价 | web_search + westock-data marketnews | `web_search "硅料短缺 涨价 2026"` |
| 供应链中断 | web_search + neodata | `web_search "半导体 供应链中断 制裁"` |
| 产能投放/缩减 | westock-data news + neodata | `westock-data news <标的> --limit 10` |
| 政策/贸易事件 | web_search | `web_search "半导体 出口管制 关税"` |

### 产业链受益方向判定

| 事件类型 | 受益方向 | 受损方向 |
|----------|---------|---------|
| 材料短缺/涨价 | 上游生产商 ✅ | 中下游成本承压 ❌ |
| 供应链中断 | 替代供应商 ✅ | 依赖该供应链的企业 ❌ |
| 政策催化（国产替代） | 国产厂商 ✅ | 进口依赖企业 ❌ |
| 产能释放 | 龙头（规模效应）✅ | 二线（价格战）❌ |

### 产业链定位验证（第十一条强制）

每只推荐标的必须验证产业链位置：

```bash
# 步骤1：查主营业务
westock-data profile sh688396

# 步骤2：判断位置
# "功率半导体设计生产销售 + 开放式晶圆制造" → 中游（晶圆厂）→ 硅片的买方/使用者，不是卖方/生产商

# 步骤3：标注定位
# 上游 = 直接受益 ✅
# 中游 = 成本端影响 ⚠️
# 下游 = 间接影响 ⚠️
# 概念沾边 = 必须剔除 ❌
```

**典型教训**：华润微(688396)主营"功率半导体设计+晶圆制造"，是**中游使用者**，不是硅片生产商。被归入"大硅片"板块是概念沾边，不验证就推荐 = 违规。

---

## 🔴 CL-W 周线缠论数据获取（V26 新增）

> **强制规则**：缠论分析**必须使用周线K线**作为主分析级别，日线仅做确认辅助，月线做级别协同。不可仅用日线数据做缠论分析。

```bash
# 三条必须全部执行：
westock-data kline <代码> --period week --limit 80     ← 周线（主分析级别）
westock-data kline <代码> --period day --limit 260      ← 日线（确认辅助）
westock-data kline <代码> --period month --limit 24     ← 月线（级别协同）
```

**CL-W 分析流程**：
1. 周线分型判定（顶分型/底分型确认）
2. 周线笔方向判断（向上笔/向下笔）
3. 周线中枢位置计算（重叠区间）
4. 日线确认（周线信号+日线同向=强度更高）
5. 月线协同（月线支撑/压力位验证）

## DRGN/EMO 情绪数据源（V26 新增）

```bash
# 游资龙头识别 (DRGN)
westock-data lhb <代码>              ← 龙虎榜（机构买入/游资席位）
westock-data hot                     ← 热搜榜（人气第一龙头判断）
westock-data sector --rank           ← 板块最强标的排序

# 情绪周期定位 (EMO)
westock-data kline sh000001 --period day --limit 60   ← 大盘环境
web_search "今日涨停板统计 连板数 2026"                ← 涨停板情绪
web_search "A股情绪指数"                               ← 市场情绪量化
```

**EMO 四阶段情绪判断指标**：
| 阶段 | 连板数 | 涨停板数 | 操作策略 |
|------|--------|---------|---------|
| 启动期 | 1-2 | ≤5 | 🟢开始介入 |
| 发酵期 | 2-4 | 5-15 | 🟢重仓 |
| 高潮期 | 5+ | 15+ | 🔴逐步兑现 |
| 退潮期 | 0-1 | ≤3 | 🔴空仓 |

---

## Skill 可用性速查

| Skill | 不可用时的影响 | 降级方案 |
|---|---|---|
| `westock-data` | 无法获取结构化时序数据 | web_fetch / online-search 获取公开数据，精度下降，须告知用户 |
| `westock-tool` | 无法批量选股/筛选 universe | 用 westock-data 逐只查询（低效）或 web_fetch |
| `neodata-financial-search` | 无法语义搜索/事件查证 | online-search 或 web_fetch |
| `quant-backtest-lab` | 无法执行标准回测流程 | **无降级**，必须告知用户，建议开启 |
| `backtest-expert` | 无法自动鲁棒性评估 | 在 C 段手动覆盖分析要点 |
| `quantitative-research` | 无法自动 Alpha 诊断 | 在 C 段手动覆盖分析要点 |

## Skill 文件位置

> 以下目录结构为理想配置。skill 实际是否存在取决于用户是否开启。

```
# === 数据层 ===
westock-data/                  数据-个股结构化时序(回测主数据源)
westock-tool/                  数据-选股筛池 / 板块成份
neodata-financial-search/      数据-跨资产语义搜索 / 事件查证

# === 分析层（流派系统）=== 
trend-following/               趋势跟踪流派
mean-reversion/                均值回归流派
momentum-flow/                 动量/资金流派
event-sentiment/               事件/情绪流派
fundamental/                   基本面流派
chan-theory/                   缠论流派

# === 融合层 ===
fusion-engine/                 融合引擎（交叉辩论+综合报告）

# === 回测层 ===
quant-backtest-lab/            回测主骨架 / 三件套契约 / 仪表盘 / 自检
backtest-expert/               鲁棒性评估 / 参数敏感性 / 滑点压力
quantitative-research/         Alpha 真伪诊断 / 过拟合 / regime 依赖

# === 运营层 ===
portfolio-manager/             组合管理（持仓/交易/计划）
review-engine/                 复盘引擎（事后归因/规则提炼）

# === 系统层 ===
workflows/                     流程增强（self_refutation / review_evolve / multi_perspective）
strategies/                    策略版本库
portfolio/                     组合数据
```

### 分析标的时的调用顺序

```
用户：「分析一下 XXX」
  ↓
1. 检查 portfolio/positions.json → 是否有持仓
2. 拉取所有流派需要的数据（一次取完）
3. 逐个流派分析（trend→mean-reversion→momentum→event→fundamental→chan）
4. fusion-engine 加载各流派输出 → 交叉辩论 → 综合报告
5. 更新交易计划 → 保存到 portfolio/plans/
6. 输出综合分析报告

用户：「复盘 XXX」
  ↓
1. 调取 portfolio/plans/ 中的分析计划
2. 拉取实际走势
3. review-engine 四维度归因
4. 提炼规则 → 写入 MEMORY.md + 更新策略版本
```

---

## 何时使用「westock-data」

### 角色

回测**主数据源**。所有需要喂进 Python 回测循环的结构化时序,都走这里。

### 触发关键词

| 数据类型 | 用户可能说的话 | CLI 示例 |
|---|---|---|
| 行情 | "实时行情"、"现在多少钱"、"现价" | `westock-data quote sh600519` |
| K线 | "日线"、"周线"、"K线"、"历史价格" | `westock-data kline sh600519 --period day --limit 250` |
| 财报 | "财务"、"营收"、"利润"、"ROE" | `westock-data finance sh600519 --num 12` |
| 公司简况 | "主营"、"业务介绍"、"行业" | `westock-data profile sh600519` |
| 资金流向 | "主力资金"、"北向资金" | `westock-data asfund sh600519` / `hkfund` / `usfund` |
| 龙虎榜 | "龙虎榜"、"游资" | `westock-data lhb sz000001`(仅 A股) |
| 大宗交易 | "大宗" | `westock-data blocktrade sz000001`(仅沪深) |
| 融资融券 | "两融"、"融资余额" | `westock-data margintrade sz000001`(仅沪深) |
| 技术指标 | "MACD"、"RSI"、"BOLL" | `westock-data technical sh600519 --group macd` |
| 筹码成本 | "筹码"、"持仓成本" | `westock-data chip sh600519`(仅沪深京 A) |
| 股东结构 | "十大股东"、"股权" | `westock-data shareholder sh600519`(仅 A 股 / 港股) |
| 分红 | "分红"、"除权除息" | `westock-data dividend sh600519` |
| ETF | "ETF"、"指数基金" | `westock-data etf sh510300` / `etf-holdings sh510300` |
| 板块 | "板块"、"概念股"、"成份股" | `westock-data sector --search 华为` |
| 投资日历 | "今日重要事件" | `westock-data calendar 2026-04-22` |
| 新股 | "打新"、"新股申购" | `westock-data ipo hs` |
| 业绩预告 | "业绩预告"、"业绩快报" | `westock-data reserve sh600519` |
| 停复牌 | "停牌"、"复牌" | `westock-data suspension hs` |
| 宏观 | "GDP"、"CPI"、"M2" | `westock-data macro --indicator gdp --year 2025` |
| 搜索 | "代码是多少"、"叫什么" | `westock-data search 腾讯控股` |

### 代码格式

| 市场 | 前缀 | 示例 |
|---|---|---|
| 上交所 | sh | sh600519 |
| 深交所 | sz | sz000001 |
| 北交所 | bj | bj430047 |
| 港股 | hk | hk00700 |
| 美股 | us | usAAPL |

### 已知限制

- 龙虎榜 / 大宗交易 / 融资融券:仅沪深(sh/sz)
- 筹码成本:仅沪深京 A 股(sh/sz/bj)
- 股东结构:仅 A 股和港股
- 港股 / 美股货币单位必须保持 HKD / USD,**禁止套人民币符号**
- `search` / `minute` 不支持批量

---

## 何时使用「westock-tool」

### 角色

多标的回测的 **universe 来源** —— "找出符合条件的所有股票"。

### 触发关键词

| 任务 | 用户可能说的话 |
|---|---|
| 条件选股 | "找出 PE<20 且 ROE>15% 的股票"、"筛一下小市值高股息" |
| 板块成份 | "新能源板块所有股票"、"沪深 300 成份股" |
| 预置策略 | "MACD 金叉"、"突破年线"、"放量上涨"(40+ 预置) |
| 财务筛选 | "营收增速 >30%"、"扣非净利润为正" |
| 技术筛选 | "MA20 上穿 MA60"、"BOLL 下轨触底" |

### 用法要点

- **不要把 CSI 300 / CSI 500 当全市场代理**:它们是头部 / 中盘选样,有显著选样偏差
- 筛出 N 只 → 喂 westock-data 取每只的完整 K 线 → 再进回测
- 必须断言 `len(loaded) == len(target)`,加载失败的标的要在最终回复中明确披露

---

## 何时使用「neodata-financial-search」

### 角色

**仅做语义补充**,不进回测循环。

### 触发关键词

| 任务 | 用户可能说的话 |
|---|---|
| 跨资产宏观 | "美元指数走势"、"原油价格"、"黄金 vs 比特币" |
| 事件查证 | "央行什么时候降准的?"、"特朗普关税政策具体哪天?" |
| 宏观叙事 | "中美利差"、"债券收益率倒挂"、"经济衰退指标" |
| 研报 / 新闻 | "看看最近的研报怎么说"、"最新行业新闻" |
| 公募基金 | "中欧医疗基金净值" —— 主要覆盖中国境内基金,不覆盖香港基金 |

### 已知限制(命中即跳过,直接走 westock-data 或公开检索)

- 公募基金不覆盖香港基金
- 板块 / 指数基础数据、板块资金、估值主要覆盖 A 股
- 龙虎榜、融资融券、业绩发布会、估值同行对比偏 A 股
- 商品 / 贵金属以行情为主,不等同于完整基本面

### 关键约束

**不要把 neodata 的输出直接当回测价格序列**:它返回的是 LLM-context 大小的语义片段,有截断和排序启发,不是结构化全量时序。最多用来确认事件日期,然后再用 westock-data 取完整 K 线。

---

## 何时使用「quant-backtest-lab」

### 角色

整个 Agent 的**主骨架**。回测脚本结构、三件套契约、HTML 仪表盘、自检流程,全部在这里。

### 触发场景(几乎所有回测任务)

| 用户描述 | 形态 |
|---|---|
| "MA 金叉买、死叉卖,回测一下"、"海龟突破策略"、"布林带均值回归" | 规则型策略回测 |
| "央行降准后买入持有 30 日,平均收益多少?"、"业绩超预期后第二天买、5 日卖" | 事件研究 |
| "PE<20 且 ROE>15% 的股票每月买入"、"动量前 5 名持有 1 个月" | 多标的选股 |
| "60% 沪深 300 + 40% 国债,季度再平衡"、"风险平价" | 组合再平衡 |

### 调用流程

```
1. mandatory 第一步:读 reference/pitfalls/pandas.md + reference/common_pitfalls.md
2. 读 reference/strategy_parsing.md,把策略翻译成结构化形式
3. 写 <prefix>_backtest.py(纯 Python + pandas,signal-on-i / execute-on-i+1,warmup 段独立)
4. 调用 reference/export_results.py 落 3 个标准文件到 cwd
5. 用 reference/render_dashboard.py + dashboard_template.html 渲染 index.html
6. 跑 4 步自检:运行 / pitfalls / sanity+对抗式 / 仪表盘渲染
7. 三段式回复 A/B/C
```

### 必读 reference 子文件

- `pitfalls/pandas.md` —— 写代码前必读
- `common_pitfalls.md` —— 自检时必读
- `china_a_rules.md` / `us_stock_rules.md` / `hong_kong_rules.md` —— 按市场加载
- `dashboard_schema.md` —— 仪表盘字段语义

### 不读的文件

- `dashboard_template.html` —— 2000+ 行 CSS/JS,LLM 不需要读,只需调 `render_dashboard()` 替换占位符

---

## 何时使用「backtest-expert」

### 角色

主流程跑完之后的**鲁棒性评估**。

### 触发场景

| 用户可能说的话 | 调用动作 |
|---|---|
| "这个策略稳不稳?"、"参数换了会怎样?" | 跑参数敏感性扫描 |
| "加点滑点会怎样?"、"实盘能用吗?" | 跑滑点压力测试 |
| "现在的 Sharpe 是真的吗?" | 走 Deploy/Refine/Abandon 打分 |
| "有没有过拟合?" | 走样本外 / Walk-forward 验证 |

### 调用流程

主流程跑完三件套后,如果用户继续追问鲁棒性,调 skill 内的 `evaluate_backtest.py`,把 summary.json + trades.csv 喂进去,输出鲁棒性评级和具体改进建议。

---

## 何时使用「quantitative-research」

### 角色

**方法论级判断**。在 C 段结果解读阶段提供"这是真 alpha 还是 beta 伪装"。

### 触发场景

| 用户可能说的话 | 调用动作 |
|---|---|
| "这个收益是真的吗?"、"会不会就是市场涨了?" | t-stat 显著性检验,beta 拆解 |
| "样本外能跑通吗?" | Walk-forward 分析 |
| "牛市熊市都能用?" | regime 依赖分析 |
| "这是因子暴露还是 alpha?" | 因子归因 |

### 用法要点

仅在用户提出"严肃质疑"或"准备实盘前最终验证"时调用。常规回测任务不必每次走这一步。

---

## 新增工作流文件

以下文件在 `workflows/` 目录下，是本次 Agentic 迭代新增的增强流程：

| 文件 | 用途 | 何时触发 |
|------|------|---------|
| `workflows/self_refutation.md` | 自省清单（7 问） | 每次交付前必做 |
| `workflows/review_evolve.md` | 复盘迭代协议 | P2 阶段 / 每次交付后自动 / 用户说「复盘」|
| `workflows/multi_perspective.md` | 多流派交叉验证 | P1 深度分析时使用 |

### 调用顺序

```
回测/分析任务开始
  ↓
取数 → 脚本 → 执行
  ↓
self_refutation（workflows/self_refutation.md）
  ↓
交付（A/B/C 三段式，C 段包含自省结论）
  ↓
自动复盘（workflows/review_evolve.md：轻量版）
  ↓
写入 memory/ + MEMORY.md
```

---

## Skill 协作矩阵

| 当前任务 | 主要 skill | 辅助 skill |
|---|---|---|
| 单标的规则策略 | quant-backtest-lab | westock-data |
| 多标的选股 | quant-backtest-lab | westock-tool + westock-data |
| 事件研究 | quant-backtest-lab | westock-data + neodata(查事件日期) |
| 组合再平衡 | quant-backtest-lab | westock-tool + westock-data |
| 鲁棒性追问 | backtest-expert | quant-backtest-lab(主流程已跑) |
| 严肃实盘前验证 | quantitative-research | backtest-expert + quant-backtest-lab |
| **标的完整分析** | **fusion-engine** + 6个流派skills | westock-data + westock-tool（取数据） |
| **复盘迭代** | **review-engine** | portfolio/ + memory/ |
| **组合管理** | **portfolio-manager** | portfolio/positions.json |

### 完整分析流程（标的分析场景）

```
1. 取数阶段（一次性拉取）：
   - westock-data kline 日线/周线
   - westock-data technical --group ma,macd,rsi,boll,bias
   - westock-data asfund / quote / finance / news
   - westock-data sector --rank（板块数据）

2. 流派分析（逐个运行）：
   - trend-following → 输出趋势判断
   - mean-reversion → 输出回归信号
   - momentum-flow → 输出动量判断
   - event-sentiment → 输出事件分析
   - fundamental → 输出估值判断
   - chan-theory（如适用）→ 输出缠论分析

3. 融合：
   - fusion-engine 加载所有流派输出
   - 识别共识/分歧 → 推理 → 综合报告 + 交易计划

4. 保存 + 输出：
   - 交易计划 → portfolio/plans/
   - 完整报告 → 回复中呈现
```

---

## 标准回复结构(任何回测任务交付时)

### A. 实现细节(Implementation Details)

至少要说清:

- 哪些数据字段用于信号判定(close / high / low / open),为什么
- 执行时点:次日开盘 / 当日收盘
- 止损止盈触发语义:用 high/low 近似日内 / 仅用 close
- 仓位计算口径:满仓 / 固定金额 / 占比 / 手数取整后实际敞口
- equity_curve 口径:单标的 / 组合 / 含空仓 / 含负现金 / 含 liabilities 的聚合方式
- T+1 处理 / 复合条件组合 / 状态机重置

### B. 已知偏差(Limitations and Bias)

挑 2-3 个最关键的,例如:

- 日线粒度限制:止损止盈无法精确还原日内顺序
- 执行假设偏差:次日开盘价在剧烈波动时与信号价差距大
- 滑点 / 流动性:回测未建模冲击成本
- 数据偏差:复权方式 / 幸存者偏差 / 数据覆盖
- 策略结构性弱点:在哪种市场环境下会失效

### C. 结果解读(Result Interpretation)

从下面挑 3-5 个角度:

- 收益归因:少数大盈利还是高胜率小盈利
- 回撤分析:最差回撤发生在何时,止损是否真的起效
- 交易频次:买入 X 次 / 卖出 Y 次,持仓周期分布
- 信号质量:触发了多少次,被资金 / 手数 / 仓位约束跳过多少次
- 时段表现:年度 / 季度差异
- 策略适用边界:什么市场环境下会失效
- 事件驱动专属:哪些事件贡献最大 / 最差,收益分布是否偏斜
- 组合专属:再平衡频率 / 偏离阈值是否合理

### 写作要求

- 先讲结论 → 用具体交易数据支持 → 结果差就说差,不粉饰
- A/B/C 三段都要写,不许只写 C 漏 A B
- A/B/C/D/E 五段都要写,不许只写 C 漏 A B D E
- **D段**：量化严谨派审查（回测质量/样本外/显著性/过拟合）
- **E段**：产业链定位声明（每只标的的产业链位置：上游✅/中游⚠️/概念沾边❌）
- **不列文件清单**("已生成 xx.csv / xx.json / xx.html") —— 直接进入分析
- 语言锁:跟用户提问语言,不跟标的市场

---

## 快速参考 Prompt

**单标的规则策略:**
```
回测「标的+策略+时间窗+起始资金」
例:回测贵州茅台 2020-2025 年 MA20/MA60 金叉买、死叉卖,起始资金 100 万
```

**事件研究:**
```
事件研究「事件描述+持有期+样本范围」
例:央行降准后第二天买入沪深 300 ETF,持有 30 日,统计 2015-2025 年所有降准事件
```

**多标的选股:**
```
选股回测「筛选条件+持仓规则+时间窗」
例:每月初买入 PE<15 且 ROE>15% 的 A 股,等权持有,2018-2025
```
