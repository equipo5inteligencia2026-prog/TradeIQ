import streamlit as st
from functools import wraps
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class StreamlitCache:
    """Custom cache system for Streamlit with TTL support"""

    def __init__(self):
        if "cache" not in st.session_state:
            st.session_state.cache = {}

    def get(self, key: str):
        """Get value from cache"""
        if key in st.session_state.cache:
            value, timestamp = st.session_state.cache[key]
            # Check if expired (1 hour default)
            if datetime.now() - timestamp < timedelta(hours=1):
                return value
            else:
                del st.session_state.cache[key]
        return None

    def set(self, key: str, value, ttl_seconds: int = 3600):
        """Set value in cache with TTL"""
        st.session_state.cache[key] = (value, datetime.now())

    def clear(self):
        """Clear all cache"""
        st.session_state.cache = {}

    def cached_function(self, ttl_seconds: int = 3600):
        """Decorator for caching function results"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache = StreamlitCache()
                cache_key = f"{func.__name__}_{args}_{kwargs}"

                cached_value = cache.get(cache_key)
                if cached_value is not None:
                    return cached_value

                result = func(*args, **kwargs)
                cache.set(cache_key, result, ttl_seconds)
                return result

            return wrapper
        return decorator


# Use Streamlit's built-in cache
@st.cache_data(ttl=3600)
def cached_fetch_data(symbol: str, period: str = "1y"):
    """Cache data fetching for 1 hour"""
    from utils.data_fetcher import fetch_stock_data
    return fetch_stock_data(symbol, period=period)


@st.cache_data(ttl=600)
def cached_technical_indicators(df):
    """Cache technical indicator calculations for 10 minutes"""
    from utils.technical_analysis import add_technical_indicators
    return add_technical_indicators(df)


def clear_cache():
    """Clear Streamlit cache"""
    st.cache_data.clear()
