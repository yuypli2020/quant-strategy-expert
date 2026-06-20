# 策略模板 — v1

> 复制此文件到 `strategies/<ticker>_<alias>/v1/readme.md`，替换所有 `{{}}` 内容

---

## 基本信息

| 字段 | 内容 |
|------|------|
| 标的 | {{标的名称}} {{代码}} |
| 策略类型 | {{规则回测 / 事件研究 / 四框架分析 / 多标的选股}} |
| 创建日期 | {{YYYY-MM-DD}} |
| 创建人 | Agent（量化策略专家） |
| 对应 SOUL 版本 | V22.1 |
| 分析框架 | {{genesis-v22 四框架 / quant-backtest-lab 规则 / ...}} |

---

## 策略描述

{{用户原始描述}}

**结构化翻译**：
- 信号触发条件：
- 执行时点：
- 止损逻辑：
- 仓位规则：

---

## 核心指标

| 指标 | 数值 |
|------|------|
| 回测期间 | {{YYYY-MM-DD}} ~ {{YYYY-MM-DD}} |
| 总收益率 | +X% |
| 年化收益率 | +X% |
| Sharpe | X.XX |
| 最大回撤 | -X% |
| 交易次数 | X 次 |
| 胜率 | X% |
| 平均持仓天数 | X 天 |

---

## Self-Refutation（3个怀疑点）

1. **{{怀疑点1}}**
   → {{排除/验证方式}}

2. **{{怀疑点2}}**
   → {{排除/验证方式}}

3. **{{怀疑点3}}**
   → {{排除/验证方式}}

---

## 数据来源

- K线：westock-data kline {{symbol}} --period day --limit {{N}}
- 技术指标：westock-data technical {{symbol}} --group {{ma,macd}}
- 财务数据：westock-data finance {{symbol}} --num 12
- 板块数据：westock-data sector --rank

---

## 交付物文件

```
{{ticker}}_{{alias}}/v1/
├── readme.md           ← 本文件
├── {{prefix}}_equity.csv
├── {{prefix}}_trades.csv
└── {{prefix}}_summary.json
```

---

## 用户选择记录

{{记录用户最终选择的策略参数 / 放弃的替代方案}}

---

## 下次迭代待验证

{{下次回测/分析时需要重点验证的假设}}
