import SwiftUI
import Charts

@main
struct MarketLensApp: App {
    var body: some Scene { WindowGroup { MarketHome() } }
}
@MainActor
final class MarketStore: ObservableObject {
    @Published var stock: Stock?
    @Published var forecast: Forecast?
    @Published var error: String?
    @Published var loading = false
    @Published var forecasting = false
    private var generation = 0
    func load(_ symbol: String) async {
        guard !loading else { return }
        generation += 1
        forecast = nil; forecasting = false; loading = true; error = nil
        defer { loading = false }
        do { stock = try await StockService().stock(symbol.trimmingCharacters(in: .whitespacesAndNewlines).uppercased()) }
        catch { self.error = error.localizedDescription }
    }
    func predict(horizon: Int, backend: String) async {
        guard let stock, !forecasting, !loading else { return }
        let ticket = generation
        forecasting = true; forecast = nil; error = nil
        do {
            let result = try await StockService().forecast(symbol: stock.symbol, horizon: horizon, backend: backend)
            guard ticket == generation else { return }
            forecast = result
        } catch { if ticket == generation { self.error = error.localizedDescription } }
        if ticket == generation { forecasting = false }
    }
    func resetForecast() { generation += 1; forecast = nil; forecasting = false }
}
struct MarketHome: View {
    @StateObject private var store = MarketStore()
    @State private var symbol = "AAPL"
    @State private var range = 90
    @State private var horizon = 7
    @State private var settings = false
    @AppStorage("mlBackend") private var backend = ""
    @AppStorage("favoriteSymbols") private var favoriteList = "AAPL,MSFT"
    private let green = Color(red: 0.08, green: 0.5, blue: 0.4)
    private var favorites: [String] { favoriteList.split(separator: ",").map(String.init) }
    private var visiblePoints: [PricePoint] {
        guard let all = store.stock?.points, let last = all.last else { return [] }
        return all.filter { $0.time >= last.time - Double(range) * 86_400_000 }
    }
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 22) {
                    Text("YOUR MARKET, IN FOCUS").font(.caption.weight(.bold)).tracking(2).foregroundStyle(green)
                    Text("Find your\nperspective.").font(.system(size: 38, weight: .bold, design: .rounded))
                    HStack {
                        TextField("Ticker, e.g. TSLA", text: $symbol).textInputAutocapitalization(.characters).autocorrectionDisabled().submitLabel(.search)
                            .onSubmit { Task { await store.load(symbol) } }
                        Button { Task { await store.load(symbol) } } label: { Image(systemName: "arrow.up.right") }.disabled(store.loading)
                    }.padding().background(.background, in: RoundedRectangle(cornerRadius: 16))
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack { ForEach(favorites, id: \.self) { code in
                            Button(code) { symbol = code; Task { await store.load(code) } }.buttonStyle(.bordered).tint(green).disabled(store.loading)
                        } }
                    }
                    if store.loading { ProgressView("Loading Yahoo Finance…").frame(maxWidth: .infinity) }
                    if let error = store.error { Text(error).font(.callout).foregroundStyle(.red).accessibilityLabel("Error: \(error)") }
                    if let stock = store.stock { stockContent(stock) }
                    Text("Yahoo quotes may be delayed. Forecasts are experimental and are not investment advice.").font(.footnote).foregroundStyle(.secondary)
                }.padding(22)
            }.background(Color(uiColor: .systemGroupedBackground))
                .navigationTitle("MarketLens").navigationBarTitleDisplayMode(.inline)
                .toolbar { Button { settings = true } label: { Image(systemName: "gearshape") }.accessibilityLabel("Settings") }
                .sheet(isPresented: $settings) { settingsView }
                .task { if store.stock == nil { await store.load(symbol) } }
                .onChange(of: horizon) { _, _ in store.resetForecast() }
        }.tint(green)
    }
    private func currency(_ value: Double, code: String) -> String {
        if code == "GBp" { return String(format: "%.2f GBp", value) }
        return value.formatted(.currency(code: code))
    }
    @ViewBuilder private func stockContent(_ stock: Stock) -> some View {
        let stats = PriceStatistics(points: visiblePoints)
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                VStack(alignment: .leading) { Text(stock.symbol).font(.title2.bold()); Text(stock.name ?? stock.symbol).font(.subheadline).foregroundStyle(.secondary) }
                Spacer()
                Button { toggleFavorite(stock.symbol) } label: { Image(systemName: favorites.contains(stock.symbol) ? "star.fill" : "star") }.accessibilityLabel("Toggle watchlist")
            }
            Text(currency(stock.price, code: stock.currency)).font(.system(size: 34, weight: .bold, design: .rounded)).minimumScaleFactor(0.6)
            Label(String(format: "%+.2f%% in selected period", stats.change), systemImage: stats.change >= 0 ? "arrow.up.right" : "arrow.down.right").foregroundStyle(stats.change >= 0 ? green : .red).font(.subheadline)
            Picker("Date range", selection: $range) { Text("1M").tag(30); Text("3M").tag(90); Text("1Y").tag(365) }.pickerStyle(.segmented)
            Chart(visiblePoints) { point in
                AreaMark(x: .value("Date", point.date), yStart: .value("Base", stats.low * 0.98), yEnd: .value("Price", point.close)).foregroundStyle(green.opacity(0.12))
                LineMark(x: .value("Date", point.date), y: .value("Price", point.close)).foregroundStyle(green).lineStyle(StrokeStyle(lineWidth: 2))
            }.chartYScale(domain: max(0, stats.low * 0.98)...max(stats.high * 1.02, stats.low + 1)).frame(height: 220).accessibilityLabel("Daily closing prices in \(stock.currency)")
            HStack { metric("Period high", currency(stats.high, code: stock.currency)); Spacer(); metric("Daily volatility", String(format: "%.2f%%", stats.volatility)) }
            if let date = stock.points.last?.date { Text("Last daily observation: \(date.formatted(date: .abbreviated, time: .omitted))").font(.caption).foregroundStyle(.secondary) }
        }.padding(20).background(.background, in: RoundedRectangle(cornerRadius: 22))
        VStack(alignment: .leading, spacing: 16) {
            Label("Python ML forecasts", systemImage: "sparkles").font(.title3.bold())
            Text("Random Forest · Gradient Boosting · Ridge Regression").font(.caption).foregroundStyle(.secondary)
            Picker("Forecast horizon", selection: $horizon) { Text("7 sessions").tag(7); Text("14").tag(14); Text("30").tag(30) }.pickerStyle(.segmented)
            Button { Task { await store.predict(horizon: horizon, backend: backend) } } label: {
                HStack { if store.forecasting { ProgressView().tint(.white) }; Text(store.forecasting ? "Training models…" : "Compare forecasts"); Spacer(); Image(systemName: "arrow.up.right") }.padding(4)
            }.buttonStyle(.borderedProminent).disabled(store.forecasting || store.loading)
            if backend.isEmpty { Text("Connect your Python Render service in Settings. Market charts work without it.").font(.footnote).foregroundStyle(.secondary) }
            if let forecast = store.forecast {
                ForEach(forecast.models) { model in
                    VStack(alignment: .leading, spacing: 5) {
                        HStack { Text(model.name).bold(); Spacer(); Text(currency(model.price, code: forecast.currency)) }
                        Text("MAE \(currency(model.mae, code: forecast.currency)) · RMSE \(currency(model.rmse, code: forecast.currency))").font(.caption)
                        Text(model.beatsBaseline ? "Lower MAE than the baseline" : "Did not beat the no-change baseline").font(.caption).foregroundStyle(.secondary)
                    }.padding(.vertical, 5)
                }
                Text("Baseline MAE: \(currency(forecast.baseline.mae, code: forecast.currency)). \(forecast.evaluation.testSamples) test observations with a \(forecast.evaluation.gapSessions)-session gap.").font(.caption).foregroundStyle(.secondary)
            }
        }.padding(20).background(.background, in: RoundedRectangle(cornerRadius: 22))
    }
    private func metric(_ name: String, _ value: String) -> some View { VStack(alignment: .leading, spacing: 6) { Text(name).font(.caption).foregroundStyle(.secondary); Text(value).font(.subheadline.bold()) } }
    private func toggleFavorite(_ code: String) { var list = favorites; if list.contains(code) { list.removeAll { $0 == code } } else { list.append(code) }; favoriteList = list.joined(separator: ",") }
    private var settingsView: some View {
        NavigationStack { Form {
            Section("Python ML service") { TextField("https://your-service.onrender.com", text: $backend).textInputAutocapitalization(.never).autocorrectionDisabled().keyboardType(.URL); Text("Use the HTTPS URL of the Python version in your GitHub repository. This app does not train scikit-learn models on-device.").font(.caption) }
            Section("About") { Text("MarketLens v2 · Native SwiftUI + Swift Charts"); Text("Direct Yahoo Finance history. No account credentials or brokerage access.").font(.caption) }
        }.navigationTitle("Settings").toolbar { Button("Done") { settings = false; store.resetForecast() } } }
    }
}
