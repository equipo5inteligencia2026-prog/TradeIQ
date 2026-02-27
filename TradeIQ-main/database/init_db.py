import uuid
from datetime import datetime, timedelta
from database.connection import get_session
from database.models import User, Asset, PriceHistory, Portfolio
from config.settings import DEFAULT_USER, STOCK_SYMBOLS, CRYPTO_SYMBOLS
import logging
import hashlib

logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def init_database():
    """Initialize database with default data"""
    session = get_session()
    try:
        # Check if DB already has data
        user_count = session.query(User).count()
        if user_count > 0:
            logger.info("Database already initialized with users")
            return

        # Create default user
        default_user = User(
            user_id=str(uuid.uuid4()),
            email=DEFAULT_USER["email"],
            username=DEFAULT_USER["email"].split("@")[0],
            password_hash=hash_password(DEFAULT_USER["password"]),
            name=DEFAULT_USER["name"],
            risk_profile=DEFAULT_USER["risk_profile"],
            is_active=1,
            subscription_tier="pro",
            created_at=datetime.utcnow(),
            last_login=datetime.utcnow()
        )
        session.add(default_user)
        logger.info(f"Created default user: {DEFAULT_USER['email']}")

        # Commit user first so portfolio can reference it
        session.commit()

        # Create default portfolio for the user
        default_portfolio = Portfolio(
            portfolio_id=str(uuid.uuid4()),
            user_id=default_user.user_id,
            name="Mi Portafolio",
            risk_profile=DEFAULT_USER["risk_profile"],
            total_value=10000.0,
            cash_available=10000.0
        )
        session.add(default_portfolio)
        logger.info(f"Created portfolio for user: {DEFAULT_USER['email']}")

        # Create stock and cryptocurrency assets
        assets_to_create = []

        # Stocks
        for symbol in STOCK_SYMBOLS:
            asset = Asset(
                asset_id=f"{symbol}-STOCK",
                symbol=symbol,
                name=f"{symbol} Inc.",
                asset_type="stock",
                exchange="NASDAQ",
                currency="USD",
                is_active=1
            )
            assets_to_create.append(asset)

        # Cryptos
        for symbol in CRYPTO_SYMBOLS:
            asset = Asset(
                asset_id=f"{symbol}-CRYPTO",
                symbol=symbol,
                name=f"{symbol}",
                asset_type="crypto",
                exchange="CRYPTO",
                currency="USD",
                is_active=1
            )
            assets_to_create.append(asset)

        session.add_all(assets_to_create)
        logger.info(f"Created {len(assets_to_create)} assets")

        # Commit assets first so we can reference them
        session.commit()

        # Add historical price data for the last 60 days
        base_prices = {
            "AAPL": 187.42,
            "TSLA": 242.10,
            "NVDA": 875.20,
            "MSFT": 415.80,
            "AMZN": 180.50,
            "GOOGL": 140.30,
            "META": 420.15,
            "AMD": 180.90,
            "BTC": 67840,
            "ETH": 3520.50,
            "SOL": 198.30,
            "BNB": 612.45,
            "XRP": 2.45,
        }

        import random
        now = datetime.utcnow()
        prices_to_add = []

        for asset in assets_to_create:
            base_price = base_prices.get(asset.symbol, 100)

            # Create 60 days of historical data
            for days_ago in range(60, 0, -1):
                date = now - timedelta(days=days_ago)

                # Random price movements
                open_p = base_price + random.uniform(-5, 5)
                close_p = open_p + random.uniform(-3, 3)
                high_p = max(open_p, close_p) + random.uniform(0, 2)
                low_p = min(open_p, close_p) - random.uniform(0, 2)
                volume = random.randint(1000000, 10000000)

                price_record = PriceHistory(
                    asset_id=asset.asset_id,
                    timestamp=date,
                    open_price=round(open_p, 2),
                    high_price=round(high_p, 2),
                    low_price=round(low_p, 2),
                    close_price=round(close_p, 2),
                    volume=volume,
                    adjusted_close=round(close_p, 2)
                )
                prices_to_add.append(price_record)
                base_price = close_p  # Use close price as base for next day

        session.add_all(prices_to_add)
        logger.info(f"Created {len(prices_to_add)} price history records")

        session.commit()
        logger.info("Database initialization completed successfully")

    except Exception as e:
        session.rollback()
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_database()
