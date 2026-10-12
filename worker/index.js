const SYMBOLS = ['AAPL','MSFT','NVDA','GOOGL','AMZN','^GSPC','^IXIC','^DJI','^VIX'];
let snapshot = null;
let inFlight = null;
const json = (value,status=200) => new Response(JSON.stringify(value), {status,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store'}});
export function normalize(result) {
  const quote = result.indicators?.quote?.[0];
  const points = (result.timestamp || []).map((time,i)=>({time:time*1000,close:quote?.close?.[i],volume:quote?.volume?.[i]??null})).filter(p=>Number.isFinite(p.close)&&p.close>0);
  if(points.length < 30) throw new Error('Insufficient price history');
  const meta=result.meta || {};
  return {symbol:meta.symbol,currency:meta.currency || 'USD',exchange:meta.exchangeName || '',points,marketTime:meta.regularMarketTime?meta.regularMarketTime*1000:null,price:meta.regularMarketPrice??points.at(-1).close,previousClose:meta.previousClose??meta.regularMarketPreviousClose??points.at(-2).close};
}
async function getHistory(symbol) {
  const url = new URL('https://query1.finance.yahoo.com/v8/finance/chart/'+encodeURIComponent(symbol));
  url.searchParams.set('range','1y');url.searchParams.set('interval','1d');
  const response = await fetch(url,{headers:{'User-Agent':'MarketLens/1.0 (personal educational dashboard)','Accept':'application/json'},signal:AbortSignal.timeout(15000)});
  if(!response.ok) throw new Error(response.status===429?'Yahoo Finance is rate-limiting requests. Try again in a few minutes.':'Yahoo Finance is unavailable. Please try again later.');
  const body=await response.json();
  if(body.chart?.error || !body.chart?.result?.[0]) throw new Error('Yahoo Finance did not return valid market data.');
  return normalize(body.chart.result[0]);
}
async function loadMarket(){
  const results={};let next=0;
  await Promise.all(Array.from({length:3},async()=>{while(next<SYMBOLS.length){const symbol=SYMBOLS[next++];try{results[symbol]=await getHistory(symbol)}catch(e){results[symbol]={error:e.message || 'Data unavailable'}}}}));
  if(SYMBOLS.every(s=>results[s].error)) throw new Error(results.AAPL.error);
  return {source:'Yahoo Finance',fetchedAt:new Date().toISOString(),symbols:results};
}
export default {
  async fetch(request,env,ctx){
    const url=new URL(request.url);
    if(request.method!=='GET') return json({error:'Method not allowed'},405);
    if(url.pathname==='/api/market'){
      try{
        if(snapshot && Date.now()-snapshot.time<300000) return json(snapshot.data);
        if(!inFlight) inFlight=loadMarket().then(data=>{snapshot={time:Date.now(),data};return data}).finally(()=>{inFlight=null});
        return json(await inFlight);
      }catch(e){return json({error:e.message || 'Unable to retrieve market data'},503)}
    }
    const path=url.pathname==='/'?'/index.html':url.pathname;
    const asset=ASSETS[path];
    return asset?new Response(asset.body,{headers:{'Content-Type':asset.type,'Cache-Control':'no-cache'}}):new Response('Not found',{status:404});
  }
};
