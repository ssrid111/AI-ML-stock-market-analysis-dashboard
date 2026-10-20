import Foundation

struct PricePoint: Codable, Identifiable {
    let time: Double
    let close: Double
    var id: Double { time }
    var date: Date { Date(timeIntervalSince1970: time / 1000) }
}
struct Stock: Decodable {
    let symbol: String
    let name: String?
    let currency: String
    let price: Double
    let points: [PricePoint]
}
struct StockEnvelope: Decodable { let stock: Stock }
struct Forecast: Decodable {
    struct Model: Decodable, Identifiable {
        let id: String
        let name: String
        let price: Double
        let mae: Double
        let rmse: Double
        let beatsBaseline: Bool
    }
    struct Baseline: Decodable { let mae: Double; let rmse: Double }
    struct Evaluation: Decodable { let trainSamples: Int; let testSamples: Int; let gapSessions: Int }
    let models: [Model]
    let baseline: Baseline
    let evaluation: Evaluation
    let horizon: Int
    let currency: String
}
struct APIMessage: Decodable { let error: String }
enum AppError: LocalizedError {
    case message(String)
    var errorDescription: String? { if case .message(let text) = self { return text }; return nil }
}
struct YahooEnvelope: Decodable {
    struct Chart: Decodable { let result: [Result]? }
    struct Result: Decodable {
        struct Meta: Decodable { let symbol: String; let currency: String?; let longName: String?; let shortName: String?; let regularMarketPrice: Double? }
        struct Indicators: Decodable {
            struct Quote: Decodable { let close: [Double?] }
            let quote: [Quote]
        }
        let meta: Meta
        let timestamp: [Double]?
        let indicators: Indicators
    }
    let chart: Chart
}
struct StockService {
    func stock(_ symbol: String) async throws -> Stock {
        guard symbol.range(of: "^[A-Z0-9^][A-Z0-9.^=\\-]{0,24}$", options: .regularExpression) != nil else {
            throw AppError.message("Enter a Yahoo ticker, such as TSLA or RELIANCE.NS.")
        }
        var url = URLComponents(string: "https://query1.finance.yahoo.com/v8/finance/chart/\(symbol)")!
        url.queryItems = [URLQueryItem(name: "range", value: "1y"), URLQueryItem(name: "interval", value: "1d")]
        var request = URLRequest(url: url.url!)
        request.timeoutInterval = 25
        request.setValue("MarketLens/2.0 (personal educational dashboard)", forHTTPHeaderField: "User-Agent")
        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw AppError.message("Yahoo couldn't load that ticker. Check the symbol or try again later.")
        }
        let body = try JSONDecoder().decode(YahooEnvelope.self, from: data)
        guard let result = body.chart.result?.first, let times = result.timestamp,
              let closes = result.indicators.quote.first?.close else { throw AppError.message("No price history returned.") }
        let points = zip(times, closes).compactMap { time, close -> PricePoint? in
            guard let close, close.isFinite, close > 0 else { return nil }
            return PricePoint(time: time * 1000, close: close)
        }
        guard points.count > 1 else { throw AppError.message("This ticker has too little price history.") }
        return Stock(symbol: result.meta.symbol, name: result.meta.longName ?? result.meta.shortName,
                     currency: result.meta.currency ?? "USD", price: result.meta.regularMarketPrice ?? points.last!.close, points: points)
    }
    func forecast(symbol: String, horizon: Int, backend: String) async throws -> Forecast {
        guard var components = URLComponents(string: backend.trimmingCharacters(in: .whitespacesAndNewlines)),
              components.scheme == "https", components.host != nil else {
            throw AppError.message("Add your deployed Python service's HTTPS URL in Settings to use ML forecasts.")
        }
        components.path = "/api/predict"
        components.queryItems = [URLQueryItem(name: "symbol", value: symbol), URLQueryItem(name: "horizon", value: String(horizon))]
        var request = URLRequest(url: components.url!)
        request.timeoutInterval = 90
        let (data, response) = try await URLSession.shared.data(for: request)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            let message = (try? JSONDecoder().decode(APIMessage.self, from: data).error) ?? "The Python service didn't return a forecast. Check its URL or retry after it wakes up."
            throw AppError.message(message)
        }
        return try JSONDecoder().decode(Forecast.self, from: data)
    }
}
struct PriceStatistics {
    let change: Double
    let high: Double
    let low: Double
    let volatility: Double
    init(points: [PricePoint]) {
        let prices = points.map(\.close)
        high = prices.max() ?? 0; low = prices.min() ?? 0
        change = prices.count > 1 ? (prices.last! / prices.first! - 1) * 100 : 0
        let returns = zip(prices.dropFirst(), prices).map { $0 / $1 - 1 }
        let mean = returns.isEmpty ? 0 : returns.reduce(0, +) / Double(returns.count)
        volatility = returns.isEmpty ? 0 : sqrt(returns.map { pow($0 - mean, 2) }.reduce(0, +) / Double(returns.count)) * 100
    }
}
