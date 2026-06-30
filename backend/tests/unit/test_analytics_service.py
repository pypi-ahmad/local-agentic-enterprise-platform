from app.services.analytics_service import AnalyticsService


def test_analytics_summary_shape() -> None:
    summary = AnalyticsService.summarize([1, 2, 3, 10, 5, 6])
    assert isinstance(summary.average, float)
    assert isinstance(summary.trend_slope, float)
    assert isinstance(summary.anomalies, list)
