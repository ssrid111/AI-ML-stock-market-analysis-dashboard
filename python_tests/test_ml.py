import unittest
import numpy as np
from backend.ml import dataset, split_positions, features_at, evaluate_and_forecast
from backend.main import app, normalize
from fastapi.testclient import TestClient


def stock_fixture():
    points=[]
    for i in range(330):
        price=100*np.exp(.0005*i+.02*np.sin(i*.13))
        points.append({'time':(1700000000+i*86400)*1000,'close':float(price),
                       'adjustedClose':float(price),'volume':1000+i%20})
    return {'symbol':'TEST','currency':'USD','points':points}


class MLTests(unittest.TestCase):
    def test_features_do_not_read_the_future(self):
        stock=stock_fixture();prices=np.array([p['close'] for p in stock['points']]);volumes=np.ones(len(prices))
        before=features_at(prices,volumes,150)
        prices[151:]*=100;volumes[151:]*=100
        np.testing.assert_array_equal(before,features_at(prices,volumes,150))

    def test_targets_and_gap_for_all_horizons(self):
        for horizon in (7,14,30):
            prices,_,origins,_,y=dataset(stock_fixture()['points'],horizon)
            np.testing.assert_allclose(y,np.log(prices[origins+horizon]/prices[origins]))
            train,test=split_positions(origins,horizon)
            self.assertLess(origins[train[-1]]+horizon,origins[test[0]])

    def test_three_models_and_baseline_report_finite_results(self):
        result=evaluate_and_forecast(stock_fixture(),14)
        self.assertEqual(len(result['models']),3)
        self.assertGreater(result['baseline']['mae'],0)
        for model in result['models']:
            self.assertGreater(model['price'],0)
            self.assertTrue(np.isfinite(model['rmse']))
        self.assertLess(result['evaluation']['trainLastTargetDate'],result['evaluation']['testStartDate'])

    def test_short_history_is_rejected(self):
        stock=stock_fixture();stock['points']=stock['points'][:80]
        with self.assertRaisesRegex(ValueError,'160'):
            evaluate_and_forecast(stock,30)

    def test_adjusted_prices_are_used_for_training(self):
        stock=stock_fixture();stock['points'][100]['close']*=2
        prices,*_=dataset(stock['points'],7)
        self.assertEqual(prices[100],stock['points'][100]['adjustedClose'])

    def test_api_validation_and_frontend(self):
        with TestClient(app) as client:
            self.assertEqual(client.get('/health').json()['runtime'],'Python')
            self.assertEqual(client.get('/api/stock?symbol=https://evil.example').status_code,400)
            self.assertEqual(client.get('/api/predict?symbol=TSLA&horizon=99').status_code,400)
            self.assertEqual(client.get('/').status_code,200)
            self.assertEqual(client.get('/no-such-file').status_code,404)

    def test_prediction_api_preserves_currency_and_reuses_cached_evaluation(self):
        from unittest.mock import AsyncMock, patch
        from backend.main import prediction_cache
        stock=stock_fixture();stock['symbol']='TESTINR';stock['currency']='INR'
        entry={'fetchedAt':'fixture','stock':stock}
        prediction_cache.clear()
        with patch('backend.main.get_stock',new=AsyncMock(return_value=entry)):
            with TestClient(app) as client:
                first=client.get('/api/predict?symbol=TESTINR&horizon=7')
                self.assertEqual(first.status_code,200)
                self.assertEqual(first.json()['currency'],'INR')
                second=client.get('/api/predict?symbol=TESTINR&horizon=7')
                self.assertEqual(first.json()['trainedAt'],second.json()['trainedAt'])
        prediction_cache.clear()

    def test_normalization_drops_missing_prices(self):
        result={'meta':{'symbol':'TEST','currency':'INR'},'timestamp':list(range(35)),
                'indicators':{'quote':[{'close':[None]+[100.]*34,'volume':[10]*35}],
                              'adjclose':[{'adjclose':[50.]*35}]}}
        normalized=normalize(result)
        self.assertEqual(len(normalized['points']),34)
        self.assertEqual(normalized['points'][0]['adjustedClose'],50)
        self.assertEqual(normalized['currency'],'INR')

if __name__=='__main__':
    unittest.main()
