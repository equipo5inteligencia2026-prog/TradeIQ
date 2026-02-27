import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
import xgboost as xgb
import logging

logger = logging.getLogger(__name__)

class PricePredictor:
    """Base class for price prediction models"""

    def __init__(self, lookback_window: int = 60):
        self.lookback_window = lookback_window
        self.scaler = MinMaxScaler()
        self.model = None

    def prepare_features(self, df: pd.DataFrame) -> tuple:
        """
        Prepare features for modeling

        Args:
            df: DataFrame with technical indicators

        Returns:
            Tuple of (X, y) arrays
        """
        try:
            # Select features
            feature_cols = ['close', 'volume', 'rsi', 'macd', 'bb_upper', 'bb_lower',
                           'sma20', 'sma50', 'atr', 'stoch_k']

            # Use only available columns
            available_cols = [col for col in feature_cols if col in df.columns]
            df_features = df[available_cols].fillna(method='bfill')

            # Normalize features
            X = self.scaler.fit_transform(df_features)

            # Create sequences
            X_seq = []
            y_seq = []

            for i in range(len(X) - self.lookback_window):
                X_seq.append(X[i:i + self.lookback_window])
                y_seq.append(1 if df['close'].iloc[i + self.lookback_window] > df['close'].iloc[i + self.lookback_window - 1] else 0)

            return np.array(X_seq), np.array(y_seq)

        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return np.array([]), np.array([])

    def train(self, X, y):
        """Train the model"""
        raise NotImplementedError("Subclasses must implement train()")

    def predict(self, X) -> np.ndarray:
        """Make predictions"""
        raise NotImplementedError("Subclasses must implement predict()")

    def predict_trend(self, X) -> dict:
        """Predict trend (ALZA/BAJA) with confidence"""
        raise NotImplementedError("Subclasses must implement predict_trend()")


class NeuralNetPredictor(PricePredictor):
    """Neural Network (MLP) for price prediction"""

    def __init__(self, lookback_window: int = 60):
        super().__init__(lookback_window)
        self.model = MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=100, random_state=42, early_stopping=True)

    def train(self, X, y):
        """Train Neural Network model"""
        try:
            X_flat = X.reshape(X.shape[0], -1)
            self.model.fit(X_flat, y)
            logger.info("Neural Network model trained successfully")
        except Exception as e:
            logger.error(f"Error training Neural Network: {e}")

    def predict(self, X) -> np.ndarray:
        """Make predictions"""
        try:
            X_flat = X.reshape(X.shape[0], -1)
            return self.model.predict_proba(X_flat)[:, 1]
        except Exception as e:
            logger.error(f"Error predicting with Neural Network: {e}")
            return np.array([])

    def predict_trend(self, X) -> dict:
        """Predict trend with confidence"""
        try:
            if len(X) == 0:
                return {"trend": "HOLD", "confidence": 0.5, "model": "Neural Network"}

            predictions = self.predict(X)
            if len(predictions) == 0:
                logger.warning("No predictions returned from model")
                return {"trend": "HOLD", "confidence": 0.5, "model": "Neural Network"}

            confidence = float(np.mean(predictions))
            confidence = np.clip(confidence, 0.0, 1.0)
            trend = "ALZA" if confidence > 0.5 else "BAJA"

            return {
                "trend": trend,
                "confidence": confidence,
                "model": "Neural Network"
            }
        except Exception as e:
            logger.error(f"Error predicting trend with NN: {e}")
            return {"trend": "HOLD", "confidence": 0.5, "model": "Neural Network"}


class RandomForestPredictor(PricePredictor):
    """Random Forest for price prediction"""

    def __init__(self, lookback_window: int = 60):
        super().__init__(lookback_window)
        self.model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)

    def train(self, X, y):
        """Train Random Forest model"""
        try:
            # Flatten sequences for RF
            X_flat = X.reshape(X.shape[0], -1)
            self.model.fit(X_flat, y)
            logger.info("Random Forest model trained successfully")
        except Exception as e:
            logger.error(f"Error training Random Forest: {e}")

    def predict(self, X) -> np.ndarray:
        """Make predictions"""
        try:
            X_flat = X.reshape(X.shape[0], -1)
            return self.model.predict_proba(X_flat)[:, 1]
        except Exception as e:
            logger.error(f"Error predicting with Random Forest: {e}")
            return np.array([])

    def predict_trend(self, X) -> dict:
        """Predict trend with confidence"""
        try:
            if len(X) == 0:
                return {"trend": "HOLD", "confidence": 0.5, "model": "Random Forest"}

            predictions = self.predict(X)
            if len(predictions) == 0:
                logger.warning("No predictions returned from model")
                return {"trend": "HOLD", "confidence": 0.5, "model": "Random Forest"}

            confidence = float(np.mean(predictions))
            confidence = np.clip(confidence, 0.0, 1.0)
            trend = "ALZA" if confidence > 0.5 else "BAJA"

            return {
                "trend": trend,
                "confidence": confidence,
                "model": "Random Forest"
            }
        except Exception as e:
            logger.error(f"Error predicting trend with RF: {e}")
            return {"trend": "HOLD", "confidence": 0.5, "model": "Random Forest"}


class GradientBoostPredictor(PricePredictor):
    """Gradient Boosting for price prediction"""

    def __init__(self, lookback_window: int = 60):
        super().__init__(lookback_window)
        self.model = GradientBoostingClassifier(n_estimators=100, random_state=42)

    def train(self, X, y):
        """Train Gradient Boosting model"""
        try:
            X_flat = X.reshape(X.shape[0], -1)
            self.model.fit(X_flat, y)
            logger.info("Gradient Boosting model trained successfully")
        except Exception as e:
            logger.error(f"Error training Gradient Boosting: {e}")

    def predict(self, X) -> np.ndarray:
        """Make predictions"""
        try:
            X_flat = X.reshape(X.shape[0], -1)
            return self.model.predict_proba(X_flat)[:, 1]
        except Exception as e:
            logger.error(f"Error predicting with Gradient Boosting: {e}")
            return np.array([])

    def predict_trend(self, X) -> dict:
        """Predict trend with confidence"""
        try:
            if len(X) == 0:
                return {"trend": "HOLD", "confidence": 0.0}

            predictions = self.predict(X)
            confidence = np.mean(predictions)
            trend = "ALZA" if confidence > 0.5 else "BAJA"

            return {
                "trend": trend,
                "confidence": float(confidence),
                "model": "Gradient Boosting"
            }
        except Exception as e:
            logger.error(f"Error predicting trend with GB: {e}")
            return {"trend": "HOLD", "confidence": 0.0, "model": "Gradient Boosting"}


class XGBoostPredictor(PricePredictor):
    """XGBoost for price prediction"""

    def __init__(self, lookback_window: int = 60):
        super().__init__(lookback_window)
        self.model = xgb.XGBClassifier(n_estimators=100, random_state=42, n_jobs=-1)

    def train(self, X, y):
        """Train XGBoost model"""
        try:
            X_flat = X.reshape(X.shape[0], -1)
            self.model.fit(X_flat, y)
            logger.info("XGBoost model trained successfully")
        except Exception as e:
            logger.error(f"Error training XGBoost: {e}")

    def predict(self, X) -> np.ndarray:
        """Make predictions"""
        try:
            X_flat = X.reshape(X.shape[0], -1)
            return self.model.predict_proba(X_flat)[:, 1]
        except Exception as e:
            logger.error(f"Error predicting with XGBoost: {e}")
            return np.array([])

    def predict_trend(self, X) -> dict:
        """Predict trend with confidence"""
        try:
            if len(X) == 0:
                return {"trend": "HOLD", "confidence": 0.5, "model": "XGBoost"}

            predictions = self.predict(X)
            if len(predictions) == 0:
                logger.warning("No predictions returned from model")
                return {"trend": "HOLD", "confidence": 0.5, "model": "XGBoost"}

            confidence = float(np.mean(predictions))
            confidence = np.clip(confidence, 0.0, 1.0)
            trend = "ALZA" if confidence > 0.5 else "BAJA"

            return {
                "trend": trend,
                "confidence": confidence,
                "model": "XGBoost"
            }
        except Exception as e:
            logger.error(f"Error predicting trend with XGBoost: {e}")
            return {"trend": "HOLD", "confidence": 0.5, "model": "XGBoost"}


class SVMPredictor(PricePredictor):
    """Support Vector Machine for price prediction"""

    def __init__(self, lookback_window: int = 60):
        super().__init__(lookback_window)
        self.model = SVC(kernel='rbf', probability=True, random_state=42)

    def train(self, X, y):
        """Train SVM model"""
        try:
            X_flat = X.reshape(X.shape[0], -1)
            self.model.fit(X_flat, y)
            logger.info("SVM model trained successfully")
        except Exception as e:
            logger.error(f"Error training SVM: {e}")

    def predict(self, X) -> np.ndarray:
        """Make predictions"""
        try:
            X_flat = X.reshape(X.shape[0], -1)
            return self.model.predict_proba(X_flat)[:, 1]
        except Exception as e:
            logger.error(f"Error predicting with SVM: {e}")
            return np.array([])

    def predict_trend(self, X) -> dict:
        """Predict trend with confidence"""
        try:
            if len(X) == 0:
                return {"trend": "HOLD", "confidence": 0.5, "model": "SVM"}

            predictions = self.predict(X)
            if len(predictions) == 0:
                logger.warning("No predictions returned from model")
                return {"trend": "HOLD", "confidence": 0.5, "model": "SVM"}

            confidence = float(np.mean(predictions))
            confidence = np.clip(confidence, 0.0, 1.0)
            trend = "ALZA" if confidence > 0.5 else "BAJA"

            return {
                "trend": trend,
                "confidence": confidence,
                "model": "SVM"
            }
        except Exception as e:
            logger.error(f"Error predicting trend with SVM: {e}")
            return {"trend": "HOLD", "confidence": 0.5, "model": "SVM"}
