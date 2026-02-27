import numpy as np
import pandas as pd
from models.prediction import NeuralNetPredictor, RandomForestPredictor, XGBoostPredictor, SVMPredictor
import logging

logger = logging.getLogger(__name__)

class EnsemblePredictor:
    """Ensemble of multiple predictors for robust stock predictions"""

    def __init__(self, lookback_window: int = 30):
        self.lookback_window = lookback_window
        self.models = {
            'neural_network': NeuralNetPredictor(lookback_window),
            'random_forest': RandomForestPredictor(lookback_window),
            'xgboost': XGBoostPredictor(lookback_window),
            'svm': SVMPredictor(lookback_window)
        }
        self.model_results = {}
        self.is_trained = False

    def train_all(self, X_train, y_train):
        """Train all models"""
        try:
            if len(X_train) == 0 or len(y_train) == 0:
                logger.warning("Empty training data provided")
                return

            logger.info(f"Starting training with X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")

            for model_name, model in self.models.items():
                logger.info(f"Training {model_name}...")
                try:
                    model.train(X_train, y_train)
                    logger.info(f"✓ {model_name} trained successfully")
                except Exception as e:
                    logger.error(f"✗ Error training {model_name}: {e}")
                    import traceback
                    logger.error(traceback.format_exc())

            self.is_trained = True
            logger.info("All models trained successfully")
        except Exception as e:
            logger.error(f"Error training ensemble: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def predict_individual(self, X) -> dict:
        """Get predictions from individual models with fallback"""
        predictions = {}

        if len(X) == 0:
            # Return default predictions if no data
            for model_name in self.models.keys():
                predictions[model_name] = {
                    "trend": "HOLD",
                    "confidence": 0.5,
                    "model": model_name.replace("_", " ").title()
                }
            return predictions

        for model_name, model in self.models.items():
            try:
                result = model.predict_trend(X)
                predictions[model_name] = result
                self.model_results[model_name] = result
            except Exception as e:
                logger.warning(f"Model {model_name} prediction failed: {e}")
                # Fallback to HOLD prediction
                predictions[model_name] = {
                    "trend": "HOLD",
                    "confidence": 0.5,
                    "model": model_name.replace("_", " ").title()
                }

        return predictions

    def ensemble_prediction(self, X) -> dict:
        """Get ensemble prediction using voting mechanism"""
        try:
            individual_predictions = self.predict_individual(X)

            if not individual_predictions:
                return {
                    "trend": "HOLD",
                    "confidence": 0.5,
                    "consensus": 0.5,
                    "num_models": 0,
                    "predictions": {}
                }

            # Count votes
            alza_count = 0
            confidence_scores = []

            for prediction in individual_predictions.values():
                if prediction.get("trend") == "ALZA":
                    alza_count += 1
                conf = prediction.get("confidence", 0.5)
                confidence_scores.append(conf)

            # Determine ensemble trend
            num_models = len(individual_predictions)
            consensus = alza_count / num_models if num_models > 0 else 0.5
            avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.5

            # Ensure valid values
            avg_confidence = float(np.clip(avg_confidence, 0.0, 1.0))
            consensus = float(np.clip(consensus, 0.0, 1.0))

            # Final decision
            if consensus > 0.6:
                final_trend = "ALZA"
            elif consensus < 0.4:
                final_trend = "BAJA"
            else:
                final_trend = "HOLD"

            return {
                "trend": final_trend,
                "confidence": avg_confidence,
                "consensus": consensus,
                "num_models": num_models,
                "alza_votes": alza_count,
                "predictions": individual_predictions
            }

        except Exception as e:
            logger.error(f"Error in ensemble prediction: {e}")
            return {
                "trend": "HOLD",
                "confidence": 0.5,
                "consensus": 0.5,
                "num_models": 0,
                "predictions": {}
            }

    def get_price_target(self, X, current_price: float, horizon_days: int = 30) -> dict:
        """
        Calculate price target based on ensemble predictions
        """
        try:
            if current_price <= 0:
                current_price = 100.0  # Default fallback price

            ensemble = self.ensemble_prediction(X)
            confidence = np.clip(ensemble.get("confidence", 0.5), 0.0, 1.0)

            # Estimate price movement based on confidence
            if ensemble["trend"] == "ALZA":
                estimated_change = (confidence - 0.5) * 0.1
                target_price = current_price * (1 + estimated_change)
            elif ensemble["trend"] == "BAJA":
                estimated_change = -(0.5 - confidence) * 0.1
                target_price = current_price * (1 + estimated_change)
            else:
                target_price = current_price

            # Calculate confidence intervals
            upper_bound = target_price * (1 + confidence * 0.05)
            lower_bound = max(0.01, target_price * (1 - confidence * 0.05))

            return {
                "target_price": round(float(target_price), 2),
                "upper_bound": round(float(upper_bound), 2),
                "lower_bound": round(float(lower_bound), 2),
                "confidence": float(confidence),
                "trend": ensemble["trend"],
                "horizon_days": horizon_days
            }

        except Exception as e:
            logger.error(f"Error calculating price target: {e}")
            return {
                "target_price": float(current_price),
                "upper_bound": float(current_price * 1.05),
                "lower_bound": float(current_price * 0.95),
                "confidence": 0.5,
                "trend": "HOLD",
                "horizon_days": horizon_days
            }

    def get_model_performance(self) -> pd.DataFrame:
        """Get performance summary of all models"""
        try:
            data = []
            for model_name, result in self.model_results.items():
                data.append({
                    "Model": model_name.replace("_", " ").title(),
                    "Prediction": result.get("trend", "N/A"),
                    "Confidence": f"{result.get('confidence', 0.5)*100:.1f}%"
                })

            if data:
                return pd.DataFrame(data)
            else:
                return pd.DataFrame({
                    "Model": ["No Data"],
                    "Prediction": ["N/A"],
                    "Confidence": ["N/A"]
                })

        except Exception as e:
            logger.error(f"Error getting model performance: {e}")
            return pd.DataFrame()
