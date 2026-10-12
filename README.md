# AI/ML Stock Market Analysis Dashboard

## MarketLens

This is my stock market analysis dashboard. The idea is simple: enter a stock you're interested in and explore its performance without having to go through rows of data.

You can look at price history, compare stocks, save a watchlist, and try a basic forecast. It uses Yahoo Finance data, so you can search for stocks beyond the ones already listed.

**[Try the website here](https://market-lens-swetha.swetha-sangeetha2809.chatgpt.site/)**

## How to use it

1. Enter a Yahoo Finance ticker, like `AAPL`, `TSLA`, or `RELIANCE.NS`.
2. Click **Analyze stock**.
3. Explore the charts, change the time range, and check the trend and volatility.
4. Compare it with other stocks or add it to your watchlist.

Use the ticker symbol rather than the company name. For stocks outside the US, you may need the exchange suffix—for example, `.NS` for an NSE-listed stock.

## What's included so far

- Stock price charts with different time ranges.
- A 10-session moving average, period highs and lows, and daily volatility.
- Comparisons for up to three stocks.
- A watchlist saved in your browser.
- CSV downloads of the comparison data.
- Market index snapshots.
- A simple forecast for 7, 14, or 30 trading sessions.

Prices are shown in each stock's original currency. Yahoo quotes can be delayed, and the data is cached for five minutes.

## About the prediction part

This part is still basic. It uses linear regression on the last 30 trading observations to project the recent trend forward.

It isn't an advanced AI model, and I don't want to present it as one. The range shown with the forecast is experimental, not a reliable confidence interval. A stock also needs at least 30 observations for the analysis to work.

The next step is to test the forecasts properly, compare them with a simple baseline, and see where they fail before adding more models.

## Built with

HTML, CSS, JavaScript, and a small server that fetches data from Yahoo Finance. The hosted version runs as a Cloudflare-compatible Worker.

## Run it locally

You'll need **Node.js 22 or newer**.

```bash
git clone https://github.com/ssrid111/AI-ML-stock-market-analysis-dashboard.git
cd AI-ML-stock-market-analysis-dashboard
npm start
```

Then open **http://127.0.0.1:8000**.

There are no packages to install or API keys to enter. Start the server instead of opening the HTML file directly—the Yahoo connection needs it.

To build or run the tests:

```bash
npm run build
npm test
```

## Finding your way around the code

- `public/` — the dashboard's HTML, CSS, and JavaScript.
- `worker/` — the Yahoo Finance connection and server routes.
- `scripts/` — the build script and local server.
- `tests/` — checks for data handling, caching, and errors.

Make dashboard changes in `public/`. The files at the repository root are copies for easy viewing. GitHub Pages by itself won't run the server, and pushing to GitHub doesn't automatically update the hosted website.

## What I'd like to add next

- Volume charts and more technical indicators.
- Proper backtesting with chronological training and testing splits.
- Model comparisons using MAE and RMSE.
- A better way to search by company name.

## A quick note

This is a research and learning project, not an investment tool. Yahoo's unofficial endpoint can change or stop responding, and daily prices are unadjusted for corporate actions. Use the data for personal research and check Yahoo's terms before redistributing it.

Please don't make investment decisions based on the forecasts.

No license has been added yet.
