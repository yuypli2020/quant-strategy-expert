#!/usr/bin/env python3
"""
Genesis 数据采集工具箱 V1.0
统一数据获取接口：A股/港股/美股基本面+行情+财务数据

Usage:
  python3 data_acquisition.py quote <code>          # 实时行情
  python3 data_acquisition.py financials <code>     # 财务报表
  python3 data_acquisition.py valuation <code>      # 估值指标(P/E/PB/PEG/DCF)
  python3 data_acquisition.py moat <code>           # 护城河评估
  python3 data_acquisition.py earnings <code>       # 财报关键指标
  python3 data_acquisition.py seasonality           # 市场时钟(季节性+政策周期)

依赖: yahooquery (pip install yahooquery)
"""

import sys
import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

# ============================================================
# 数据源抽象层
# ============================================================

class DataSource:
    """统一数据源接口，优先 yahooquery，降级 web scraping"""

    @staticmethod
    def safe_float(value, default: float = 0.0) -> float:
        """安全转换浮点数，处理 yahooquery 的 dict 格式"""
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, dict):
            for k in ("raw", "fmt", "longFmt", "value"):
                if k in value:
                    return DataSource.safe_float(value.get(k), default)
            return default
        try:
            return float(value)
        except Exception:
            return default

    @staticmethod
    def fetch_quote(ticker: str) -> Dict:
        """获取实时行情"""
        try:
            from yahooquery import Ticker
            t = Ticker(ticker)
            data = t.price.get(ticker, {})
            return {
                "price": DataSource.safe_float(data.get("regularMarketPrice")),
                "change_pct": DataSource.safe_float(data.get("regularMarketChangePercent")),
                "volume": DataSource.safe_float(data.get("regularMarketVolume")),
                "high_52w": DataSource.safe_float(data.get("fiftyTwoWeekHigh")),
                "low_52w": DataSource.safe_float(data.get("fiftyTwoWeekLow")),
                "market_cap": DataSource.safe_float(data.get("marketCap")),
                "pe_ttm": DataSource.safe_float(data.get("trailingPE")),
                "pe_forward": DataSource.safe_float(data.get("forwardPE")),
            }
        except ImportError:
            return {"error": "yahooquery not installed. Run: pip install yahooquery"}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def fetch_financials(ticker: str) -> Dict:
        """获取财务报表关键指标"""
        try:
            from yahooquery import Ticker
            t = Ticker(ticker)

            # 关键统计
            stats = t.key_stats.get(ticker, {})

            # 财务数据
            fin = t.financial_data.get(ticker, {})

            return {
                # 盈利能力
                "roe": DataSource.safe_float(stats.get("returnOnEquity")) * 100,
                "roa": DataSource.safe_float(stats.get("returnOnAssets")) * 100,
                "gross_margin": DataSource.safe_float(stats.get("grossMargins")) * 100,
                "net_margin": DataSource.safe_float(stats.get("profitMargins")) * 100,
                "operating_margin": DataSource.safe_float(stats.get("operatingMargins")) * 100,

                # 增长
                "revenue_growth": DataSource.safe_float(stats.get("revenueGrowth")) * 100,
                "earnings_growth": DataSource.safe_float(stats.get("earningsGrowth")) * 100,

                # 财务健康
                "debt_to_equity": DataSource.safe_float(stats.get("debtToEquity")),
                "current_ratio": DataSource.safe_float(stats.get("currentRatio")),
                "quick_ratio": DataSource.safe_float(stats.get("quickRatio")),

                # 现金流
                "free_cash_flow": DataSource.safe_float(fin.get("freeCashflow")),
                "operating_cash_flow": DataSource.safe_float(fin.get("totalCashFromOperatingActivities")),
                "capex": DataSource.safe_float(fin.get("capitalExpenditures")),

                # 估值
                "pe_forward": DataSource.safe_float(stats.get("forwardPE")),
                "peg_ratio": DataSource.safe_float(stats.get("pegRatio")),
                "price_to_book": DataSource.safe_float(stats.get("priceToBook")),
                "price_to_sales": DataSource.safe_float(stats.get("priceToSales")),

                # 分红
                "dividend_yield": DataSource.safe_float(stats.get("dividendYield")) * 100,
                "payout_ratio": DataSource.safe_float(stats.get("payoutRatio")) * 100,
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def compute_dcf(fcf: float, growth_rates: List[float], wacc: float = 0.10,
                    terminal_growth: float = 0.03, shares: float = 1.0) -> Dict:
        """
        三阶段 DCF 估值模型
        growth_rates: [高增长期(3年), 中等增长期(2年), 永续增长率]
        """
        if fcf <= 0:
            return {"error": "FCF must be positive for DCF"}

        stages = [
            ("高增长期", 3, growth_rates[0] if len(growth_rates) > 0 else 0.15),
            ("中等增长期", 2, growth_rates[1] if len(growth_rates) > 1 else 0.08),
            ("永续增长期", 0, 0),  # terminal value
        ]

        pv_sum = 0
        current_fcf = fcf
        year = 1

        # Stage 1 & 2
        for stage_name, duration, growth in stages[:2]:
            for _ in range(duration):
                current_fcf *= (1 + growth)
                pv = current_fcf / ((1 + wacc) ** year)
                pv_sum += pv
                year += 1

        # Stage 3: Terminal Value
        terminal_value = current_fcf * (1 + terminal_growth) / (wacc - terminal_growth)
        pv_terminal = terminal_value / ((1 + wacc) ** (year - 1))
        pv_sum += pv_terminal

        intrinsic_per_share = pv_sum / shares if shares > 0 else 0

        return {
            "fcf_base": fcf,
            "wacc": wacc,
            "terminal_growth": terminal_growth,
            "intrinsic_value": intrinsic_per_share,
            "total_pv": pv_sum,
            "growth_stage_1": growth_rates[0] if growth_rates else 0.15,
            "growth_stage_2": growth_rates[1] if len(growth_rates) > 1 else 0.08,
        }

    @staticmethod
    def estimate_moat(stats: Dict) -> Dict:
        """
        段永平五维护城河评分模型
        返回: {维度: {score: 1-5, evidence: str}, overall: float}
        """
        moat = {}

        # 1. 网络效应 (20%)
        moat["network_effect"] = {"score": 3, "weight": 0.20,
            "evidence": "需人工评估：用户规模、平台双边市场、生态粘性"}

        # 2. 品牌护城河 (20%)
        gross_margin = stats.get("gross_margin", 0)
        if gross_margin > 50:
            moat["brand"] = {"score": 5, "weight": 0.20,
                "evidence": f"毛利率{gross_margin:.1f}%>50%，强定价权"}
        elif gross_margin > 30:
            moat["brand"] = {"score": 3, "weight": 0.20,
                "evidence": f"毛利率{gross_margin:.1f}%中等"}
        else:
            moat["brand"] = {"score": 2, "weight": 0.20,
                "evidence": f"毛利率{gross_margin:.1f}%偏低，定价权弱"}

        # 3. 技术护城河 (20%)
        moat["technology"] = {"score": 3, "weight": 0.20,
            "evidence": "需人工评估：专利壁垒、R&D投入、技术领先性"}

        # 4. 成本优势 (20%)
        op_margin = stats.get("operating_margin", 0)
        if op_margin > 30:
            moat["cost_advantage"] = {"score": 5, "weight": 0.20,
                "evidence": f"营业利润率{op_margin:.1f}%>30%"}
        elif op_margin > 15:
            moat["cost_advantage"] = {"score": 3, "weight": 0.20,
                "evidence": f"营业利润率{op_margin:.1f}%中等"}
        else:
            moat["cost_advantage"] = {"score": 2, "weight": 0.20,
                "evidence": f"营业利润率{op_margin:.1f}%偏低"}

        # 5. 切换成本 (20%)
        moat["switching_cost"] = {"score": 3, "weight": 0.20,
            "evidence": "需人工评估：数据沉淀、服务依赖、迁移难度"}

        overall = sum(m["score"] * m["weight"] for m in moat.values())
        moat["overall"] = round(overall, 2)

        # 评级
        if overall >= 4.5:
            moat["rating"] = "极宽护城河 ⭐⭐⭐⭐⭐"
        elif overall >= 4.0:
            moat["rating"] = "宽阔护城河 ⭐⭐⭐⭐"
        elif overall >= 3.0:
            moat["rating"] = "中等护城河 ⭐⭐⭐"
        else:
            moat["rating"] = "护城河狭窄 ⭐⭐"

        return moat


# ============================================================
# A股市场时钟 (新增)
# ============================================================

class AMarketClock:
    """A股市场时钟：季节性规律、政策周期、资金面周期"""

    @staticmethod
    def get_month_factor(month: int) -> Dict:
        """A股月度季节性因子"""
        seasonality = {
            1:  {"name": "春季躁动启动", "bias": "偏多", "factor": 1.2,
                 "reason": "年初流动性宽松+两会政策预期+机构调仓"},
            2:  {"name": "春季躁动延续", "bias": "偏多", "factor": 1.15,
                 "reason": "两会前政策预期升温"},
            3:  {"name": "两会窗口", "bias": "中性", "factor": 1.0,
                 "reason": "两会期间政策落地，利好兑现"},
            4:  {"name": "财报季", "bias": "分化", "factor": 0.95,
                 "reason": "年报一季报密集披露，业绩驱动分化"},
            5:  {"name": "五穷", "bias": "偏空", "factor": 0.85,
                 "reason": "Sell in May效应，流动性边际收紧"},
            6:  {"name": "六绝", "bias": "偏空", "factor": 0.80,
                 "reason": "半年末资金面紧张+政策空窗"},
            7:  {"name": "七翻身预热", "bias": "中性偏多", "factor": 1.05,
                 "reason": "半年报预告+流动性改善预期"},
            8:  {"name": "中报季", "bias": "分化", "factor": 0.95,
                 "reason": "中报密集披露，业绩验证期"},
            9:  {"name": "金九", "bias": "偏多", "factor": 1.10,
                 "reason": "秋季开工+政策密集期+国庆前行情"},
            10: {"name": "银十", "bias": "中性偏多", "factor": 1.05,
                 "reason": "三季报+秋季行情延续"},
            11: {"name": "年末调仓", "bias": "中性", "factor": 0.95,
                 "reason": "机构年末调仓+排名行情"},
            12: {"name": "年末效应", "bias": "分化", "factor": 0.90,
                 "reason": "年末流动性收紧+机构锁定收益"},
        }
        return seasonality.get(month, {"name": "未知", "bias": "中性", "factor": 1.0, "reason": ""})

    @staticmethod
    def get_policy_cycle(date: datetime = None) -> Dict:
        """A股政策周期检测"""
        if date is None:
            date = datetime.now()

        month = date.month

        # 两会窗口 (3月)
        if month == 3:
            return {"cycle": "两会窗口", "policy_intensity": "高",
                    "focus": ["政府工作报告", "产业政策", "财政预算"]}

        # 政治局会议窗口 (4/7/10/12月)
        if month in (4, 7, 10, 12):
            return {"cycle": "政治局会议窗口", "policy_intensity": "高",
                    "focus": ["经济形势研判", "货币政策定调", "产业方向"]}

        # 中央经济工作会议 (12月)
        if month == 12:
            return {"cycle": "中央经济工作会议", "policy_intensity": "最高",
                    "focus": ["明年经济工作总基调", "重点任务部署"]}

        return {"cycle": "常规政策窗口", "policy_intensity": "中",
                "focus": ["行业政策", "部委文件"]}

    @staticmethod
    def get_sector_rotation() -> Dict:
        """A股板块轮动时钟"""
        month = datetime.now().month

        if month in (1, 2, 3):
            return {"phase": "春季躁动", "lead": ["科技成长", "券商"],
                    "lag": ["消费防御", "公用事业"]}
        elif month in (4, 5, 6):
            return {"phase": "业绩驱动", "lead": ["消费白马", "医药"],
                    "lag": ["纯题材", "高估值成长"]}
        elif month in (7, 8, 9):
            return {"phase": "秋季行情", "lead": ["周期股", "新能源"],
                    "lag": ["防御股"]}
        else:
            return {"phase": "年末收官", "lead": ["金融地产", "低估值"],
                    "lag": ["高波动题材"]}


# ============================================================
# 财报关键指标提取
# ============================================================

class EarningsAnalyzer:
    """财报关键指标提取与评分"""

    @staticmethod
    def analyze(financials: Dict) -> Dict:
        """从财务数据中提取关键信号"""
        signals = []

        # ROE 分析
        roe = financials.get("roe", 0)
        if roe > 20:
            signals.append({"signal": "bullish", "strength": 9,
                "reason": f"ROE {roe:.1f}% > 20%，巴菲特标准优秀"})
        elif roe > 15:
            signals.append({"signal": "bullish", "strength": 7,
                "reason": f"ROE {roe:.1f}% 良好"})
        elif roe < 10:
            signals.append({"signal": "bearish", "strength": 6,
                "reason": f"ROE {roe:.1f}% < 10%，资本回报偏弱"})

        # 毛利率
        gm = financials.get("gross_margin", 0)
        if gm > 50:
            signals.append({"signal": "bullish", "strength": 8,
                "reason": f"毛利率{gm:.1f}%>50%，强定价权"})
        elif gm < 20:
            signals.append({"signal": "bearish", "strength": 5,
                "reason": f"毛利率{gm:.1f}%<20%，竞争激烈"})

        # 营收增长
        rg = financials.get("revenue_growth", 0)
        if rg > 20:
            signals.append({"signal": "bullish", "strength": 7,
                "reason": f"营收增速{rg:.1f}%>20%，高增长"})
        elif rg < 0:
            signals.append({"signal": "bearish", "strength": 8,
                "reason": f"营收增速{rg:.1f}%为负，衰退信号"})

        # PEG
        peg = financials.get("peg_ratio", 0)
        if peg > 0 and peg < 1.0:
            signals.append({"signal": "bullish", "strength": 8,
                "reason": f"PEG {peg:.2f}<1.0，低估信号"})
        elif peg > 2.0:
            signals.append({"signal": "bearish", "strength": 6,
                "reason": f"PEG {peg:.2f}>2.0，估值偏高"})

        # 资产负债率
        de = financials.get("debt_to_equity", 0)
        if de > 200:
            signals.append({"signal": "bearish", "strength": 7,
                "reason": f"负债权益比{de:.0f}%>200%，财务杠杆偏高"})

        # 综合信号
        bull = sum(s["strength"] for s in signals if s["signal"] == "bullish")
        bear = sum(s["strength"] for s in signals if s["signal"] == "bearish")
        net = bull - bear

        if net > 15:
            verdict = "STRONG_BUY"
        elif net > 5:
            verdict = "BUY"
        elif net > -5:
            verdict = "HOLD"
        else:
            verdict = "AVOID"

        return {
            "signals": signals,
            "bull_score": bull,
            "bear_score": bear,
            "net_score": net,
            "verdict": verdict
        }


# ============================================================
# CLI 入口
# ============================================================

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 data_acquisition.py <command> <ticker>")
        print("Commands: quote, financials, valuation, moat, earnings, seasonality, dcf")
        sys.exit(1)

    cmd = sys.argv[1]
    ticker = sys.argv[2] if len(sys.argv) > 2 else None

    ds = DataSource()

    if cmd == "quote" and ticker:
        result = ds.fetch_quote(ticker)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif cmd == "financials" and ticker:
        result = ds.fetch_financials(ticker)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif cmd == "moat" and ticker:
        stats = ds.fetch_financials(ticker)
        result = ds.estimate_moat(stats)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif cmd == "earnings" and ticker:
        fin = ds.fetch_financials(ticker)
        result = EarningsAnalyzer.analyze(fin)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif cmd == "dcf" and ticker:
        fin = ds.fetch_financials(ticker)
        fcf = fin.get("free_cash_flow", 0)
        shares = 1_000_000_000  # default, should fetch actual shares
        result = ds.compute_dcf(fcf, [0.15, 0.08], 0.10, 0.03, shares)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif cmd == "seasonality":
        now = datetime.now()
        clock = AMarketClock()
        result = {
            "month_factor": clock.get_month_factor(now.month),
            "policy_cycle": clock.get_policy_cycle(now),
            "sector_rotation": clock.get_sector_rotation(),
            "current_month": now.month,
            "current_date": now.strftime("%Y-%m-%d")
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif cmd == "valuation" and ticker:
        quote = ds.fetch_quote(ticker)
        fin = ds.fetch_financials(ticker)
        dcf = ds.compute_dcf(fin.get("free_cash_flow", 0), [0.15, 0.08])
        result = {**quote, **fin, "dcf": dcf}
        print(json.dumps(result, indent=2, ensure_ascii=False))

    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
