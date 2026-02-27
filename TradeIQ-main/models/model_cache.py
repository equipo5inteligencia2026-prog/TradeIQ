import logging
import pickle
from pathlib import Path
from models.ensemble import EnsemblePredictor
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Path for cached models
MODELS_PATH = Path(__file__).parent.parent / "models" / "trained_models"
MODELS_PATH.mkdir(exist_ok=True)

_ensemble_cache = None

def get_trained_ensemble():
    """Get or create trained ensemble (singleton with lazy loading)"""
    global _ensemble_cache

    if _ensemble_cache is not None:
        return _ensemble_cache

    try:
        # Try to load from disk
        model_file = MODELS_PATH / "ensemble_model.pkl"
        if model_file.exists():
            with open(model_file, 'rb') as f:
                _ensemble_cache = pickle.load(f)
            logger.info("Loaded pre-trained ensemble from disk")
            return _ensemble_cache
    except Exception as e:
        logger.warning(f"Could not load cached ensemble: {e}")

    # Create and train new ensemble
    logger.info("Creating new ensemble and training with dummy data...")
    _ensemble_cache = EnsemblePredictor(lookback_window=30)

    # Create proper training data for multiple samples
    # Generate 100 samples with proper feature sequences
    np.random.seed(42)
    X_train = []
    y_train = []

    for _ in range(100):
        # Create a sequence of 30 timesteps with 10 features
        sample = np.random.randn(30, 10) * 0.1 + 0.5  # Normalized to ~0.5 mean
        X_train.append(sample)
        # Random binary label
        y_train.append(np.random.randint(0, 2))

    X_train = np.array(X_train)  # Shape: (100, 30, 10)
    y_train = np.array(y_train)  # Shape: (100,)

    try:
        logger.info(f"Training ensemble with data shape X: {X_train.shape}, y: {y_train.shape}")
        _ensemble_cache.train_all(X_train, y_train)

        # Save to disk
        model_file = MODELS_PATH / "ensemble_model.pkl"
        with open(model_file, 'wb') as f:
            pickle.dump(_ensemble_cache, f)
        logger.info("Trained and cached new ensemble successfully")
    except Exception as e:
        logger.error(f"Error training ensemble: {e}")
        import traceback
        logger.error(traceback.format_exc())

    return _ensemble_cache


def clear_ensemble_cache():
    """Clear the cached ensemble"""
    global _ensemble_cache
    _ensemble_cache = None

