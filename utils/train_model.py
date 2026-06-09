"""
Standalone training script.
Usage:
    python -m utils.train_model
This is useful for CI, MLOps demos, or when you update historical data.
"""
import logging

from .ml_model import train_and_save_model

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    model, acc = train_and_save_model()
    logger.info("Model trained via standalone script")
    print("✅ Model trained and saved to data/wc2026_model.joblib")
    print(f"   Validation accuracy: {acc}")
