from dataclasses import dataclass
from statistics import mean

import numpy as np
from sklearn.linear_model import LinearRegression


@dataclass(slots=True)
class AnalyticsSummary:
    average: float
    trend_slope: float
    anomalies: list[int]


class AnalyticsService:
    """Computes descriptive metrics, trend, and anomaly indices."""

    @staticmethod
    def summarize(values: list[float]) -> AnalyticsSummary:
        if not values:
            return AnalyticsSummary(average=0.0, trend_slope=0.0, anomalies=[])

        arr = np.array(values, dtype=float)
        x = np.arange(len(values)).reshape(-1, 1)
        model = LinearRegression()
        model.fit(x, arr)
        slope = float(model.coef_[0])

        avg = float(mean(values))
        std = float(np.std(arr)) if len(values) > 1 else 0.0
        threshold = 2 * std
        anomalies = [idx for idx, val in enumerate(values) if abs(val - avg) > threshold and std > 0]

        return AnalyticsSummary(average=avg, trend_slope=slope, anomalies=anomalies)
