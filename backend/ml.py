"""Causal features and direct-horizon forecasts with a purged chronological holdout."""
from datetime import datetime, timezone
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ALGORITHMS = {
    'random_forest': 'Random Forest',
    'gradient_boosting': 'Gradient Boosting',
    'ridge': 'Ridge Regression',
}
FEATURE_NAMES = ['return_1', 'return_2', 'return_3', 'return_4', 'return_5',
                 'return_5_sessions', 'return_10_sessions', 'return_20_sessions',
                 'price_to_ma5', 'price_to_ma20', 'volatility_20', 'volume_to_mean20']


def estimator(name):
    if name == 'random_forest':
        return RandomForestRegressor(n_estimators=80, max_depth=6, min_samples_leaf=5,
                                     random_state=42, n_jobs=1)
    if name == 'gradient_boosting':
        return GradientBoostingRegressor(n_estimators=80, max_depth=2,
                                        min_samples_leaf=5, learning_rate=0.04,
                                        random_state=42, loss='huber')
    return make_pipeline(StandardScaler(), Ridge(alpha=10.0))


def features_at(prices, volumes, i):
    """Only uses observations through i; no future prices or fitted global scalers."""
    log_prices = np.log(prices)
    recent_returns = np.diff(log_prices[i-20:i+1])
    volume_window = volumes[i-19:i+1]
    volume_mean = float(np.mean(volume_window))
    return np.array([
        *[log_prices[i-j] - log_prices[i-j-1] for j in range(5)],
        *[log_prices[i] - log_prices[i-j] for j in [5, 10, 20]],
        prices[i] / np.mean(prices[i-4:i+1]) - 1,
        prices[i] / np.mean(prices[i-19:i+1]) - 1,
        np.std(recent_returns),
        volumes[i] / volume_mean - 1 if volume_mean > 0 else 0,
    ], dtype=float)


def dataset(points, horizon):
    prices = np.array([p.get('adjustedClose', p['close']) for p in points], dtype=float)
    volumes = np.array([p.get('volume') or 0 for p in points], dtype=float)
    if len(prices) < 160 or not np.isfinite(prices).all() or (prices <= 0).any():
        raise ValueError('At least 160 valid daily observations are needed for ML evaluation.')
    origins = np.arange(20, len(prices) - horizon)
    x = np.array([features_at(prices, volumes, i) for i in origins])
    y = np.log(prices[origins+horizon] / prices[origins])
    return prices, volumes, origins, x, y


def split_positions(origins, horizon):
    split = int(len(origins) * 0.8)
    test = np.arange(split, len(origins))
    # No training label is allowed to reach the first test observation.
    train = np.flatnonzero(origins + horizon < origins[split])
    if len(train) < 50 or len(test) < 20:
        raise ValueError('Not enough history for an independent chronological holdout.')
    return train, test


def evaluate_and_forecast(stock, horizon):
    if horizon not in (7, 14, 30):
        raise ValueError('Choose a horizon of 7, 14, or 30 trading sessions.')
    points = stock['points']
    prices, volumes, origins, x, y = dataset(points, horizon)
    train, test = split_positions(origins, horizon)
    origin_prices = prices[origins[test]]
    actual_prices = prices[origins[test] + horizon]
    latest_features = features_at(prices, volumes, len(prices)-1).reshape(1, -1)
    # Convert adjusted-price predictions into the latest raw-price denomination.
    scale = points[-1]['close'] / prices[-1]
    baseline_mae = float(mean_absolute_error(actual_prices, origin_prices) * scale)
    baseline_rmse = float(np.sqrt(mean_squared_error(actual_prices, origin_prices)) * scale)
    models = []
    for key, name in ALGORITHMS.items():
        model = estimator(key)
        model.fit(x[train], y[train])
        prediction = model.predict(x[test])
        predicted_prices = origin_prices * np.exp(prediction)
        mae = float(mean_absolute_error(actual_prices, predicted_prices) * scale)
        rmse = float(np.sqrt(mean_squared_error(actual_prices, predicted_prices)) * scale)
        # Refit only after the holdout metrics have been measured.
        model.fit(x, y)
        future_return = float(model.predict(latest_features)[0])
        forecast = float(points[-1]['close'] * np.exp(future_return))
        if not np.isfinite(forecast):
            raise ValueError('The model could not produce a finite forecast.')
        models.append({'id': key, 'name': name, 'price': forecast,
                       'changePercent': float(np.expm1(future_return)*100),
                       'mae': mae, 'rmse': rmse,
                       'beatsBaseline': mae < baseline_mae})
    def date(i):
        return datetime.fromtimestamp(points[int(i)]['time']/1000, timezone.utc).date().isoformat()
    return {
        'symbol': stock['symbol'], 'currency': stock['currency'],
        'horizon': horizon, 'lastClose': points[-1]['close'],
        'lastTradingDate': date(len(points)-1), 'models': models,
        'baseline': {'name': 'No-change baseline', 'mae': baseline_mae, 'rmse': baseline_rmse},
        'evaluation': {'trainSamples': len(train), 'testSamples': len(test),
                       'gapSessions': horizon, 'trainLastTargetDate': date(origins[train[-1]]+horizon),
                       'testStartDate': date(origins[test[0]]),
                       'testEndTargetDate': date(origins[test[-1]]+horizon),
                       'strategy': 'Chronological 80/20 holdout with purged overlapping targets',
                       'overlappingTestTargets': True},
        'features': FEATURE_NAMES,
        'note': 'Experimental forecasts. Holdout targets overlap; errors are not independent. No confidence interval is claimed.',
    }
