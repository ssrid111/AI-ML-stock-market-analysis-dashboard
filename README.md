# AI/ML Stock Market Analysis Dashboard

## MarketLens

This is my stock market analysis dashboard. Enter a stock you're interested in, explore its performance, and compare what different ML models predict.

The backend now uses **Python, FastAPI, and scikit-learn**. The dashboard still uses HTML, CSS, and JavaScript for the charts and controls.

## Try it

The [existing public website](https://market-lens-swetha.swetha-sangeetha2809.chatgpt.site/) is still the earlier JavaScript version. **The Python ML version is ready for Render, but hasn't been deployed there yet.**

[Deploy the Python version on Render](https://render.com/deploy?repo=https://github.com/ssrid111/AI-ML-stock-market-analysis-dashboard)

## What you can do

- Enter a Yahoo ticker, like `TSLA`, `AAPL`, or `RELIANCE.NS`.
- Explore price charts, moving averages, returns, and volatility.
- Compare up to three stocks and download the comparison as a CSV.
- Save a watchlist in your browser.
- Choose Random Forest, Gradient Boosting, or Ridge Regression for a forecast.
- Compare each model's MAE and RMSE with a simple no-change baseline.

Prices stay in the stock's original currency. Yahoo quotes may be delayed, and fetched history is cached for five minutes. The latest daily observation can be incomplete while its market is open.

## About the ML part

The models use daily return lags, recent returns, moving-average ratios, volatility, and relative volume. They learn from up to two years of Yahoo history and predict the return over 7, 14, or 30 trading sessions.

The latest 20% of labeled observations are kept for testing. There is also a gap before that test period so training targets don't overlap it. The models are evaluated first, then refitted on all available labeled history to make the next forecast.

**Lower MAE and RMSE are better, but an ML model isn't automatically better than doing nothing.** The dashboard shows when a model fails to beat the baseline. Test targets overlap, so the errors aren't independent, and this isn't a trading-strategy backtest.

At least 160 daily observations are required for ML evaluation. Adjusted closes are used where Yahoo provides them; charts show raw closes. Forecast prices and errors are converted to the latest raw-price denomination. No confidence interval is claimed.

## Run it locally

You'll need **Python 3.12**.

```bash
git clone https://github.com/ssrid111/AI-ML-stock-market-analysis-dashboard.git
cd AI-ML-stock-market-analysis-dashboard
python -m venv .venv
```

Activate the environment:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Then install and start:

```bash
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload --port 8000
```

Open **http://127.0.0.1:8000**. No Yahoo API key is needed.

Run the Python checks with:

```bash
python -m unittest discover -s python_tests -v
```

## Deploy on Render

1. Open the **Deploy the Python version on Render** link above and sign in.
2. Connect this GitHub repository if Render asks for it.
3. Review the service created from `render.yaml` and deploy it.
4. Open the `onrender.com` URL that Render gives you.

The same Python service serves both the dashboard and its API, so there's no separate frontend URL to configure. The Blueprint specifies the free plan; check Render's current terms and limits before deploying. Free services can take time to wake up after being idle.

If you're setting up a web service manually:

- **Runtime:** Python
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT --workers 1`
- **Health check:** `/health`

## Finding your way around the code

- `backend/main.py` — Yahoo data, API routes, caching, and the web server.
- `backend/ml.py` — features, models, evaluation, and forecasts.
- `public/` — the dashboard interface.
- `python_tests/` — checks for model evaluation and API behavior.
- `render.yaml` — Render hosting configuration.

Make interface changes in `public/`; the root HTML, CSS, and JavaScript files are copies for easy viewing. The older `worker/`, `scripts/`, and JavaScript tests remain as reference for the original Sites deployment. They aren't used by the Python service.

## What I'd like to add next

- Walk-forward evaluation across more market conditions.
- More technical indicators and volume charts.
- Better company-name search.
- Model tuning using a separate validation period.

## A quick note

This is a research and learning project, not an investment tool. Yahoo's unofficial endpoint can change or stop responding. Use the data for personal research and check Yahoo's terms before redistributing it.

Please don't make investment decisions based on the forecasts.

No license has been added yet.
