"""FastAPI application: Yahoo data, scikit-learn forecasts, and the dashboard."""
import asyncio
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
import re
import time

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from .ml import evaluate_and_forecast

app = FastAPI(title='MarketLens Python ML API')
PUBLIC = Path(__file__).resolve().parents[1] / 'public'
SYMBOLS = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', '^GSPC', '^IXIC', '^DJI', '^VIX']
stock_cache = OrderedDict()
prediction_cache = OrderedDict()
pending_stocks = {}
fetch_slots = asyncio.Semaphore(3)
training_slot = asyncio.Semaphore(1)
TTL = 300


def symbol_input(raw):
    symbol = raw.strip().upper()
    if not re.fullmatch(r'[A-Z0-9^][A-Z0-9.^=\-]{0,24}', symbol):
        raise HTTPException(400, 'Enter a Yahoo Finance ticker, such as TSLA or RELIANCE.NS.')
    return symbol


def now():
    return datetime.now(timezone.utc).isoformat()


def normalize(result):
    import math
    meta = result.get('meta', {})
    indicators = result.get('indicators', {})
    quote = indicators.get('quote', [{}])[0]
    adjusted = indicators.get('adjclose', [{}])[0].get('adjclose', [])
    points = []
    for i, timestamp in enumerate(result.get('timestamp', [])):
        close = quote.get('close', [])[i] if i < len(quote.get('close', [])) else None
        if not isinstance(close, (int, float)) or not math.isfinite(close) or close <= 0:
            continue
        adj = adjusted[i] if i < len(adjusted) else close
        if not isinstance(adj, (int, float)) or not math.isfinite(adj) or adj <= 0:
            adj = close
        volume = quote.get('volume', [])[i] if i < len(quote.get('volume', [])) else 0
        if not isinstance(volume, (int, float)) or not math.isfinite(volume) or volume < 0:
            volume = 0
        points.append({'time': timestamp*1000, 'close': close, 'adjustedClose': adj, 'volume': volume})
    if len(points) < 30:
        raise HTTPException(422, 'This stock has too little daily price history.')
    return {'symbol': meta.get('symbol'), 'name': meta.get('longName') or meta.get('shortName') or meta.get('symbol'),
            'currency': meta.get('currency', 'USD'), 'exchange': meta.get('exchangeName', ''),
            'points': points, 'price': meta.get('regularMarketPrice') or points[-1]['close'],
            'previousClose': meta.get('previousClose') or meta.get('regularMarketPreviousClose') or points[-2]['close'],
            'marketTime': meta.get('regularMarketTime', 0)*1000}


async def fetch_yahoo(symbol):
    async with fetch_slots:
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.get('https://query1.finance.yahoo.com/v8/finance/chart/'+symbol,
                                            params={'range': '2y', 'interval': '1d'},
                                            headers={'User-Agent': 'MarketLens/1.0 (personal educational dashboard)'})
            if response.status_code == 404:
                raise HTTPException(404, 'Stock symbol not found. Check the ticker and exchange suffix.')
            if response.status_code == 429:
                raise HTTPException(503, 'Yahoo Finance is rate-limiting requests. Try again later.')
            if response.status_code != 200:
                raise HTTPException(503, 'Yahoo Finance is currently unavailable.')
            body = response.json().get('chart', {})
            if body.get('error') or not body.get('result'):
                raise HTTPException(404, 'Yahoo Finance did not return this stock.')
            stock = normalize(body['result'][0])
        except (httpx.HTTPError, ValueError, KeyError, IndexError) as exc:
            raise HTTPException(503, 'Unable to retrieve valid Yahoo Finance data. Please retry.') from exc
    entry = {'time': time.monotonic(), 'fetchedAt': now(), 'stock': stock}
    if len(stock_cache) >= 100:
        stock_cache.popitem(last=False)
    stock_cache[symbol] = entry
    return entry


async def get_stock(symbol):
    entry = stock_cache.get(symbol)
    if entry and time.monotonic()-entry['time'] < TTL:
        return entry
    if symbol not in pending_stocks:
        pending_stocks[symbol] = asyncio.create_task(fetch_yahoo(symbol))
    task = pending_stocks[symbol]
    try:
        return await asyncio.shield(task)
    finally:
        if task.done():
            pending_stocks.pop(symbol, None)


@app.exception_handler(HTTPException)
async def api_error(request, exc):
    return JSONResponse({'error': exc.detail}, status_code=exc.status_code)


@app.get('/health')
def health():
    return {'status': 'ok', 'runtime': 'Python', 'ml': 'scikit-learn'}


@app.get('/api/stock')
async def stock_route(symbol: str = ''):
    entry = await get_stock(symbol_input(symbol))
    return {'source': 'Yahoo Finance', 'fetchedAt': entry['fetchedAt'], 'stock': entry['stock']}


@app.get('/api/market')
async def market_route():
    async def one(symbol):
        try:
            return symbol, (await get_stock(symbol))['stock']
        except HTTPException as exc:
            return symbol, {'error': exc.detail}
    symbols = dict(await asyncio.gather(*(one(s) for s in SYMBOLS)))
    if all('error' in value for value in symbols.values()):
        raise HTTPException(503, 'Yahoo Finance is currently unavailable. Please retry.')
    return {'source': 'Yahoo Finance', 'fetchedAt': now(), 'symbols': symbols}


@app.get('/api/predict')
async def predict_route(symbol: str = '', horizon: int = Query(7)):
    symbol = symbol_input(symbol)
    if horizon not in (7, 14, 30):
        raise HTTPException(400, 'Choose 7, 14, or 30 trading sessions.')
    entry = await get_stock(symbol)
    # A new Yahoo snapshot invalidates predictions for that symbol/horizon.
    key = (symbol, horizon, entry['fetchedAt'])
    async with training_slot:
        cached = prediction_cache.get(key)
        if cached:
            return cached
        try:
            result = await asyncio.to_thread(evaluate_and_forecast, entry['stock'], horizon)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        result['source'] = 'Yahoo Finance'
        result['trainedAt'] = now()
        if len(prediction_cache) >= 64:
            prediction_cache.popitem(last=False)
        prediction_cache[key] = result
        return result


@app.get('/')
def index():
    return FileResponse(PUBLIC / 'index.html')


@app.get('/{asset}')
def static_asset(asset: str):
    if asset not in ('index.html', 'style.css', 'app.js'):
        raise HTTPException(404, 'Not found')
    return FileResponse(PUBLIC / asset)
