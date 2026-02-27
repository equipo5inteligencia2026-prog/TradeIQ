from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Integer, default=1)
    subscription_tier = Column(String, default="free")
    risk_profile = Column(String)

    portfolios = relationship("Portfolio", back_populates="user")
    strategies = relationship("Strategy", back_populates="user")
    alerts = relationship("Alert", back_populates="user")


class Asset(Base):
    __tablename__ = "assets"

    asset_id = Column(String, primary_key=True)
    symbol = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    asset_type = Column(String)
    exchange = Column(String)
    currency = Column(String, default="USD")
    sector = Column(String)
    market_cap = Column(Float)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    prices = relationship("PriceHistory", back_populates="asset", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="asset", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="asset", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="asset", cascade="all, delete-orphan")
    backtests = relationship("BacktestResult", back_populates="asset", cascade="all, delete-orphan")


class PriceHistory(Base):
    __tablename__ = "price_history"

    price_id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(String, ForeignKey("assets.asset_id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Integer)
    adjusted_close = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset", back_populates="prices")


class MLModel(Base):
    __tablename__ = "ml_models"

    model_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    model_type = Column(String)
    algorithm = Column(String)
    version = Column(String)
    file_path = Column(String)
    is_active = Column(Integer, default=1)
    trained_at = Column(DateTime)
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    metrics_json = Column(Text)

    predictions = relationship("Prediction", back_populates="model")


class Prediction(Base):
    __tablename__ = "predictions"

    prediction_id = Column(String, primary_key=True)
    asset_id = Column(String, ForeignKey("assets.asset_id"), nullable=False, index=True)
    model_id = Column(String, ForeignKey("ml_models.model_id"))
    prediction_date = Column(DateTime, nullable=False)
    horizon_days = Column(Integer)
    predicted_price = Column(Float)
    predicted_trend = Column(String)
    confidence = Column(Float)
    upper_bound = Column(Float)
    lower_bound = Column(Float)
    actual_price = Column(Float)
    is_correct = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset", back_populates="predictions")
    model = relationship("MLModel", back_populates="predictions")


class Strategy(Base):
    __tablename__ = "strategies"

    strategy_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    name = Column(String, nullable=False)
    strategy_type = Column(String)
    parameters_json = Column(Text)
    risk_level = Column(Integer)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="strategies")
    backtests = relationship("BacktestResult", back_populates="strategy")


class BacktestResult(Base):
    __tablename__ = "backtest_results"

    backtest_id = Column(String, primary_key=True)
    strategy_id = Column(String, ForeignKey("strategies.strategy_id"), nullable=False)
    asset_id = Column(String, ForeignKey("assets.asset_id"), nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    initial_capital = Column(Float)
    final_value = Column(Float)
    total_return_pct = Column(Float)
    sharpe_ratio = Column(Float)
    sortino_ratio = Column(Float)
    max_drawdown_pct = Column(Float)
    win_rate = Column(Float)
    num_trades = Column(Integer)
    executed_at = Column(DateTime, default=datetime.utcnow)

    strategy = relationship("Strategy", back_populates="backtests")
    asset = relationship("Asset", back_populates="backtests")


class Portfolio(Base):
    __tablename__ = "portfolios"

    portfolio_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    name = Column(String, nullable=False)
    base_currency = Column(String, default="USD")
    total_value = Column(Float, default=0.0)
    cash_available = Column(Float, default=0.0)
    risk_profile = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Integer, default=1)

    user = relationship("User", back_populates="portfolios")
    trades = relationship("Trade", back_populates="portfolio")


class Trade(Base):
    __tablename__ = "trades"

    trade_id = Column(String, primary_key=True)
    portfolio_id = Column(String, ForeignKey("portfolios.portfolio_id"), nullable=False)
    asset_id = Column(String, ForeignKey("assets.asset_id"), nullable=False)
    trade_type = Column(String)
    quantity = Column(Float)
    price = Column(Float)
    commission = Column(Float, default=0.0)
    status = Column(String, default="pending")
    executed_at = Column(DateTime)
    broker_order_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    portfolio = relationship("Portfolio", back_populates="trades")
    asset = relationship("Asset", back_populates="trades")


class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    asset_id = Column(String, ForeignKey("assets.asset_id"), nullable=False)
    alert_type = Column(String)
    condition_json = Column(Text)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_triggered = Column(DateTime)

    user = relationship("User", back_populates="alerts")
    asset = relationship("Asset", back_populates="alerts")
