# AI/ML Stock Market Analysis Dashboard

**MarketLens** is a responsive stock research dashboard built with HTML, CSS, and JavaScript. Explore illustrative price trends, compare stocks, save a watchlist, and experiment with a simple forecast model.

## Current features

- Five selectable demo stocks: AAPL, MSFT, NVDA, GOOGL, and AMZN.
- Interactive charts with 1-week through 1-year ranges and a 10-observation moving average.
- Period highs, lows, returns, and daily volatility.
- Normalized performance comparison for up to three stocks.
- Watchlist saved locally in your browser.
- CSV export of the selected comparison.
- Linear regression forecasts for 7, 14, or 30 days.
- Responsive layouts for desktop and mobile.

## Run locally

```bash
git clone https://github.com/ssrid111/AI-ML-stock-market-analysis-dashboard.git
cd AI-ML-stock-market-analysis-dashboard
python3 -m http.server 8000
```

Open **http://localhost:8000** in your browser. No dependency installation or build step is required. You can also open `index.html` directly; browser storage behavior may differ for local files.

## Project files

```text
index.html   Dashboard structure
style.css    Responsive styles
app.js       Demo data, charts, watchlist, comparisons, and forecasts
```

Fonts are loaded from Google Fonts when internet access is available; fallback fonts work offline.

## Data and model limitations

All prices and market index values are synthetic or illustrative, not live quotes. Stock series contain 365 daily observations ending December 31, 2025; they do not follow an exchange trading calendar.

The forecast fits a linear regression to the last 30 synthetic observations and projects the trend forward. Its displayed range is based on residual variation and is **not a calibrated confidence interval**. This version has no external AI service, trained production ML model, or out-of-sample evaluation.

## Roadmap

- [x] Interactive stock dashboard and price charts.
- [x] Moving averages and stock comparisons.
- [x] Browser watchlist and CSV export.
- [x] Experimental linear trend forecast.
- [ ] Connect a real stock market data provider.
- [ ] Add volume charts and additional technical indicators.
- [ ] Evaluate models with chronological train/test splits.
- [ ] Compare forecasts against a persistence baseline using MAE and RMSE.

## Hosting

The HTML, CSS, and JavaScript can be served by any static hosting service. A separate private Sites deployment has been retained. GitHub commits do not automatically update that deployment.

## Contributing

Open an issue to report a bug or propose an improvement. Pull requests should describe the change and relevant verification.

## Disclaimer

For educational and research purposes only. Demo values and experimental forecasts are not financial or investment advice.

## License

No license has been selected. Add a license file to define permissions for reuse and distribution.
