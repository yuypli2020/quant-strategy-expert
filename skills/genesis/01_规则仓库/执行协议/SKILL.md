---
name: genesis-execution
description: |
  执行协议：仓位计算、ATR/3R、风险堡垒。当需要制定具体交易计划时使用。
---

# 执行协议 SKILL.md

## 一、ATR计算

### 1.1 ATR定义

```
ATR(14) = EMA(TrueRange, 14)

TrueRange = max(
  |当日高点 - 当日低点|,
  |当日高点 - 前一日收盘|,
  |前一日收盘 - 当日低点|
)
```

### 1.2 获取ATR

```bash
# 通过技术指标获取（如果有）
westock-data technical XXX --group all
# 或者手动计算
```

### 1.3 ATR计算代码

```javascript
function calcATR(data, period = 14) {
  const trs = [];
  
  for (let i = 1; i < data.length; i++) {
    const high = data[i].high;
    const low = data[i].low;
    const prevClose = data[i-1].close;
    
    const tr = Math.max(
      high - low,
      Math.abs(high - prevClose),
      Math.abs(prevClose - low)
    );
    trs.push(tr);
  }
  
  // EMA计算ATR
  const multiplier = 2 / (period + 1);
  let atr = trs.slice(0, period).reduce((a, b) => a + b) / period;
  
  for (let i = period; i < trs.length; i++) {
    atr = (trs[i] - atr) * multiplier + atr;
  }
  
  return atr;
}
```

---

## 二、3R仓位计算

### 2.1 3R概念

```
R = 风险金额（止损幅度 × 仓位）

亏损 R = 1R
盈利 R = N × R（N为盈亏比）

目标：找到正期望的R
```

### 2.2 仓位公式

```javascript
function calcPosition(params) {
  const {
    accountSize,      // 账户金额
    riskPercent,      // 账户风险比例（默认2%）
    entryPrice,       // 入场价格
    stopLossPrice,    // 止损价格
    atr              // ATR
  } = params;
  
  // 止损幅度
  const stopLossPct = Math.abs(entryPrice - stopLossPrice) / entryPrice;
  
  // 每份R的金额
  const riskAmount = accountSize * riskPercent;
  
  // 止损金额对应的股数
  const sharePerR = riskAmount / Math.abs(entryPrice - stopLossPrice);
  
  // 取整到最小交易单位
  const position = Math.floor(sharePerR / 100) * 100;
  
  // 实际风险金额
  const actualRisk = position * Math.abs(entryPrice - stopLossPrice);
  const actualRiskPct = actualRisk / accountSize * 100;
  
  // 目标盈利（R的倍数）
  const targetProfit = actualRisk * params.targetR;  // 通常2R或3R
  
  return {
    position,
    riskAmount: actualRisk,
    riskPercent: actualRiskPct,
    targetProfit,
    stopLossPct,
    rewardRiskRatio: params.targetR
  };
}
```

### 2.3 ATR止损

```javascript
// ATR止损法（波动率自适应）
function calcATRStop(entryPrice, atr, multiplier = 2) {
  const stopLossPrice = entryPrice - atr * multiplier;
  return stopLossPrice;
}

// 保守止损：入场价 - 2×ATR
// 激进止损：入场价 - 1.5×ATR
```

---

## 三、仓位等级

### 3.1 融合派评分 → 仓位

| 综合评分 | 仓位上限 | 止损倍数 |
|----------|----------|----------|
| ★★★★★ | 100% | 2×ATR |
| ★★★★ | 80% | 2×ATR |
| ★★★ | 60% | 1.5×ATR |
| ★★ | 40% | 1.5×ATR |
| ★ | 20% | 1×ATR |

### 3.2 账户仓位管理

```
单笔最大仓位 = 账户 × 5%（大市值股）
单笔最大仓位 = 账户 × 3%（小市值股）
单日最大亏损 = 账户 × 3%
单周最大亏损 = 账户 × 5%
```

---

## 四、执行清单

### 4.1 入场前检查

```
□ 融合派评分 ≥ ★★★
□ ATR已计算
□ 止损位已确定
□ 目标位已确定（R倍数）
□ 仓位已计算
□ 风险在可控范围内
□ 账户风险 < 2%
```

### 4.2 入场执行

```javascript
// 入场流程
async function executeEntry(params) {
  const { symbol, position, entryPrice, orderType } = params;
  
  // 1. 下单
  if (orderType === 'LIMIT') {
    // 限价单
    await placeLimitOrder(symbol, position, entryPrice);
  } else {
    // 市价单
    await placeMarketOrder(symbol, position);
  }
  
  // 2. 记录
  const trade = {
    symbol,
    position,
    entryPrice,
    entryTime: new Date(),
    stopLoss: calcATRStop(entryPrice, params.atr),
    target: entryPrice + params.atr * params.targetR,
    status: 'OPEN'
  };
  
  // 3. 保存
  await saveTrade(trade);
  
  return trade;
}
```

### 4.3 止损执行

```javascript
// 止损条件
function shouldStopLoss(trade, currentPrice) {
  if (currentPrice <= trade.stopLoss) {
    return { action: 'STOP_LOSS', price: trade.stopLoss };
  }
  
  // 移动止损
  const profit = (currentPrice - trade.entryPrice) / trade.entryPrice;
  if (profit > 0.50) {  // 50%利润
    const newStop = trade.entryPrice + (currentPrice - trade.entryPrice) * 0.30;
    return { action: 'MOVE_STOP', newStop };
  }
  
  return { action: 'HOLD' };
}
```

---

## 五、风险堡垒检查

### 5.1 风险检查清单

```
□ 单日亏损 < 3%
□ 单周亏损 < 5%
□ 单月亏损 < 10%
□ 持仓集中度 < 30%（单只）
□ 总持仓 < 80%
□ 无流动性风险（成交量充足）
□ 无黑天鹅风险（持仓板块）
```

### 5.2 风险评级

| 风险等级 | 条件 | 操作 |
|----------|------|------|
| 🟢 安全 | 所有检查通过 | 正常交易 |
| 🟡 警戒 | 1-2项超标 | 降低仓位50% |
| 🔴 危险 | 3项以上超标 | 停止开新仓 |
| ⚫ 熔断 | 单日亏损 > 5% | 清仓观望 |

### 5.3 熔断规则

```
连续亏损3次 → 强制休息1天
单日亏损 > 5% → 清仓观望
单周亏损 > 8% → 强制复盘
```

---

## 六、输出格式

```
【执行协议】标的名称 (代码)

## 基础数据
- 入场价格：XXX
- ATR(14)：XXX
- 当前账户：XXX元

## 仓位计算
- 融合派评分：★ X.X
- 建议仓位：XX%
- 仓位上限：XXX股

## 止损设计
- 止损位：XXX
- 止损幅度：X.XX%
- 止损类型：[ATR止损/固定止损]

## 目标设计
- 目标位：XXX
- 目标R倍数：X R
- 预期盈利：XXX元

## 风险检查
| 检查项 | 状态 | 说明 |
|--------|------|------|
| 单日亏损 | 🟢 | <3% |
| 持仓集中度 | 🟢 | XX% |
| 流动性 | 🟢 | 充足 |

## 执行清单
- [ ] 确认融合派评分 ≥ ★★★
- [ ] 确认止损位在 ATR X 倍
- [ ] 确认仓位在账户 X% 以内
- [ ] 确认风险检查全部通过
- [ ] 下单并记录
```

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1 | 2026-06-18 | 完整执行协议 |
