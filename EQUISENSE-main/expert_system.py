def run_expert_system(indicators):
    pe_ratio = indicators.get('pe_ratio')
    revenue_growth = indicators.get('revenue_growth')
    rsi = indicators.get('rsi')
    macd = indicators.get('macd')
    signal_line = indicators.get('signal_line')
    ma_50 = indicators.get('ma_50')
    ma_200 = indicators.get('ma_200')

    # ── STRONG BUY RULES
    if rsi and pe_ratio:
        if rsi < 30 and pe_ratio < 15:
            return {
                'recommendation': 'BUY',
                'reason': 'Stock is oversold (RSI below 30) with a low P/E ratio below 15, indicating it is undervalued and a strong buying opportunity.'
            }

    if rsi and revenue_growth:
        if rsi < 30 and revenue_growth > 10:
            return {
                'recommendation': 'BUY',
                'reason': 'Stock is oversold (RSI below 30) combined with strong revenue growth above 10%, signaling a high-potential buying opportunity.'
            }

    if ma_50 and ma_200:
        if ma_50 > ma_200 and macd and macd > 0:
            return {
                'recommendation': 'BUY',
                'reason': 'Golden cross detected — the 50-day moving average is above the 200-day moving average, and positive MACD confirms bullish momentum.'
            }

    if pe_ratio and revenue_growth:
        if pe_ratio < 20 and revenue_growth > 15:
            return {
                'recommendation': 'BUY',
                'reason': 'Strong revenue growth above 15% combined with a reasonable P/E ratio below 20 indicates a financially healthy and growing company.'
            }

    # ── STRONG SELL RULES 
    if rsi and pe_ratio:
        if rsi > 70 and pe_ratio > 30:
            return {
                'recommendation': 'SELL',
                'reason': 'Stock is overbought (RSI above 70) with an inflated P/E ratio above 30, suggesting the stock is overvalued and due for a correction.'
            }

    if ma_50 and ma_200:
        if ma_50 < ma_200 and macd and macd < 0:
            return {
                'recommendation': 'SELL',
                'reason': 'Death cross detected — the 50-day moving average has fallen below the 200-day moving average, and negative MACD confirms bearish momentum.'
            }

    if revenue_growth and rsi:
        if revenue_growth < 0 and rsi > 60:
            return {
                'recommendation': 'SELL',
                'reason': 'Declining revenue combined with an overbought RSI above 60 indicates weakening fundamentals while the stock remains overpriced.'
            }

    if pe_ratio and revenue_growth:
        if pe_ratio > 40 and revenue_growth < 5:
            return {
                'recommendation': 'SELL',
                'reason': 'Extremely high P/E ratio above 40 with weak revenue growth below 5% indicates the stock is significantly overvalued relative to its performance.'
            }

    # ── HOLD RULES 
    if rsi:
        if 40 <= rsi <= 60:
            return {
                'recommendation': 'HOLD',
                'reason': 'RSI is in the neutral zone between 40 and 60, indicating no strong momentum in either direction. It is advisable to hold and monitor.'
            }

    if pe_ratio and revenue_growth:
        if 15 <= pe_ratio <= 25 and 5 <= revenue_growth <= 15:
            return {
                'recommendation': 'HOLD',
                'reason': 'P/E ratio and revenue growth are both within moderate ranges, suggesting the stock is fairly valued with steady but unremarkable performance.'
            }

    if macd and signal_line:
        if abs(macd - signal_line) < 0.5:
            return {
                'recommendation': 'HOLD',
                'reason': 'MACD and signal line are very close together, indicating market indecision. Holding is recommended until a clearer trend emerges.'
            }

    # ── DEFAULT 
    return {
        'recommendation': 'HOLD',
        'reason': 'Insufficient signal strength from the available indicators to justify a Buy or Sell recommendation. Holding is advised pending further data.'
    }