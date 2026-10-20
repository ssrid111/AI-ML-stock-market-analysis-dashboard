# MarketLens v2 — SwiftUI

This is the native iPhone and iPad version of my stock analysis project. I wanted the same idea—pick a ticker and understand its performance—in an interface built around SwiftUI and Swift Charts.

## What's here

- Native ticker search with live Yahoo Finance history.
- Interactive 1-month, 3-month, and 1-year chart ranges.
- Period returns, highs, lows, and daily volatility.
- A watchlist stored on the device using AppStorage.
- Loading states, errors, and a settings screen.
- A client for the Python backend's Random Forest, Gradient Boosting, and Ridge forecasts, including MAE/RMSE and baseline comparisons.

Charts work directly with Yahoo. ML forecasts require the deployed Python service; add its HTTPS address in the app's **Settings**. The Python service is prepared for Render in the `main` branch. The app does not run scikit-learn on-device or claim to use Core ML.

## Open in Xcode

1. Open `MarketLens.xcodeproj`.
2. Select the MarketLens scheme and an iPhone simulator.
3. Build and run. The project targets iOS 17 and newer, for iPhone and iPad.
4. For a physical device, select your own signing team and a unique bundle identifier.

No third-party Swift dependencies are required.

## Core checks

From the repository root:

```bash
swiftc ios/MarketLens/Models.swift ios/CoreChecks.swift -o /tmp/marketlens-checks
/tmp/marketlens-checks
```

The unsigned iOS simulator target compiled with Xcode. Core checks cover period returns, extrema, and volatility. Simulator interaction testing is still needed: the development machine's installed simulator runtime was older than its Xcode SDK.

## Before an App Store release

This version is source code, not an App Store release. It still needs device testing, an app icon, screenshots, a privacy policy, an Apple Developer signing team, a working Python service for ML, and App Store review. Yahoo data may be delayed or unavailable; forecasts are for education, not investment advice.

Portfolio source: https://github.com/ssrid111/AI-ML-stock-market-analysis-dashboard/tree/swiftui-v2/ios
