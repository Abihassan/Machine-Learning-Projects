import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error
from sklearn.pipeline import Pipeline


def compute_trading_metrics(y_true: pd.Series, y_pred: np.ndarray, current_close: pd.Series) -> dict:
    """
    Calculates RMSE, MAE, MAPE, and Directional Trading Accuracy.
    """
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred) * 100

    # Directional Accuracy: Did the algorithm correctly predict an UP or DOWN day?
    actual_direction = np.sign(y_true.values - current_close.values)
    pred_direction = np.sign(y_pred - current_close.values)

    valid_idx = actual_direction != 0
    directional_acc = np.mean(actual_direction[valid_idx] == pred_direction[valid_idx]) * 100

    return {
        "RMSE": rmse,
        "MAE": mae,
        "MAPE (%)": mape,
        "Directional Accuracy (%)": directional_acc,
    }


def extract_feature_ranking(rf_pipeline: Pipeline, feature_names: list[str]) -> pd.DataFrame:
    """Extracts Gini feature importances from a trained Random Forest Pipeline."""
    rf_model = rf_pipeline.named_steps["model"]
    importances = rf_model.feature_importances_
    df = pd.DataFrame({"Feature": feature_names, "Importance": importances})
    return df.sort_values(by="Importance", ascending=False).reset_index(drop=True)