# AI/ML Stock Market Analysis Dashboard

**MarketLens** connects a responsive stock dashboard to Yahoo Finance price history through a small JavaScript server.

## Features

- Enter any supported Yahoo Finance stock ticker to analyze it, such as TSLA, BRK-B, or RELIANCE.NS.
- Latest available quotes and one year of daily history, with prices displayed in the stock’s original currency.
- Default AAPL, MSFT, NVDA, GOOGL, and AMZN shortcuts.
- S&P 500, Nasdaq Composite, Dow Jones, and VIX snapshots.
- Calendar date ranges, actual trading dates, 10-session moving averages, period highs/lows, and daily volatility.
- Normalized stock comparisons aligned on shared trading dates.
- Browser watchlist and CSV export.
- Experimental linear trend forecasts for 7, 14, and 30 trading sessions.
- Loading states, partial-data errors, manual refresh, and a five-minute server cache.

## Run locally

Requires Node.js 22 or later. No dependencies or API keys are required.

```bash
git clone https://github.com/ssrid111/AI-ML-stock-market-analysis-dashboard.git
cd AI-ML-stock-market-analysis-dashboard
npm start
```

Open **http://127.0.0.1:8000**. Use the server rather than opening the HTML file directly: browsers request `/api/market` from it.

```bash
npm run build
npm test
```

## Structure

```text
public/       Dashboard HTML, CSS, and JavaScript
worker/       Yahoo Finance connection and server routes
scripts/      Build and local server
tests/       Server data normalization, errors, cache, and route tests
```

The build embeds the browser assets into `dist/server/index.js`, a Cloudflare Worker-compatible ES module. The local Node server runs that same module. The root `index.html`, `style.css`, and `app.js` mirror the browser assets for easy review, but `public/` is the source used by the build. GitHub Pages alone cannot run the Yahoo server connection.

## Yahoo Finance connection

`GET /api/stock?symbol=TSLA` validates a user-entered ticker, retrieves daily Yahoo Finance history, and caches the result. Symbols use Yahoo exchange suffixes where needed (for example, RELIANCE.NS). A valid symbol must have at least 30 daily observations to support the trend model.

`GET /api/market` retrieves the default stocks and market indices from Yahoo's chart endpoint, requesting one year of daily data. Three concurrent requests limit upstream load. Responses are cached in server memory for five minutes; the cache may reset when a server instance restarts. The refresh button uses this cache until it expires.

The frontend displays when data was retrieved and the last available trading date. Quotes may be delayed; the latest available quote can differ from the latest daily chart close. Daily close prices are unadjusted and can reflect stock splits or other corporate actions.

Yahoo's endpoint is unofficial and may change, rate-limit, or become unavailable. Errors are shown explicitly; fabricated prices are never substituted. If a refresh fails, the previously fetched snapshot remains visible with an error message. This connection requires no Yahoo login and does not access a personal Yahoo portfolio.

Use this integration for personal research and review Yahoo's data-use terms before redistribution. The [yfinance project's documentation](https://github.com/ranaroussi/yfinance) also describes Yahoo Finance data as intended for personal use; this project calls Yahoo directly and does not use the Python package.

## Forecast limitations

The experimental model fits linear regression to the last 30 trading observations. Forecast horizons count trading observations, not calendar days. The displayed range uses residual variation and is not a calibrated confidence interval. This is not an AI service or a validated investment model. Chronological backtesting, a persistence baseline, and MAE/RMSE evaluation are planned.

## Hosting

The dashboard is publicly hosted at https://market-lens-swetha.swetha-sangeetha2809.chatgpt.site. Users can enter a ticker and select **Analyze stock** to load charts, indicators, and an experimental forecast. GitHub commits do not automatically deploy the hosted site.

## Disclaimer

For educational and research purposes only. Data may be delayed or inaccurate. Forecasts are not financial or investment advice.

## License

No license has been selected. Add a license file to define reuse and distribution terms.
