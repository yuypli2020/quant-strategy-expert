---
name: chanlun-weekly
description: |
  缠论周线分析。当需要判断趋势方向和买卖点时使用（核心skill）。
---

# 缠论周线 SKILL.md

## 一、核心原则

**仅使用周线级别，不使用日线。**

---

## 二、数据获取

```bash
# 获取周线数据
westock-data kline XXX --period week --limit 80

# 获取技术指标
westock-data technical XXX --group ma,macd,rsi
```

---

## 三、笔的定义与判定

### 3.1 顶底分型

```
顶分型：三根连续K线，中间K线的高点最高
  ┌───────┐
  │  高  │  ← 最高点
  └───────┘
  ┌───────┐
  │  中  │
  └───────┘
  ┌───────┐
  │  低  │  ← 最高点
  └───────┘

底分型：三根连续K线，中间K线的低点最低
  ┌───────┐
  │  高  │  ← 最低点
  └───────┘
  ┌───────┐
  │  中  │
  └───────┘
  ┌───────┐
  │  低  │  ← 最低点
  └───────┘
```

### 3.2 笔的构成

```
笔 = 底分型 + n根K线 + 顶分型（n ≥ 3）
    或
笔 = 顶分型 + n根K线 + 底分型（n ≥ 3）
```

### 3.3 简化判定（用于回测）

```
顶分型：连续3根K线，第2根高点 > 第1根高点 AND 第2根高点 > 第3根高点
底分型：连续3根K线，第2根低点 < 第1根低点 AND 第2根低点 < 第3根低点

笔确认：顶分型后出现底分型（下跌笔结束）
      底分型后出现顶分型（上升笔结束）
```

---

## 四、买卖点判定

### 4.1 一买（趋势反转买点）

```
条件：
1. 连续3个或以上下跌笔
2. 最后一个下跌笔后出现底分型
3. 底分型后出现阳线突破

简化判定（金叉）：
1. MA20向下
2. 价格在MA20下方
3. 金叉出现（价格上穿MA20）
```

### 4.2 二买（回调确认买点）

```
条件：
1. 一买后形成上升笔
2. 上升笔后回调
3. 回调不破一买低点
4. 出现底分型

简化判定：
1. 一买形成后
2. 价格回踩MA20
3. 不破前低
4. 再次金叉（或在MA20支撑）
```

### 4.3 三买（中枢突破买点）

```
条件：
1. 存在上涨后形成的中枢
2. 价格回调到中枢上沿
3. 回调不破中枢上沿
4. 出现底分型

简化判定：
1. 价格在MA20上方
2. 回踩MA20
3. 再次金叉
```

### 4.4 一卖（趋势反转卖点）

```
条件：
1. 连续3个或以上上升笔
2. 最后一个上升笔后出现顶分型
3. 顶分型后出现阴线跌破

简化判定（死叉）：
1. MA20向上
2. 价格在MA20上方
3. 死叉出现（价格下穿MA20）
```

### 4.5 二卖（反弹确认卖点）

```
条件：
1. 一卖后形成下跌笔
2. 下跌笔后反弹
3. 反弹不破一卖高点
4. 出现顶分型

简化判定：
1. 死叉形成后
2. 反弹到MA20
3. 再次死叉
```

---

## 五、中枢定义

### 5.1 中枢构成

```
中枢 = 三笔的重叠部分
     = max(前两笔高低点的重叠区间)
```

### 5.2 中枢简化

```
中枢区间 = [回调最低点, 回调最高点]

简化判定：
- 连续3次触及的价位区间 = 中枢
- 中枢上沿 = 回调高点
- 中枢下沿 = 回调低点
```

---

## 六、简化MA20判定（用于回测）

### 6.1 基础规则

```javascript
// 计算MA20
ma20 = sum(close[i-19..i]) / 20

// 信号判定
if (prev_close <= prev_ma20 AND close > ma20) {
  // 金叉 = 买入信号
  signal = 'BUY';
} else if (prev_close >= prev_ma20 AND close < ma20) {
  // 死叉 = 卖出信号
  signal = 'SELL';
}
```

### 6.2 买卖点映射

| MA20信号 | 缠论买点 | 操作 |
|----------|----------|------|
| 金叉 | 一买/类一买 | 买入 |
| 金叉后回踩MA20不破 | 二买 | 加仓 |
| 价格在MA20上方持有 | 持有 | 持有 |
| 死叉 | 一卖/类一卖 | 卖出 |
| 死叉后反弹MA20不过 | 二卖 | 清仓 |

### 6.3 趋势判断

```
强势：价格 > MA20 > MA60 > MA120
多头：价格 > MA20
震荡：价格围绕MA20波动
空头：价格 < MA20
弱势：价格 < MA20 < MA60 < MA120
```

---

## 七、缠论评级

| 评级 | 缠论状态 | MA20信号 | 操作 | 仓位 |
|------|----------|----------|------|------|
| ★★★★★ | 二买/三买 | 金叉回踩不破 | 重仓买入 | 80-100% |
| ★★★★ | 一买 | 金叉确认 | 正常买入 | 60-80% |
| ★★★ | 上升中继 | 持有 | 持有 | 60% |
| ★★ | 震荡 | 频繁金叉死叉 | 轻仓/观望 | 20-40% |
| ★ | 一卖/二卖 | 死叉 | 清仓 | 0% |

---

## 八、执行模板

```
用户：「缠论分析 XXX」

Step 1: 获取数据
  westock-data kline XXX --period week --limit 80
  westock-data technical XXX --group ma,macd,rsi

Step 2: 计算MA20
  ma20 = sum(last_20_close) / 20

Step 3: 判定买卖点
  - 检查是否存在顶底分型
  - 判定当前趋势
  - 输出买卖点

Step 4: 输出报告
```

---

## 九、输出格式

```
【缠论周线分析】标的名称 (代码)

## 当前状态
- 周线收盘：XXX
- MA20：XXX
- MA60：XXX
- MA120：XXX

## 趋势判断
- 当前位置：MA20 [上/下]
- 趋势：[强势多头/多头/震荡/空头/弱势空头]

## 买卖点
- 当前信号：[金叉/死叉/持有]
- 最近买卖点：[日期] [一买/二买/一卖/二卖]
- 评级：★ X.X

## 关键价位
- 压力位1：XXX（MA60）
- 压力位2：XXX（MA120）
- 支撑位1：XXX（MA20）
- 支撑位2：XXX（前低）

## 操作建议
- 评级：★ X.X
- 建议：[买入/持有/卖出]
- 仓位：XX%
- 止损位：XXX
```

---

## 十、回测模板

```javascript
// 缠论周线MA20回测模板

const params = {
  ma_period: 20,      // MA周期
  initial_cash: 1000000,
  commission: 0.0003,  // 3bps
};

// 计算MA20
function calcMA20(data) {
  for (let i = 19; i < data.length; i++) {
    let sum = 0;
    for (let j = 0; j < 20; j++) {
      sum += data[i - j].close;
    }
    data[i].ma20 = sum / 20;
  }
  return data;
}

// 判定信号
function checkSignal(prevData, currData) {
  const prevAbove = prevData.close > prevData.ma20;
  const currAbove = currData.close > currData.ma20;
  
  if (!prevAbove && currAbove) return 'BUY';   // 金叉
  if (prevAbove && !currAbove) return 'SELL';  // 死叉
  return null;
}

// 回测主逻辑
function backtest(data) {
  let cash = params.initial_cash;
  let position = 0;
  let signal = null;
  
  for (let i = 20; i < data.length; i++) {
    const prev = data[i - 1];
    const curr = data[i];
    
    // 判定信号（下周执行）
    const sig = checkSignal(prev, curr);
    
    if (sig === 'BUY' && position === 0) {
      // 买入
      position = Math.floor(cash / curr.open / 100) * 100;
      cash -= position * curr.open * (1 + params.commission);
      signal = 'BUY';
    }
    
    if (sig === 'SELL' && position > 0) {
      // 卖出
      cash += position * curr.open * (1 - params.commission);
      position = 0;
      signal = 'SELL';
    }
  }
  
  return calculateMetrics();
}
```

---

## 十一、Self-Refutation

```
可能错误：
1. 周线滞后：金叉确认时可能已上涨10%+
2. 震荡市失效：频繁金叉死叉导致频繁止损

失效边界：
- 跌破周线MA20 → 止损
- 3周内未盈利 → 可能趋势失效

数据局限：
- 周线每周只有5个数据点
- 无法识别日内大幅波动
- 分型判定依赖K线形态
```

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1 | 2026-06-18 | 完整缠论周线策略 |
