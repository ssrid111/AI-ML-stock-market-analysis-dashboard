# MarketLens — Stock Market Analysis Dashboard

This is my stock market analysis project. You can enter a stock ticker, explore its price history, compare it with other stocks, and see how different machine learning models perform.

The backend uses **Python, FastAPI, and scikit-learn**, with **HTML, CSS, and JavaScript** for the dashboard.

## Project Versions

- **Web + Python ML:** Available on the `main` branch.
- **Native iOS app:** Available on the [`swiftui-v2` branch](https://github.com/ssrid111/AI-ML-stock-market-analysis-dashboard/tree/swiftui-v2), built with SwiftUI and Swift Charts.

## Try It

[Open the public web dashboard](https://market-lens-swetha.swetha-sangeetha2809.chatgpt.site/)

The public website currently runs the earlier JavaScript version. The Python ML version is included in this repository and prepared for deployment on Render.

[Deploy the Python version on Render](https://render.com/deploy?repo=https://github.com/ssrid111/AI-ML-stock-market-analysis-dashboard)

## What You Can Do

- Search using Yahoo Finance tickers such as `AAPL`, `TSLA`, or `RELIANCE.NS`.
- Explore price charts, moving averages, returns, and volatility.
- Compare up to three stocks.
- Save a watchlist in your browser.
- Download stock comparisons as CSV files.
- Compare forecasts from Random Forest, Gradient Boosting, and Ridge Regression.
- Check each model’s MAE and RMSE against a no-change baseline.

Prices are displayed in each stock’s original currency. Yahoo quotes may be delayed, and fetched data is cached for five minutes.

## How the ML Works

The models use features based on past prices and volume, including:

- Daily return lags.
- Returns over 5, 10, and 20 trading sessions.
- Moving-average ratios.
- Rolling volatility.
- Relative trading volume.

They use up to two years of Yahoo Finance history to predict returns over **7, 14, or 30 trading sessions**.

The latest 20% of labeled observations are reserved for testing. Training observations whose targets overlap the test period are removed. After evaluation, each model is refitted on the available labeled history to generate a forecast.

The dashboard reports:

- **MAE:** Mean Absolute Error.
- **RMSE:** Root Mean Squared Error.
- **Baseline comparison:** Whether the model performs better than predicting no price change.

Lower errors are better, but a machine learning model does not always beat the baseline. Test targets overlap, so their errors are not independent. This evaluation is not a trading-strategy backtest.

At least **160 daily observations** are required. Models use adjusted closing prices where available, while charts show raw closing prices. Forecasts and errors are converted to the latest raw-price denomination.

## Run Locally

You’ll need **Python 3.12**.

### 1. Clone the repository

```bash
git clone https://github.com/ssrid111/AI-ML-stock-market-analysis-dashboard.git
cd AI-ML-stock-market-analysis-dashboard
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Or on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the app

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

Open **http://127.0.0.1:8000** in your browser.

No Yahoo API key is required.

### Run the tests

```bash
python -m unittest discover -s python_tests -v
```

## Deploy on Render

1. Open the deployment link above and sign in to Render.
2. Connect this GitHub repository if prompted.
3. Review the configuration from `render.yaml`.
4. Deploy the service and open the URL Render provides.

The Python service serves both the dashboard and its API.

For manual setup, use:

| Setting | Value |
| --- | --- |
| Runtime | Python |
| Build command | `pip install -r requirements.txt` |
| Start command | `uvicorn backend.main:app --host 0.0.0.0 --port $PORT --workers 1` |
| Health check | `/health` |

The Blueprint specifies the free plan. Review the plan’s current limits before deploying.

## Project Structure

```text
backend/
├── main.py          # API routes, Yahoo data, caching, and server
└── ml.py            # Features, models, evaluation, and forecasts

public/              # Dashboard HTML, CSS, and JavaScript
python_tests/        # Python tests
requirements.txt     # Python dependencies
render.yaml          # Render deployment configuration
```

Make dashboard changes in `public/`. The HTML, CSS, and JavaScript files at the repository root are copies for easy viewing.

The older `worker/`, `scripts/`, and JavaScript tests belong to the original Sites deployment and are not used by the Python service.

## SwiftUI Version

The native iOS version includes ticker search, price charts, period statistics, and a watchlist stored on the device.

To explore it:

1. Switch to the `swiftui-v2` branch.
2. Open `ios/MarketLens.xcodeproj` in Xcode.
3. Select the MarketLens scheme and an iPhone simulator.
4. Build and run.

ML forecasts require the deployed Python backend’s HTTPS URL in the app’s Settings.

The iOS project targets **iOS 17 and newer**. It is still in development and has not been published to the App Store.

## What I’d Like to Add Next

- Walk-forward evaluation across different market conditions.
- More technical indicators and volume charts.
- Search by company name.
- Model tuning with a separate validation period.

## Limitations

Yahoo Finance’s unofficial endpoint may change, rate-limit requests, or become unavailable. Quotes may be delayed, and the latest daily observation may be incomplete while the market is open.

The forecasts are experimental, and no confidence interval is claimed.

## Disclaimer

This is a research and learning project, not an investment tool. Please don’t make investment decisions based on its forecasts.

Use market data for personal research and review Yahoo’s terms before redistributing it.

## License

No license has been added yet.
