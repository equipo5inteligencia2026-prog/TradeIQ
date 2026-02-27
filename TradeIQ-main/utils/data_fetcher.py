import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from database.connection import get_session
from database.models import Asset, PriceHistory
import logging

logger = logging.getLogger(__name__)

def fetch_stock_data(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch stock data from yfinance

    Args:
        symbol: Stock ticker symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Data interval (1m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo)

    Returns:
        DataFrame with OHLCV data
    """
    try:
        data = yf.download(symbol, period=period, interval=interval, progress=False)
        if isinstance(data, pd.DataFrame):
            return data
        else:
            logger.warning(f"No data found for {symbol}")
            return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()


def fetch_crypto_data(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch cryptocurrency data from yfinance (using Yahoo's crypto tickers)

    Args:
        symbol: Crypto ticker (e.g., BTC-USD, ETH-USD)
        period: Time period
        interval: Data interval

    Returns:
        DataFrame with OHLCV data
    """
    crypto_symbol = f"{symbol}-USD" if not symbol.endswith("-USD") else symbol
    return fetch_stock_data(crypto_symbol, period=period, interval=interval)


def store_price_data(asset_id: str, data: pd.DataFrame) -> int:
    """
    Store price data in database

    Args:
        asset_id: Asset ID in database
        data: DataFrame with OHLCV data

    Returns:
        Number of records stored
    """
    session = get_session()
    count = 0
    try:
        for index, row in data.iterrows():
            # Check if record already exists
            existing = session.query(PriceHistory).filter(
                PriceHistory.asset_id == asset_id,
                PriceHistory.timestamp == index
            ).first()

            if not existing:
                price_record = PriceHistory(
                    asset_id=asset_id,
                    timestamp=index,
                    open_price=float(row.get('Open', 0)),
                    high_price=float(row.get('High', 0)),
                    low_price=float(row.get('Low', 0)),
                    close_price=float(row.get('Close', 0)),
                    volume=int(row.get('Volume', 0)),
                    adjusted_close=float(row.get('Adj Close', row.get('Close', 0)))
                )
                session.add(price_record)
                count += 1

        session.commit()
        logger.info(f"Stored {count} price records for {asset_id}")
        return count

    except Exception as e:
        session.rollback()
        logger.error(f"Error storing price data: {e}")
        return 0
    finally:
        session.close()


def get_price_history(asset_id: str, days: int = 90) -> pd.DataFrame:
    """
    Get price history from database

    Args:
        asset_id: Asset ID in database
        days: Number of days of history to retrieve

    Returns:
        DataFrame with OHLCV data indexed by timestamp
    """
    session = get_session()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        prices = session.query(PriceHistory).filter(
            PriceHistory.asset_id == asset_id,
            PriceHistory.timestamp >= cutoff_date
        ).order_by(PriceHistory.timestamp).all()

        if not prices:
            return pd.DataFrame()

        data = {
            'timestamp': [p.timestamp for p in prices],
            'open': [p.open_price for p in prices],
            'high': [p.high_price for p in prices],
            'low': [p.low_price for p in prices],
            'close': [p.close_price for p in prices],
            'volume': [p.volume for p in prices],
            'adjusted_close': [p.adjusted_close for p in prices]
        }

        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df

    except Exception as e:
        logger.error(f"Error retrieving price history: {e}")
        return pd.DataFrame()
    finally:
        session.close()


def get_latest_price(asset_id: str) -> float:
    """Get the latest closing price for an asset"""
    session = get_session()
    try:
        latest_price = session.query(PriceHistory).filter(
            PriceHistory.asset_id == asset_id
        ).order_by(PriceHistory.timestamp.desc()).first()

        return latest_price.close_price if latest_price else 0.0

    except Exception as e:
        logger.error(f"Error getting latest price: {e}")
        return 0.0
    finally:
        session.close()
