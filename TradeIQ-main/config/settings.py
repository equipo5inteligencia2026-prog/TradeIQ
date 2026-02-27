import os
from pathlib import Path

# Project root path
PROJECT_ROOT = Path(__file__).parent.parent

# Database configuration
DB_PATH = PROJECT_ROOT / "data" / "tradeiq.db"
DB_URL = f"sqlite:///{DB_PATH}"

# Data directories
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed"
MODELS_PATH = PROJECT_ROOT / "models" / "trained_models"

# Ensure directories exist
RAW_DATA_PATH.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_PATH.mkdir(parents=True, exist_ok=True)
MODELS_PATH.mkdir(parents=True, exist_ok=True)

# Stock and crypto symbols
STOCK_SYMBOLS = ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "GOOGL", "META", "AMD"]
CRYPTO_SYMBOLS = ["BTC", "ETH", "SOL", "BNB", "XRP"]

# ML Model Configuration
ML_CONFIG = {
    "test_size": 0.2,
    "validation_size": 0.1,
    "lookback_window": 60,  # 60 days of historical data
    "forecast_horizon": [7, 14, 30],  # 7, 14, 30 days ahead
    "batch_size": 32,
    "epochs": 100
}

# Cache configuration
CACHE_TTL = 3600  # 1 hour

# Default user for demo
DEFAULT_USER = {
    "email": "trader@tradeiq.com",
    "password": "password123",
    "name": "Trader Pro",
    "risk_profile": "moderado"
}
