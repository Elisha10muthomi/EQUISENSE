def compute_pe_ratio(share_price, eps):
    try:
        if eps == 0:
            return None
        return round(share_price / eps, 2)
    except:
        return None


def compute_revenue_growth(current_revenue, previous_revenue):
    try:
        if previous_revenue == 0:
            return None
        growth = ((current_revenue - previous_revenue) / previous_revenue) * 100
        return round(growth, 2)
    except:
        return None


def compute_rsi(prices, period=14):
    try:
        if len(prices) < period + 1:
            return None
        gains = []
        losses = []
        for i in range(1, period + 1):
            change = prices[i] - prices[i - 1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 2)
    except:
        return None


def compute_ema(prices, period):
    try:
        if len(prices) < period:
            return None
        k = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        for price in prices[period:]:
            ema = (price * k) + (ema * (1 - k))
        return round(ema, 4)
    except:
        return None


def compute_macd(prices):
    try:
        ema12 = compute_ema(prices, 12)
        ema26 = compute_ema(prices, 26)
        if ema12 is None or ema26 is None:
            return None, None
        macd = round(ema12 - ema26, 4)
        return macd
    except:
        return None


def compute_signal_line(prices):
    try:
        if len(prices) < 35:
            return None
        macd_values = []
        for i in range(9, len(prices)):
            subset = prices[:i]
            ema12 = compute_ema(subset, 12)
            ema26 = compute_ema(subset, 26)
            if ema12 and ema26:
                macd_values.append(ema12 - ema26)
        if len(macd_values) < 9:
            return None
        signal = compute_ema(macd_values, 9)
        return signal
    except:
        return None


def compute_moving_average(prices, period):
    try:
        if len(prices) < period:
            return None
        return round(sum(prices[-period:]) / period, 2)
    except:
        return None


def run_calculator(share_price, eps, current_revenue,
                   previous_revenue, historical_prices):
    prices = [float(p.strip()) for p in historical_prices.split(',') if p.strip()]

    pe_ratio = compute_pe_ratio(share_price, eps)
    revenue_growth = compute_revenue_growth(current_revenue, previous_revenue)
    rsi = compute_rsi(prices)
    macd = compute_macd(prices)
    signal_line = compute_signal_line(prices)
    ma_50 = compute_moving_average(prices, 50)
    ma_200 = compute_moving_average(prices, 200)

    return {
        'pe_ratio': pe_ratio,
        'revenue_growth': revenue_growth,
        'rsi': rsi,
        'macd': macd,
        'signal_line': signal_line,
        'ma_50': ma_50,
        'ma_200': ma_200
    }