# MarketLens — SwiftUI v2

This branch adds a native iPhone and iPad app to my stock market dashboard project. It uses SwiftUI for the interface, Swift Charts for price history, and a small Swift service for Yahoo Finance requests.

## Versions

| Version | Where to find it |
| --- | --- |
| Web dashboard + Python ML backend | [main branch](https://github.com/ssrid111/AI-ML-stock-market-analysis-dashboard/tree/main) |
| Native iOS app | This `swiftui-v2` branch, inside `ios/` |

The existing web and Python source is preserved on this branch too.

## Try the iOS project

Open **ios/MarketLens.xcodeproj** in Xcode, choose an iPhone simulator, and run the MarketLens scheme. It targets iOS 17+, with no third-party Swift dependencies.

You can search Yahoo tickers, explore native charts, change the date range, and save a watchlist. To compare Python ML forecasts, deploy the backend from `main` to Render and enter its HTTPS URL in the app's Settings.

See [the iOS README](ios/README.md) for build instructions, checks, and release limitations.

## Status

The iOS simulator target compiles and the Swift calculation checks pass. Simulator interaction testing is unverified because the development machine's simulator runtime and Xcode SDK don't match. This is a portfolio project in development, not an App Store release.

The existing [web dashboard](https://market-lens-swetha.swetha-sangeetha2809.chatgpt.site/) remains available separately. Yahoo data may be delayed; experimental predictions are not investment advice.
