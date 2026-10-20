import Foundation
@main struct CoreChecks {
 static func main() {
  let values = [100.0,110.0,121.0].enumerated().map { PricePoint(time: Double($0.offset)*86400000, close:$0.element) }
  let stats = PriceStatistics(points: values)
  precondition(abs(stats.change-21) < 0.0001)
  precondition(stats.high==121 && stats.low==100)
  precondition(stats.volatility < 0.0001)
  print("MarketLens return, range, and volatility checks passed")
 }
}
