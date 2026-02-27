import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI)

    Args:
        data: Series of close prices
        period: Number of periods (default: 14)

    Returns:
        Series with RSI values (0-100)
    """
    try:
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    except Exception as e:
        logger.error(f"Error calculating RSI: {e}")
        return pd.Series(dtype=float)


def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
    """
    Calculate MACD (Moving Average Convergence Divergence)

    Args:
        data: Series of close prices
        fast: Fast EMA period (default: 12)
        slow: Slow EMA period (default: 26)
        signal: Signal line period (default: 9)

    Returns:
        Tuple of (MACD line, Signal line, Histogram)
    """
    try:
        ema_fast = data.ewm(span=fast).mean()
        ema_slow = data.ewm(span=slow).mean()

        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram
    except Exception as e:
        logger.error(f"Error calculating MACD: {e}")
        return pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=float)


def calculate_bollinger_bands(data: pd.Series, period: int = 20, num_std: float = 2) -> tuple:
    """
    Calculate Bollinger Bands

    Args:
        data: Series of close prices
        period: Rolling window period (default: 20)
        num_std: Number of standard deviations (default: 2)

    Returns:
        Tuple of (Upper Band, Middle Band, Lower Band)
    """
    try:
        middle_band = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()

        upper_band = middle_band + (std * num_std)
        lower_band = middle_band - (std * num_std)

        return upper_band, middle_band, lower_band
    except Exception as e:
        logger.error(f"Error calculating Bollinger Bands: {e}")
        return pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=float)


def calculate_moving_average(data: pd.Series, period: int) -> pd.Series:
    """
    Calculate Simple Moving Average (SMA)

    Args:
        data: Series of prices
        period: Moving average period

    Returns:
        Series with moving average values
    """
    return data.rolling(window=period).mean()


def calculate_ema(data: pd.Series, period: int) -> pd.Series:
    """
    Calculate Exponential Moving Average (EMA)

    Args:
        data: Series of prices
        period: EMA period

    Returns:
        Series with EMA values
    """
    return data.ewm(span=period).mean()


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Average True Range (ATR)

    Args:
        high: Series of high prices
        low: Series of low prices
        close: Series of close prices
        period: ATR period (default: 14)

    Returns:
        Series with ATR values
    """
    try:
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()

        return atr
    except Exception as e:
        logger.error(f"Error calculating ATR: {e}")
        return pd.Series(dtype=float)


def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> tuple:
    """
    Calculate Stochastic Oscillator

    Args:
        high: Series of high prices
        low: Series of low prices
        close: Series of close prices
        period: Stochastic period (default: 14)

    Returns:
        Tuple of (K line, D line)
    """
    try:
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()

        k_line = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_line = k_line.rolling(window=3).mean()

        return k_line, d_line
    except Exception as e:
        logger.error(f"Error calculating Stochastic: {e}")
        return pd.Series(dtype=float), pd.Series(dtype=float)


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add common technical indicators to a DataFrame

    Args:
        df: DataFrame with OHLCV data (columns: open, high, low, close, volume)

    Returns:
        DataFrame with additional indicator columns
    """
    try:
        # RSI
        df['rsi'] = calculate_rsi(df['close'], period=14)

        # MACD
        df['macd'], df['signal'], df['macd_hist'] = calculate_macd(df['close'])

        # Bollinger Bands
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = calculate_bollinger_bands(df['close'])

        # Moving Averages
        df['sma20'] = calculate_moving_average(df['close'], 20)
        df['sma50'] = calculate_moving_average(df['close'], 50)
        df['ema12'] = calculate_ema(df['close'], 12)

        # ATR
        df['atr'] = calculate_atr(df['high'], df['low'], df['close'])

        # Stochastic
        df['stoch_k'], df['stoch_d'] = calculate_stochastic(df['high'], df['low'], df['close'])

        # Volume indicators
        df['volume_sma'] = calculate_moving_average(df['volume'], 20)

        return df

    except Exception as e:
        logger.error(f"Error adding technical indicators: {e}")
        return df
